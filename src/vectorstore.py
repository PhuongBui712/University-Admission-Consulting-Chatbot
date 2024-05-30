# TODO: Initially, we will use a local vector database like Chroma but will switch if the program scales up.

from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from langchain.indexes import index, SQLRecordManager
from langchain_core.embeddings.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

import os
from typing import Union

class _IndexingConfig_:
    db_dir = '../database/'

    def __init__(self, collection_name: str = 'vectorstore'):
        self.record_manager_path = f'{self.db_dir}/{collection_name}.sql'
        self.record_manager = SQLRecordManager(
            collection_name, db_url=f'sqlite:///{self.record_manager_path}'
        )

        if not os.path.exists(self.record_manager_path):
            self.record_manager.create_schema()

    def indexing(self, documents, vectorstore, source_id_key, cleanup='full'):
        index(
            docs_source=documents,
            vector_store=vectorstore,
            record_manager=self.record_manager,
            source_id_key=source_id_key,
            cleanup=cleanup
        )


class VectorStore(_IndexingConfig_):
    def __init__(self,
                 embedding_function: Embeddings,
                 relevant_score: str = 'cosine',
                 collection_name: str = 'vectorstore'):
        super().__init__(collection_name)

        # TODO: Modify database (maybe cloud storage) for scaling
        self.embedding = embedding_function
        self.collection_metadata = {'hnsw:space': relevant_score}
        self.vector_db = Chroma(embedding_function=self.embedding,
                                persist_directory=self.db_dir,
                                collection_metadata=self.collection_metadata)

    def indexing(self, documents, source_id_key, cleanup='full'):
        super().indexing(documents, self.vector_db, source_id_key, cleanup)

    def get_retriever(self, k=5):
        return self.vector_db.as_retriever(search_kwargs={'k': k})

    def get_db(self):
        return self.vector_db