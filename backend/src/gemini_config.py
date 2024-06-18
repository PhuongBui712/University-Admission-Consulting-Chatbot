import time
import threading
from langchain_google_genai.llms import GoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings


class GeminiConfig:
    model_types = ['chat', 'llm', 'embedding']
    EMBEDDING_MODEL_NAME = 'models/text-embedding-004'
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
            
            cls.request_counter += num_request
