from langchain_core.embeddings.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec, PodSpec

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
