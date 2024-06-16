# TODO: parse html table
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from datetime import datetime
from hashlib import sha256
from urllib.parse import urlparse

import utils
from src.utils import load_json, write_json


def crawl_webpage(url, parse_reference=True, parse_image=False, hash=False):
    reference_urls = set()
    page_content = None
    hash_value = None

    soup = utils.get_web_soup(url)
    if soup:
        main_soup = utils.preprocess_website(soup)

        # hash
        if hash:
            hash_value = sha256(main_soup.encode()).hexdigest()

        # extract start url
        parsed_url = urlparse(url)
        start_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # get references
        reference_urls.update(utils.get_links(main_soup,
                                              internal_link=True,
                                              external_link=False,
                                              attachment=True,
                                              start_url=start_url))

        # parse content
        main_content, images = utils.parse_website(main_soup, parse_reference, parse_image, start_url)
        page_content = (main_content, utils.get_title(soup))

        return page_content, images, reference_urls, hash_value
    
    return None


def crawl():
    # read crawled file
    sitemap_path = os.path.join(os.path.dirname(__file__), 'sitemap.json')
    storage_urls = load_json(sitemap_path)

    # used variables
    start_url = 'https://tuyensinh.hcmus.edu.vn'
    news_url = 'https://tuyensinh.hcmus.edu.vn/th%C3%B4ng-tin-tuy%E1%BB%83n-sinh-%C4%91%E1%BA%A1i-h%E1%BB%8Dc'
    need2crawl_url = set(storage_urls['base_url']).difference(news_url)
    crawled_url = set()
    documents = []

    # crawl
    soup = utils.get_web_soup(news_url)
    if soup:
        main_soup = utils.preprocess_website(soup)

        # check latest article
        latest_article_tag = main_soup.find('li')
        latest_article_url = latest_article_tag.find('a')['href']

        if latest_article_url not in storage_urls['article_url']:
            latest_article_release_date = latest_article_tag.find('span', class_="mod-articles-category-date").text.strip()
            random_crawled_url = None
            valid_year = datetime.now().year

            if storage_urls['article_url']:
                random_crawled_url = list(storage_urls['article_url'])[0]

            # case 2: article is of new year
            if random_crawled_url and random_crawled_url['release_date'][-4:] == latest_article_release_date[-4:]:
                # delete old crawled article
                valid_year = random_crawled_url['release_date'][-4:]

            # case 3: update of this year
            else:
                storage_urls['article_url'].clear()

            # get new articles
            new_article_urls = set()
            for tag in main_soup.find_all('li'):
                release_date = tag.find('span', class_="mod-articles-category-date").text.strip()
                url = tag.find('a', class_="mod-articles-category-title")['href']
                if url and utils.is_subdirectory(url):
                    url = start_url + url
                if url not in storage_urls['article_url'] and int(release_date[-4:]) == valid_year:
                    new_article_urls.add((utils.encode_url(url), release_date))

            need2crawl_url.update(new_article_urls)

            # crawl new article
            for url, release_date in new_article_urls:
                crawled_url.add(url)

                page_content, references, hash_value = crawl_webpage(url, hash=True, parse_image=True)
                storage_urls['article_url'][url] = {
                    'release_date': release_date,
                    'hash_value': hash_value,  # TODO: whether article need to be hashed?
                }
                documents.append(utils.webpage_to_documents(url, page_content[0], page_content[1]))
                need2crawl_url.update(references)

        # crawl base url
        for url in storage_urls['base_url'].keys():
            hash_value = storage_urls['base_url'][url].get('hash_value')
            if utils.website_is_updated(url, hash_value):
                page_content, references, hash_value = crawl_webpage(url, hash=True, parse_image=True)
                storage_urls['base_url'][url] = {
                    'hash_value': hash_value,
                }

                need2crawl_url.update(references)
                documents.append(utils.webpage_to_documents(url, page_content[0], page_content[1]))

        crawled_url.update(storage_urls['base_url'].keys())

        # check if complete all references
        # TODO: Handle remaining URLs
        need2crawl_url = need2crawl_url.difference(crawled_url)

        # update sitemap file
        write_json(sitemap_path, storage_urls)

        return documents