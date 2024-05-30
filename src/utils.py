import yaml
import json
import torch
from langchain_core.documents import Document


def load_config():
    with open("./config.yaml", 'r') as stream:
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


def get_device():
    device = 'cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu')

    return device