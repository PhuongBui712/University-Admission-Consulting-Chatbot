import os
import json
from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import task

PYTHON_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", '.venv/bin/python'))

# define dags
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

with DAG(
    dag_id='update_retriever',
    default_args=default_args,
    schedule='0 0 * * *',  # Cron expression: '0 0 * * *' | Preset Schedule Interval String: '@daily'
    start_date=datetime(2024, 6, 1),
    tags=['ETL', 'staging', 'RAG', 'daily', 'chatbot']
) as dag:
    @task.external_python(task_id='crawl_data', python=PYTHON_DIR)
    def crawl_data():
        import os, sys
        sys.path.append(os.getcwd())

        from data_etl.scraper import crawl
        from backend.src import write_json

        crawled_docs = crawl()
        if crawled_docs:
            json_docs = [json.loads(doc.json(ensure_ascii=False)) for doc in crawled_docs]
            file_path = os.path.join(os.getcwd(), 'data', 'retriever.json')
            write_json(file_path, json_docs)


    @task.external_python(task_id='process_and_ingest_data', python=PYTHON_DIR)
    def ingest_data():
        # add path
        import os, sys
        sys.path.append(os.getcwd())

        # import libraries
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from backend.src import TextSplitter
        from backend.src.vectorstore import VectorStore
        from backend.src import load_json, json_to_documents, get_device

        # load documents
        crawled_document_path = os.path.join(os.getcwd(), 'data', 'retriever.json')
        json_docs = load_json(crawled_document_path)
        docs = json_to_documents(json_docs)

        # split documents
        embedding = HuggingFaceEmbeddings(
            model_name='bkai-foundation-models/vietnamese-bi-encoder',
            cache_folder=os.path.join(os.getcwd(), 'cache'),
            model_kwargs={'device': get_device()},
        )
        splitter = TextSplitter(type='semantic', embedding=embedding)
        chunks = splitter(docs)

        # index documents
        vectorstore = VectorStore(embedding)
        vectorstore.index(documents=chunks, source_id_key='source', cleanup='full')

    crawl_data() >> ingest_data()