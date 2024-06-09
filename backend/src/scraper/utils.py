import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote
from hashlib import sha256
from langchain_core.documents import Document

from image_extractor import GeminiImageExtractor, InvalidURL

# List of common attachment file extensions
ATTACHMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar',
                         '.7z', '.png', '.jpg', '.jpeg', '.gif', '.txt', '.ppt', '.pptx'}


def is_subdirectory(href):
    parsed = urlparse(href)
    # Check if the scheme and netloc are present
    return not (bool(parsed.scheme) and bool(parsed.netloc))


def is_attachment_file(href):
    _, ext = os.path.splitext(href)
    return ext.lower() in ATTACHMENT_EXTENSIONS


def preprocess_website(soup):
    # get the main content
    main_content = soup.find('section', {'id': 'sp-main-body'})

    # decompose navigate elements (next or previous page navigators)
    navigator_element = main_content.find('ul', {'class': 'pager pagenav'})
    if navigator_element:
        navigator_element.decompose()

    return main_content


def get_web_soup(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    return None


def encode_url(url):
    if is_subdirectory(url):
        raise InvalidURL

    parsed_url = urlparse(url)
    subdirectory = parsed_url.path
    encoded_subdirectory = quote(subdirectory)
    encoded_url = f'{parsed_url.scheme}://{parsed_url.netloc}{encoded_subdirectory}'

    return encoded_url


def website_is_updated(url, hash_value):
    soup = get_web_soup(url)
    if soup:
        main_soup = preprocess_website(soup)
        return sha256(main_soup.encode()).hexdigest() != hash_value

    raise Exception('Can not connect to destination URL')


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


def parse_website_image(soup, extractor, start_url=None):
    for img in soup.find_all('img', src=True):
        url = img['src']
        if is_subdirectory(url):
            try:
                url = start_url + url
            except:
                raise InvalidURL

        parse_content = extractor.extract(url, sleep_time=1)
        if not parse_content.startswith('nothing'):
            img.insert_after(parse_content)

    return soup


def parse_website_url(soup, start_url):
    for a in soup.find_all('a', href=True):
        if a.string and a.string.strip() != a['href']:
            original_url = start_url + a['href'] if is_subdirectory(a['href']) else a['href']
            a.string += f' ({original_url})'

    return soup


def parse_website(soup, parse_reference=True, parse_image=False, start_url=None):
    # kill all script and style elements
    for script in soup(['script', 'style']):
        script.extract()

    # parse image
    if parse_image:
        image_extractor = GeminiImageExtractor(model_name='gemini-1.5-flash-latest')
        soup = parse_website_image(soup, image_extractor, start_url=start_url)

    # parse references
    if parse_reference:
        soup = parse_website_url(soup, start_url)

    # parse content
    content = soup.get_text()
    lines = (line.strip() for line in content.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


def webpage_to_documents(url, page_content, title):
    return Document(
        page_content=page_content,
        metadata={
            'source': url,
            'title': title
        }
    )
