import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from langchain.retrievers import ContextualCompressionRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage

from prompts import ADMISSION_CONSULTANT_PROMPT
from utils import get_image_type

from typing import List


class RAG_Chain:
    def __init__(self,
                 chat_model,
                 vectorstore,
                 reranker,
                 top_retrieved: int = 5):
        
        self.chat_model = chat_model
        self.retriever = ContextualCompressionRetriever(
            base_compressor=reranker, base_retriever=vectorstore.get_retriever(k=15)
        )

        self.top_retrieved = top_retrieved

    def get_chain(self):
        chain = (
            {
                'context': self.retriever | RunnableLambda(self.split_text_image_content),
                'question': RunnablePassthrough()
            }
            | RunnableLambda(self.create_prompt)
            | self.chat_model
            | StrOutputParser()
        )

        return chain


    def _split_text_image_content(self, retrieved_docs: List[Document]):
        texts = []
        b64_images = []
        for i, doc in enumerate(retrieved_docs):
            if doc.metadata.get('type') == 'image':
                b64_images.append(doc.page_content)
            elif i < self.top_retrieved:
                texts.append(doc.page_content)

        return {'texts': texts, 'images': b64_images}

    def _create_prompt(self, data_dict: dict):
        message = [
            {
                'type': 'text',
                'text': ADMISSION_CONSULTANT_PROMPT.format('\n\n'.join(data_dict['context']['texts']), data_dict['question'])
            }
        ]

        if data_dict['context']['images']:
            for image in data_dict['context']['images']:
                message.append(
                    {
                        'type': 'image_url',
                        'image_url': {'url': f'data:image/{get_image_type(image)};base64,{image}'}
                    }
                )
                
        return [HumanMessage(content=message)]