# TODO: Improve by adding more advance modules (e.g. Agent, Hallucination Evaluator, Route)

from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from src.prompts import LLAMA3_RAG_PROMPT

from typing import List


class RAG_chain:
    # TODO: RAG chain with multi-query (multi-retriever) for scaling
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate.from_template(LLAMA3_RAG_PROMPT)

    def get_chain(self, retriever):
        input_data = {
            'context': retriever | self.format_documents,
            'question': RunnablePassthrough()
        }

        rag_chain = (input_data | self.prompt | self.llm)
        return rag_chain


    def format_documents(self, documents: List[Document]):
        return '\n\n'.join([document.page_content for document in documents])