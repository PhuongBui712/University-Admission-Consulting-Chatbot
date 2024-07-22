import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain.retrievers import MultiVectorRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.documents.compressor import BaseDocumentCompressor
from langchain_core.retrievers import BaseRetriever


from src.prompts import ADMISSION_CONSULTANT_PROMPT
from src.utils import get_image_type

from typing import List


class RAG:
    def __init__(self,
                 chat_model: BaseChatModel,
                 multivector_retriever: BaseRetriever,
                 reranker: BaseDocumentCompressor,
                 num_retrieved_docs: int = 5,
                 compress_docs: bool = False):
        
        self.chat_model = chat_model
        self.multivector_retriever = multivector_retriever
        self.reranker = reranker
        self.num_retrieved_docs = num_retrieved_docs
        self.reorder_method = self._compress_documents if compress_docs else self._rerank_documents

    def get_chain(self):
        chain = (
            RunnableLambda(self._parse_input)
            | {
                'context': 
                    RunnableLambda(print)
                    | self.multivector_retriever 
                    | RunnableLambda(self._split_text_image_content),
                'question': RunnablePassthrough(),
            }
            | RunnableLambda(self.reorder_method)
            | RunnableLambda(self._create_prompt)
            | self.chat_model
            | StrOutputParser()
        )

        return chain
    
    def _parse_input(self, input):
        if isinstance(input, dict):
            if 'undefined' in input:
                return input['undefined'][-1]['content']
            return input['text']
        return input

    def _split_text_image_content(self, retrieved_docs: List[Document]):
        texts = []
        b64_images = []
        for i, doc in enumerate(retrieved_docs):
            if doc.metadata.get('type') == 'image':
                b64_images.append(doc.page_content)
            else:
                texts.append(doc)

        return {'texts': texts, 'images': b64_images}
    
    def _compress_documents(self, data_dict: dict):
        compressed_texts = self.reranker.compress_documents(documents=data_dict['context']['texts'], query=data_dict['question'])
        data_dict['context']['texts'] = compressed_texts[:self.num_retrieved_docs]

        return data_dict

    def _rerank_documents(self, data_dict: dict):
        try:
            rank = self.reranker.rerank(documents=data_dict['context']['texts'], query=data_dict['question'])
            rank = [r['index'] for r in rank[:self.num_retrieved_docs]]
            data_dict['context']['texts'] = [data_dict['context']['text'][i] for i in rank]

            return data_dict

        except:
            return self._compress_documents(data_dict)

    def _create_prompt(self, data_dict: dict):
        context = '\n\n'.join([text.page_content for text in data_dict['context']['texts']])
        message = [
            {
                'type': 'text',
                'text': ADMISSION_CONSULTANT_PROMPT.format(context, data_dict['question'])
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