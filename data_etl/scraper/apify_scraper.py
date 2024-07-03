# This is the first crawling strategy of the chatbot and no longer developed


from langchain_community.utilities import ApifyWrapper
from langchain_community.document_loaders import ApifyDatasetLoader
from langchain_community.docstore.document import Document

import os
from typing import Dict, Any
from dotenv import load_dotenv
import yaml

load_dotenv()


class Scraper:
    def __init__(self, config: Dict[str, Any] = None):
        self._configurate_(config)

        if os.getenv('APIFY_DATASET_ID') is None:
            apify = ApifyWrapper()
            self.loader = apify.call_actor(
                actor_id="apify/website-content-crawler",
                run_input={
                    "startUrls": self.config['startUrls'],
                    "maxCrawlDepth": self.config['maxCrawlDepth'],
                    "dynamicContentWaitSecs": self.config['dynamicContentWaitSecs'],
                    "saveFiles": self.config['saveFiles']
                },
                dataset_mapping_function=lambda item: Document(
                    page_content=item["text"] or "", metadata={"source": item["url"]}
                ),
            )

            self.first_crawl = True

        else:
            self.loader = ApifyDatasetLoader(
                dataset_id=os.getenv('APIFY_DATASET_ID'),
                dataset_mapping_function=lambda dataset_item: Document(
                    page_content=dataset_item["text"] or "", metadata={"source": dataset_item["url"]}
                ),
            )

            self.first_crawl = False

    def scrape(self):
        docs = self.loader.load()

        if self.first_crawl:
            self.__save_config__()

        raw_text_docs = [doc for doc in docs if doc.page_content]
        return raw_text_docs

    def _configurate_(self, config: Dict[str, Any] = None):
        if config:
            self.config = config

            self.config = {
                'startUrls': config['url'] if config.get('url') else [{"url": "https://tuyensinh.hcmus.edu.vn/"}],
                'maxCrawlDepth': config['maxCrawlDepth'] if config.get('maxCrawlDepth') else 5,
                'dynamicContentWaitSecs': config['dynamicContentWaitSecs'] if config.get('dynamicContentWaitSecs') else 20,
                'saveFiles': True
            }

        else:
            self.config = {
                'startUrls': [{"url": "https://tuyensinh.hcmus.edu.vn/"}],
                'maxCrawlDepth': 5,
                'dynamicContentWaitSecs': 20,
                'saveFiles': True
            }

    def __save_config__(self):
        self.config['dataset_id'] = self.loader.dataset_id
        with open('../config.yaml', 'a') as file:
            yaml.dump(self.config, file)