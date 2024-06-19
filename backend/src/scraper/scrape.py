# TODO: parse html table
import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__))) # add scraper dir to path (to import module from same dir)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) # add backend dir to path (to import module in src)

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from hashlib import sha256
from urllib.parse import urlparse, quote

from src.image_extractor import GeminiImageExtractor
from src.utils import load_json, write_json
from utils import *


# helper functions
def get_web_soup(url):
    response = requests.get(url, headers=REQUEST_HEADER)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    return None


def preprocess_soup(soup):
    # get the main content
    main_content = soup.find('section', {'id': 'sp-main-body'})

    # decompose navigate elements (next or previous page navigators)
    navigator_element = main_content.find('ul', {'class': 'pager pagenav'})
    if navigator_element:
        navigator_element.decompose()

    # decompose hit numbers
    for element in soup.find_all('span', {'class': 'mod-articles-category-hits'}):
        element.decompose()

    return main_content


def website_is_updated(url, hash_value):
    soup = get_web_soup(url)
    if soup:
        main_soup = preprocess_soup(soup)
        return sha256(main_soup.encode()).hexdigest() != hash_value

    raise Exception('Can not connect to destination URL')


def encode_url(url):
    if is_subdirectory(url):
        raise InvalidURL

    parsed_url = urlparse(url)
    subdirectory = parsed_url.path
    encoded_subdirectory = quote(subdirectory)
    encoded_url = f'{parsed_url.scheme}://{parsed_url.netloc}{encoded_subdirectory}'

    return encoded_url


def get_title(soup):
    title = soup.find('meta', {'property': 'og:title'}).get('content') or soup.title.get_text()

    return title


def get_links(soup, internal_link=True, external_link=False, attachment=True, start_url=None):
    # get links
    links = set()
    for a in soup.find_all('a', href=True):
        if attachment and is_attachment_file(a['href']):
            links.add(a['href'])

        else:
            is_internal_link = is_subdirectory(a['href'])
            if is_internal_link and internal_link:
                links.add(encode_url(start_url + a['href']))
            elif not is_internal_link and external_link:
                links.add(encode_url(a['href']))

    return links


def get_images(url):
    response = requests.get(url, headers=REQUEST_HEADER)
    if not response.ok:
        response.raise_for_status()

    return response.content


def is_table(table_soup):
    caption = table_soup.find('caption')
    if caption is None or not caption.get_text().startswith('Attachments'):
        return True
    return False

def get_table(soup):
    table_elements = []
    for table in soup.find_all('table'):
        if is_table(table):
            table_elements.append(str(table))
            table.decompose()

    return table_elements


def parse_website_image(soup, extractor, start_url=None):
    not_parsed_imgs = []
    for img in soup.find_all('img', src=True):
        if img['src'].split('.')[-1] == 'gif':
            continue

        url = img['src']
        if is_subdirectory(url):
            try:
                url = start_url + url
            except:
                raise Exception("Can not access incomplete URL")

        parse_content = extractor.invoke(url)
        if not parse_content.startswith('others'):
            img.insert_after(parse_content)
        else:
            not_parsed_imgs.append(url)

    return soup, not_parsed_imgs


def parse_website_url(soup, start_url):
    for a in soup.find_all('a', href=True):
        if a.string and a.string.strip() != a['href']:
            original_url = start_url + a['href'] if is_subdirectory(a['href']) else a['href']
            a.string += f' ({original_url})'

    return soup


def parse_website(soup, parse_reference=True, parse_image=False, start_url=None):
    # kill all script and style elements
    for script in soup(['script', 'style']):
        script.invoke()

    # parse image
    imgs = []
    if parse_image:
        image_extractor = GeminiImageExtractor()
        soup, imgs = parse_website_image(soup, image_extractor, start_url=start_url)

    # parse references
    if parse_reference:
        soup = parse_website_url(soup, start_url)

    tables = get_table(soup)

    # parse content
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text, tables, imgs


# crawl functions
def crawl_webpage(url, parse_reference=True, parse_image=False, hash=False):
    reference_urls = set()
    page_content = None
    hash_value = None

    soup = get_web_soup(url)
    if soup:
        title = get_title(soup)
        main_soup = preprocess_soup(soup)

        # hash
        if hash:
            hash_value = sha256(main_soup.encode()).hexdigest()

        # extract start url
        parsed_url = urlparse(url)
        start_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # get references
        reference_urls.update(get_links(main_soup,
                                              internal_link=True,
                                              external_link=False,
                                              attachment=True,
                                              start_url=start_url))

        # parse content
        text, tables, images = parse_website(main_soup, parse_reference, parse_image, start_url)

        ret = title, text, tables, images, reference_urls
        if hash:
            ret += (hash_value,)

        return ret
    return None


def crawl():
    # read crawled file
    sitemap_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/sitemap.json'))
    storage_urls = load_json(sitemap_path)

    # used variables
    start_url = 'https://tuyensinh.hcmus.edu.vn'
    news_url = 'https://tuyensinh.hcmus.edu.vn/th%C3%B4ng-tin-tuy%E1%BB%83n-sinh-%C4%91%E1%BA%A1i-h%E1%BB%8Dc'
    need2crawl_url = set(storage_urls['base_url']).difference(news_url)
    crawled_url = set()
    text_list = []
    table_list = []
    image_path_list = []

    # crawl
    soup = get_web_soup(news_url)
    if soup:
        main_soup = preprocess_soup(soup)

        # check latest article
        latest_article_tag = main_soup.find('li')
        latest_article_url = latest_article_tag.find('a')['href']
        latest_article_url = start_url + latest_article_url if is_subdirectory(latest_article_url) else latest_article_url


        if latest_article_url not in storage_urls['article_url']:
            latest_article_release_date = latest_article_tag.find('span', class_="mod-articles-category-date").text.strip()
            random_crawled_url = None
            valid_year = datetime.now().year

            if storage_urls['article_url']:
                random_crawled_url = list(storage_urls['article_url'].items())[0]

            # case 2: article is of new year
            if random_crawled_url and random_crawled_url[1]['release_date'][-4:] == latest_article_release_date[-4:]:
                # delete old crawled article
                valid_year = random_crawled_url[1]['release_date'][-4:]

            # case 3: update of this year
            else:
                storage_urls['article_url'].clear()

            # get new articles
            new_article_urls = set()
            for tag in main_soup.find_all('li'):
                release_date = tag.find('span', class_="mod-articles-category-date").text.strip()
                url = tag.find('a', class_="mod-articles-category-title")['href']
                if url and is_subdirectory(url):
                    url = start_url + url
                if url not in storage_urls['article_url'] and int(release_date[-4:]) == valid_year:
                    new_article_urls.add((encode_url(url), release_date))

            need2crawl_url.update(new_article_urls)

            # crawl new article
            for url, release_date in new_article_urls:
                crawled_url.add(url)

                title, text, tables, image_paths, references, hash_value = crawl_webpage(url, parse_reference=True, parse_image=True, hash=True)
                storage_urls['article_url'][url] = {
                    'release_date': release_date,
                    'hash_value': hash_value,
                }
                text_list.append(webpage_to_documents(url=url, title=title, text=text))
                table_list += tables
                image_path_list += image_paths
                need2crawl_url.update(references)

        # crawl base url
        for url in storage_urls['base_url'].keys():
            hash_value = storage_urls['base_url'][url].get('hash_value')
            if website_is_updated(url, hash_value):
                title, text, tables, image_paths, references, hash_value = crawl_webpage(url, parse_reference=True, parse_image=True, hash=True)
                storage_urls['base_url'][url] = {
                    'hash_value': hash_value,
                }

                text_list.append(webpage_to_documents(url=url, title=title, text=text))
                table_list += tables
                image_path_list += image_paths
                need2crawl_url.update(references)

        crawled_url.update(storage_urls['base_url'].keys())

        # check if complete all references
        # TODO: Handle remaining URLs
        need2crawl_url = need2crawl_url.difference(crawled_url)

        # update sitemap file
        write_json(sitemap_path, storage_urls)

        return text_list, table_list, image_path_list