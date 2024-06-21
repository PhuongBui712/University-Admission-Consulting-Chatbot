import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_cohere import CohereRerank

from vectorstore import VectorStore
from rag_chain import RAG_Chain
from utils import json_to_documents, get_device


def main():
    pass


if __name__ == '__main__':
    load_dotenv()
    main()