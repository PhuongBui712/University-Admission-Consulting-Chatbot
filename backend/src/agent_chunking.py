import re
import ast
from typing import List
from pydantic import BaseModel
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_google_genai.llms import GoogleGenerativeAI
from prompts import CHUNKING_PROMPT


class Chunks(BaseModel):
    """This class define the output of chunking model,
    used with `with_structured_output`"""
    chunks: List[str]


class GeminiChunker:
    prompt = PromptTemplate.from_template(
        template=CHUNKING_PROMPT)
    
    def __init__(self):
        self.llm = GoogleGenerativeAI(model='gemini-1.5-flash-latest')
        self.chain = self.prompt | self.llm
        
    def split_text(self, text: List[str]):
        chunks = []
        for t in text:
            chunk_texts = self.chain.invoke(t)
            chunk_texts = self._parse_result(chunk_texts)
            chunks += chunk_texts
            
        return chunks
    
    def split_documents(self, documents: List[Document]):
        chunks = []
        for doc in documents:
            metadata = doc.metadata
            chunk_texts = self.split_text([doc.page_content])

            chunks += [Document(page_content=c, metadata=metadata) for c in chunk_texts]
            
        return chunks
    
    def _parse_result(self, result):
        match = re.search(r'\[.*\]', result, re.DOTALL)

        parsed_chunks = match.group(0)
        parsed_chunks = ast.literal_eval(parsed_chunks)

        return parsed_chunks
    