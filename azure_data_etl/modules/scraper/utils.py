import os
from urllib.parse import urlparse
from langchain_core.documents import Document


# List of common attachment file extensions
ATTACHMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar',
                         '.7z', '.png', '.jpg', '.jpeg', '.gif', '.txt', '.ppt', '.pptx'}

REQUEST_HEADER = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }


class InvalidAPIKey(Exception):
    message = 'Invalid API Key'

    def __init__(self):
        super().__init__(self.message)


class InvalidURL(Exception):
    message = 'Invalid URL'

    def __init__(self):
        super().__init__(self.message)


def is_subdirectory(href):
    parsed = urlparse(href)
    # Check if the scheme and netloc are present
    return not (bool(parsed.scheme) and bool(parsed.netloc))


def is_attachment_file(href):
    _, ext = os.path.splitext(href)
    return ext.lower() in ATTACHMENT_EXTENSIONS


def webpage_to_documents(url, title, text):
    return Document(
        page_content=text,
        metadata={
            'source': url,
            'title': title
        }
    )
