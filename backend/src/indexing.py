import os
from typing import List, Literal
from langchain.indexes import index, SQLRecordManager
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document


class Indexing:
    def __init__(self, collection_name: str, db_url: str = None):
        db_url = db_url or os.path.abspath(os.path.join(os.path.dirname(__file__), '../database'))
        
        self.record_manager = SQLRecordManager(
            namespace=collection_name, db_url=f'sqlite:///{self.db_url}/{collection_name}.sql'
        )

        self.record_manager.create_schema()

    
    def index(self,
              documents: List[Document], 
              vectorstore: VectorStore,
              source_id_key: str,
              deletion_mode: Literal[None, 'incremental', 'full'] = None):
        
        return index(
            docs_source=documents,
            record_manager=self.record_manager,
            vector_store=vectorstore,
            source_id_key=source_id_key,
            cleanup=deletion_mode
        )