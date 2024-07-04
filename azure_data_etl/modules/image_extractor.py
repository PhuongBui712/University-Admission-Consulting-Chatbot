import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import re
import base64
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage

from prompts import IMAGE_EXTRACTOR_PROMPT
from scraper.utils import REQUEST_HEADER
from gemini_config import GeminiConfig
from modules.utils import looks_like_base64


load_dotenv()


def get_image(image_path):
    response = requests.get(image_path, headers=REQUEST_HEADER)
    if not response.ok:
        response.raise_for_status()

    return response.content


def encode_image(image: bytes):
    return base64.b64encode(image).decode('utf-8')


class GeminiImageExtractor(GeminiConfig):
    prompt = IMAGE_EXTRACTOR_PROMPT
    model = 'gemini-1.5-flash-latest'

    def __init__(self, custom_prompt=None, **kwargs):
        super().__init__('chat', **(kwargs or {'temperature': 0.0, 'top_p': 0.1, 'top_k': 1}))  # Initialize the parent class with 'chat' model type
        self.prompt = custom_prompt or self.prompt
        self.text_content = {
            "type": "text",
            "text": self.prompt
        }

    def invoke(self, image_path: str):
        image_content = {'type': 'image_url'}
        if self._is_url(image_path):
            parsed_url = urlparse(image_path)
            path = parsed_url.path
            base64_img = f"data:image/{path.split('.')[-1]};base64,{encode_image(get_image(image_path))}"
            image_content['image_url'] = {'url': base64_img}
        else:
            image_content['image_url'] = image_path

        message = HumanMessage(content=[self.text_content, image_content])

        self._increment_counter(1)
        result = self.model.invoke([message])

        return result.content
    
    # def batch(self,):
        # TODO: Develop batch method
        # pass

    def _is_url(self, s):
        try:
            result = urlparse(s)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
        
    def _is_base64_image(image: str):
        return looks_like_base64(image)
        