import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from langchain_cohere import CohereRerank, CohereEmbeddings
from langchain.retrievers import MultiVectorRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_community.storage import MongoDBStore
from langsmith import Client

from src.rag_chain import RAG
from src.vectorstore import ChromaVectorDB


load_dotenv()
client = Client()
data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database'))

vector_db = ChromaVectorDB(
    collection_name='multimodal',
    embedding=CohereEmbeddings(model='embed-multilingual-v3.0'),
    metric='cosine',
    persist_directory=data_path
)

store = MongoDBStore(connection_string=os.getenv('MONGODB_ATLAS_CLUSTER_URI'),
                     db_name='document-store',
                     collection_name='document-collection')

multivector_retriever = MultiVectorRetriever(
    vectorstore=vector_db.get_vectorstore(),
    docstore=store,
    id_key='doc_id',
    search_type='similarity',
    search_kwargs={'k': 10}
)

reranker = CohereRerank(model='rerank-multilingual-v3.0')

chain = RAG(
    chat_model=ChatGoogleGenerativeAI(model='gemini-1.5-flash-latest'),
    multivector_retriever=multivector_retriever,
    reranker=reranker,
    num_retrieved_docs=5,
    compress_docs=False
)
chain = chain.get_chain()