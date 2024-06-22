import time
import multiprocessing
from langchain_google_genai.llms import GoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings

class GeminiConfig:
    model_types = ['chat', 'llm', 'embedding']
    EMBEDDING_MODEL_NAME = 'models/text-embedding-004'
    LLM_MODEL_NAME = 'gemini-1.5-flash-latest'
    batch_size = 5

    max_requests_per_minute = 15

    # Using Manager to create shared state
    manager = multiprocessing.Manager()
    shared_state = manager.dict({
        "request_counter": 0,
        "last_reset_time": 0.0
    })
    state_lock = multiprocessing.Lock()

    def __init__(self, model_type, **kwargs):
        if model_type not in self.model_types:
            raise Exception('There is no appropriate model type')

        self.model = None
        if model_type == 'chat':
            self.model = ChatGoogleGenerativeAI(model=self.LLM_MODEL_NAME, **kwargs)
        elif model_type == 'llm':
            self.model = GoogleGenerativeAI(model=self.LLM_MODEL_NAME, **kwargs)
        else:
            self.model = GoogleGenerativeAIEmbeddings(model=self.EMBEDDING_MODEL_NAME, **kwargs)

    @classmethod
    def _reset_counter(cls):
        current_time = time.time()
        if cls.shared_state["last_reset_time"] == 0.0 or current_time - cls.shared_state["last_reset_time"] >= 60:
            cls.shared_state["request_counter"] = 0
            cls.shared_state["last_reset_time"] = current_time

    @classmethod
    def _increment_counter(cls, num_request):
        with cls.state_lock:
            cls._reset_counter()
            if cls.shared_state["request_counter"] + num_request > cls.max_requests_per_minute:
                time.sleep(max(0, cls.shared_state["last_reset_time"] + 60 - time.time()))
                cls._reset_counter()
            cls.shared_state["request_counter"] += num_request