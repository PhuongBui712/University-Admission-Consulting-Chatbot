import yaml
import json
import re
import base64
from langchain_core.documents import Document


def load_config():
    with open("config.yaml", 'r') as stream:
        config = yaml.safe_load(stream)

    return config


def json_to_documents(path):
    with open(path, 'r', encoding='utf-8') as f:
        json_docs = json.load(f)
    
    docs = [Document(
        page_content=json_doc['page_content'],
        metadata=json_doc['metadata']
    ) for json_doc in json_docs]
    
    return docs


def write_json(path, items, ensure_ascii=False):
    with open(path, 'w') as file:
        json.dump(items, file, ensure_ascii=ensure_ascii, indent=4)


def load_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        result = json.load(file)

    return result


def looks_like_base64(sb):
    return re.match("^[A-Za-z0-9+/]+[=]{0,2}$", sb) is not None


def get_image_type(b64data):
    """
    Check if the base64 data is an image by looking at the start of the data
    """
    image_signatures = {
        b"\xFF\xD8\xFF": "jpg",
        b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A": "png",
        b"\x47\x49\x46\x38": "gif",
        b"\x52\x49\x46\x46": "webp",
    }
    try:
        header = base64.b64decode(b64data)[:8]  # Decode and get the first 8 bytes
        for sig, format in image_signatures.items():
            if header.startswith(sig):
                return format
        return None
    except Exception:
        raise Exception('Can not decode data')