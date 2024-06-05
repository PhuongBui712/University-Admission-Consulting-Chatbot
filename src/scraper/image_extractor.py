import os
import shutil
from time import sleep
from urllib.parse import urlparse
import requests
import uuid
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from src.prompts import IMAGE_EXTRACTOR_PROMPT


load_dotenv()


class InvalidAPIKey(Exception):
    message = 'Invalid API Key'

    def __init__(self):
        super().__init__(self.message)


class InvalidURL(Exception):
    message = 'Invalid URL'

    def __init__(self):
        super().__init__(self.message)


class GeminiImageExtractor:
    tmp_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..',  'data/tmp'))
    prompt = IMAGE_EXTRACTOR_PROMPT
    model_list = ['gemini-1.5-flash-latest',
                  'gemini-1.5-pro-latest']

    def __init__(self, model_name='gemini-1.5-pro-latest'):
        self.api = self._get_api()
        self.chat_model = ChatGoogleGenerativeAI(model=model_name, google_api_key=self.api)
        self.text_content = {
            "type": "text",
            "text": self.prompt
        }

    def extract(self, image_path, sleep_time=0):
        image_content = {
            "type": "image_url",
            "image_url": image_path
        }
        message = HumanMessage(content=[self.text_content, image_content])

        try:
            result = self.chat_model.invoke([message])
        except:
            image_content['image_url'] = self._tmp_save(image_path)
            message = HumanMessage(content=[self.text_content, image_content])
            result = self.chat_model.invoke([message])
            os.remove(image_content['image_url'])

        sleep(sleep_time)
        return result.content

    def _tmp_save(self, url):
        # request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if not response.ok:
            response.raise_for_status()

        # parse image_extension
        parsed_url = urlparse(url)
        filename, file_extension = os.path.splitext(parsed_url.path)

        # get saving path
        filename = f'{uuid.uuid4()}{file_extension}'
        file_path = os.path.join(self.tmp_directory, filename)

        # save
        self._create_tmp_dir()
        with open(file_path, 'wb') as file:
            file.write(response.content)

        return file_path

    def _create_tmp_dir(self):
        os.makedirs(self.tmp_directory, exist_ok=True)

    # @staticmethod
    def _get_api(self):
        key = os.getenv('GOOGLE_API_KEY')
        if not key:
            raise InvalidAPIKey

        return key

    def __del__(self):
        if os.path.isdir(self.tmp_directory):
            shutil.rmtree(self.tmp_directory)