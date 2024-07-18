from langchain_chroma import Chroma
from langchain_core.embeddings.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec, PodSpec

from src.indexing import Indexing

from typing import Literal, Any


class PineconeVectorDB:
    # TODO: apply collections to save resources
    def __init__(self,
                 index_name: str,
                 embedding: Embeddings,
                 embedding_dimension: int = 1024,
                 metric: Literal['cosine', 'euclidean', 'dotproduct'] = 'cosine',
                 use_severless: bool = True,
                 create_new_index: bool = False):
        
        pinecone = Pinecone()
        spec = ServerlessSpec(cloud='aws', region='us-east-1') if use_severless else PodSpec()

        if index_name in pinecone.list_indexes().names() and create_new_index:
            pinecone.delete_index(index_name)

        if index_name not in pinecone.list_indexes().names():
            pinecone.create_index(
                index_name,
                dimension=embedding_dimension,
                metric=metric,
                spec=spec
            )

        self.vectorstore = PineconeVectorStore(index_name=index_name, embedding=embedding)

    def get_vectorstore(self):
        return self.vectorstore
    
    def get_retriever(self, **kwargs):
        return self.vectorstore.as_retriever(**kwargs)


class ChromaVectorDB:
    def __init__(self,
                 collection_name: str,
                 embedding: Embeddings,
                 metric: str,
                 persist_directory: str):
        
        self._db = Chroma(collection_name=collection_name,
                          embedding_function=embedding,
                          collection_metadata={'hnsw:space': metric},
                          persist_directory=persist_directory)
        
    def get_vectorstore(self):
        return self._db
    
    def get_retriever(self, **kwargs: Any):
        return self._db.as_retriever(**kwargs)