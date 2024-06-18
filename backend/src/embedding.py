from typing import List
from langchain_core.documents import Document
from src.gemini_config import GeminiConfig


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