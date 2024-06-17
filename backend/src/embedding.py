import time
import threading
from typing import List
from langchain_core.documents import Document
from langchain_google_genai.llms import GoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings


class GeminiConfig:
    model_types = ['chat', 'llm', 'embedding']
    EMBEDDING_MODEL_NAME = 'models/embedding-004'
    LLM_MODEL_NAME = 'gemini-1.5-latest'
    batch_size = 5

    max_requests_per_minutes = 15
    request_counter = 0
    last_reset_time = None
    lock = threading.Lock()

    def __init__(self, model_type):
        if model_type not in self.model_types:
            raise Exception('There is no approriate model type')
        
        self.model = None
        if model_type == 'chat':
            self.model = ChatGoogleGenerativeAI(model=self.LLM_MODEL_NAME)
        elif model_type == 'llm':
            self.model = GoogleGenerativeAI(model=self.LLM_MODEL_NAME)
        else:
            self.model = GoogleGenerativeAIEmbeddings(model=self.EMBEDDING_MODEL_NAME)

    @classmethod
    def _reset_counter(cls):
        current_time = time.time()
        if cls.last_reset_time is None or current_time - cls.last_reset_time >= 60:
            cls.request_counter = 0
            cls.last_reset_time = time.time()

    @classmethod
    def _increment_counter(cls, num_request):
        with cls.lock:
            cls._reset_counter()
            if cls.request_counter + num_request > cls.max_requests_per_minutes:
                time.sleep(max(0, cls.last_reset_time + 60 - time.time()))
                cls._reset_counter()
            
            cls._reset_counter += num_request
            


class GeminiEmbedding(GeminiConfig):
    def __init__(self):
        super().__init__(model='models/embedding-004') # TODO: optimize with `task_type` arguemnt
    
    def embed_query(self, query: str):
        return self.model.embed_query(query)

    def embed_document(self, document: Document):
        self._increment_counter(1)
        return Document(
            page_content=super().embed_query(document.page_content),
            metadata=document.metadata
        )

    
    def embed_documents(self, documents: List[Document]):
        self._increment_counter(self.batch_size)

        texts = [doc.page_content for doc in documents]
        titles = [doc.metadata['title'] for doc in documents]
        
        embeddings = self.model.embed_documents(texts, title=titles, batch_size=self.batch_size)
        return embeddings