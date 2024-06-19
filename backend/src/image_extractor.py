import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__))) # append src dir to path

import base64
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
from typing import List
from langchain_core.messages import HumanMessage

from prompts import IMAGE_EXTRACTOR_PROMPT
from scraper.utils import REQUEST_HEADER
from gemini_config import GeminiConfig


load_dotenv()


class GeminiImageExtractor(GeminiConfig):
    prompt = IMAGE_EXTRACTOR_PROMPT
    model = 'gemini-1.5-flash-latest'

    def __init__(self, custom_prompt=None):
        super().__init__('chat')  # Initialize the parent class with 'chat' model type
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
            base64_img = f'data:image/{path.split('.')[-1]};base64,{self._encode_image(self._get_image(image_path))}'
            image_content['image_url'] = {'url': base64_img}
        else:
            image_content['image_url'] = image_path

        message = HumanMessage(content=[self.text_content, image_content])

        self._increment_counter(1)
        result = self.model.invoke([message])

        return result.content

    def _is_url(self, s):
        try:
            result = urlparse(s)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _get_image(self, url):
        response = requests.get(url, headers=REQUEST_HEADER)
        if not response.ok:
            response.raise_for_status()

        return response.content

    def _encode_image(self, image: bytes):
        return base64.b64encode(image).decode('utf-8')