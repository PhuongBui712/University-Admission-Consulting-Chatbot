# TODO: Improve by adding more advance modules (e.g. Agent, Hallucination Evaluator, Route)
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.resolve()))

from langchain.prompts import PromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.documents import Document
from langchain_core.documents.compressor import BaseDocumentCompressor
from langchain_core.vectorstores import VectorStoreRetriever
from prompts import ADMISSION_CONSULTANT_PROMPT

from typing import List


class RAG_Chain:
    # TODO: RAG chain with multi-query (multi-retriever) for scaling

    def __init__(self, llm, 
                 retriever: VectorStoreRetriever, 
                 reranker: BaseDocumentCompressor = None):
        self.llm = llm
        self.prompt = PromptTemplate.from_template(ADMISSION_CONSULTANT_PROMPT)
        self.retriever = retriever

        self.compression_retriever = ContextualCompressionRetriever(
            base_compressor=reranker, base_retriever=self.retriever
        )

    def get_chain(self):
        chain = (
            RunnableParallel(
                {"context": self.compression_retriever,
                 "question": RunnablePassthrough()}
            )
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        # -------------------------------------------------------------------------------------------------------------
        # input_data = {
        #     'context': self.retrieve_and_rerank if self.reranker else (self.retriever | self._format_documents),
        #     'question': RunnablePassthrough()
        # }
        #
        # rag_chain = (input_data | self.prompt | self.llm)

        return chain

    @staticmethod
    def _format_documents(self, documents: List[Document]):
        return '\n\n'.join([document.page_content for document in documents])
    
    def retrieve_and_rerank(self, query):
        retrieved_documents = self.retriever.invoke(query)
        document_rank = self.reranker.rerank(query=query,
                                             documents=retrieved_documents)
        reranked_documents = [retrieved_documents[rank['index']] for rank in document_rank]

        return reranked_documents