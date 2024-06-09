from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent.resolve()))

import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_cohere import CohereRerank
from langchain_core.pydantic_v1 import BaseModel

from src.vectorstore import VectorStore
from src.rag_chain import RAG_Chain
from src.utils import json_to_documents, get_device

from dotenv import load_dotenv

load_dotenv()
root_dir = str(Path(__file__).parent.parent.parent.parent.parent.resolve())

# get test_data
docs = json_to_documents(os.path.join(root_dir, 'data/tmp_docs.json'))

# chunking
splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " "],
    chunk_size=1024,
    chunk_overlap=256
)
chunks = splitter.split_documents(docs)reareate

# load into db
embedding = HuggingFaceEmbeddings(
    model_name='bkai-foundation-models/vietnamese-bi-encoder',
    cache_folder=os.path.join(root_dir, 'models'),
    model_kwargs={'device': get_device()},
)
vector_store = VectorStore(embedding)
vector_store.index(chunks, source_id_key='source')

# create chain
llm = GoogleGenerativeAI(model='gemini-1.5-flash-latest')
retriever = vector_store.get_retriever(k=50)
reranker = CohereRerank(cohere_api_key=os.getenv('COHERE_API_KEY'),
                        model='rerank-multilingual-v3.0',
                        top_n=20)
chain = RAG_Chain(llm=llm,
                  retriever=retriever,
                  reranker=reranker).get_chain()

# Add typing for input
class Question(BaseModel):
    __root__: str

chain = chain.with_types(input_type=Question)