import os
from dotenv import load_dotenv
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_cohere import CohereRerank

from vectorstore import VectorStore
from rag_chain import RAG_Chain
from utils import json_to_documents, get_device


def main():
    # get test_data
    docs = json_to_documents('scraper/tmp_docs.json')

    # chunking
    embedding = HuggingFaceEmbeddings(
        model_name='bkai-foundation-models/vietnamese-bi-encoder',
        cache_folder='/Users/btp712/Code/University Admission Consulting Chatbot/cache',
        model_kwargs={'device': get_device()},
    )
    splitter = SemanticChunker(embedding, breakpoint_threshold_type="percentile")
    chunks = splitter.split_documents(docs)

    # load into db
    vector_store = VectorStore(embedding)
    vector_store.index(chunks, source_id_key='source')

    # create chain
    llm = GoogleGenerativeAI(model='gemini-1.5-flash-latest')
    retriever = vector_store.get_retriever(k=20)
    reranker = CohereRerank(cohere_api_key=os.getenv('COHERE_API_KEY'),
                            model='rerank-multilingual-v3.0',
                            top_n=5)
    chain = RAG_Chain(llm=llm,
                      retriever=retriever,
                      reranker=reranker)

    user_input = None
    while True:
        user_input = input('Input: ')
        if user_input == '\\exit':
            break
        print(chain.invoke(user_input))


if __name__ == '__main__':
    load_dotenv()
    main()