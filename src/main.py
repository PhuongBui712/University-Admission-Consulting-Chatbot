from src.scraper.scraper import Scraper
from src.vectorstore import VectorStore
from src.rag_chain import RAG_chain
from src.utils import load_config

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama


def main():
    config = load_config()

    # crape data
    scraper = Scraper(config=config['APIFY_CONFIG'])
    docs = scraper.scrape()

    # chunking
    splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', ' ', ''],
        chunk_size=512,
        chunk_overlap=128,
    )
    chunks = splitter.split_documents(docs)

    # load into db
    embedding = OllamaEmbeddings(model='nomic-embed-text', num_gpu=1)
    vector_store = VectorStore(embedding)
    vector_store.indexing(chunks, 'source')

    # create chain
    llm = Ollama(model='llama3', num_gpu=1)
    retriever = vector_store.get_retriever()
    chain = RAG_chain(llm).get_chain(retriever)

    user_input = None
    while True:
        user_input = input('Input: ')
        if user_input == '\\exit':
            break
        print(chain.invoke(user_input))

if __name__ == '__main__':
    main()