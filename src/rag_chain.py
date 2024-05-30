# TODO: Improve by adding more advance modules (e.g. Agent, Hallucination Evaluator, Route)

from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_core.documents.compressor import BaseDocumentCompressor
from langchain_core.vectorstores import VectorStoreRetriever
from prompts import ADMISSION_CONSULTANT_PROMPT

from typing import List


class RAG_chain:
    # TODO: RAG chain with multi-query (multi-retriever) for scaling
    def __init__(self, llm, 
                 retriever: VectorStoreRetriever, 
                 reranker: BaseDocumentCompressor = None):
        self.llm = llm
        self.prompt = PromptTemplate.from_template(ADMISSION_CONSULTANT_PROMPT)
        self.retriever = retriever
        self.reranker = reranker

    def invoke(self, query: str, max_retrieved_documents: int = 5):
        input_data = {
            'context': self.retrieve_and_rerank if self.reranker else (self.retriever | self.format_documents),
            'question': RunnablePassthrough()
        }

        rag_chain = (input_data | self.prompt | self.llm)
        result = rag_chain.invoke(query)
        
        return result

    def format_documents(self, documents: List[Document]):
        return '\n\n'.join([document.page_content for document in documents])
    
    def retrieve_and_rerank(self, query):
        retrieved_documents = self.retriever.invoke(query)
        document_rank = self.reranker.rerank(query=query,
                                             documents=retrieved_documents)
        reranked_documents = [retrieved_documents[rank['index']] for rank in document_rank]

        return reranked_documents