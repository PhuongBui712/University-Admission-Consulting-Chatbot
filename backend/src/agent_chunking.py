from math import ceil
from typing import List
from tqdm.auto import tqdm
from pydantic import BaseModel
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_google_genai.llms import GoogleGenerativeAI
from src.prompts import CHUNKING_PROMPT
from gemini_config import GeminiConfig


class Chunks(BaseModel):
    """This class define the output of chunking model,
    used with `with_structured_output`"""
    chunks: List[str]


class GeminiChunker(GeminiConfig):
    prompt = PromptTemplate.from_template(template=CHUNKING_PROMPT)
    
    def __init__(self):
        super().__init__('llm', temperature=0.0, top_k=1, top_p=0.1)
        self.chain = self.prompt | self.model
        
    def split_text(self, text: List[str]):
        self._increment_counter(1)
        chunks = []
        for t in text:
            chunk_texts = self.chain.invoke(t)
            chunk_texts = self._parse_result(chunk_texts)
            chunks += chunk_texts
            
        return chunks
    
    def split_documents(self, documents: List[Document], batch_size=1):
        chunks = []
        for i in tqdm(range(0, len(documents), batch_size)):
            batch_documents = documents[i : i + batch_size]
            batch_metadatas = [doc.metadata for doc in batch_documents]
            batch_contents = [doc.page_content for doc in batch_documents]

            self._increment_counter(batch_size)
            batch_chunked_documents = self.chain.batch(batch_contents)
            for c, m in zip(batch_chunked_documents, batch_metadatas):
                chunk_texts = self._parse_result(c)
                chunks += [Document(page_content=text, metadata=m) for text in chunk_texts]

        return chunks
    
    def _parse_result(self, text):
        if text.startswith('```python'):
            parsed_text = text[11:-4]
        else:
            parsed_text = text[6:-4]
        
        parsed_text = parsed_text.strip().split(',\n    ')
        parsed_text = [t.strip('"') for t in parsed_text]
        return parsed_text
    