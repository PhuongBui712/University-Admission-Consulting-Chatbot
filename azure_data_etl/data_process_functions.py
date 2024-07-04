import uuid
from dotenv import load_dotenv
from multiprocessing import freeze_support
from hashlib import sha256
from tqdm import tqdm
from typing import Dict, List, Union, Tuple, Sequence

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_cohere import CohereEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.storage import MongoDBStore

from modules.image_extractor import *
from modules.agent_chunking import GeminiChunker
from modules.vectorstore import PineconeVectorDB
from modules.prompts import TEXT_SUMMARIZE_PROMPT, IMAGE_SUMMARIZE_PROMPT


load_dotenv()


# Essential varilables
LLM_MODEL = 'gemini-1.5-flash-latest'
EMBEDDING_MODEL = 'embed-multilingual-v3.0'

# Hellper functions
def generate_text_summaries(texts: Union[List[str], List[Document]],
                            tables: Union[List[str], List[Document]],
                            summary_text: bool = True) -> Tuple[List[str], List[str]]:
    """
    Generates summaries for a list of texts and tables.

    Args:
        texts (Union[List[str], List[Document]]): A list of texts or documents to summarize.
        tables (Union[List[str], List[Document]]): A list of tables or documents to summarize.
        summary_text (bool): Whether to summarize the texts. If False, the texts will be returned as is. Defaults to True.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing the text summaries and table summaries.
    """
    prompt = PromptTemplate.from_template(template=TEXT_SUMMARIZE_PROMPT)
    empty_response = RunnableLambda(lambda x : AIMessage(content="Error processing document"))
    model = GoogleGenerativeAI(model=LLM_MODEL, temperature=0.0, top_k=1, top_p=0.1).with_fallbacks([empty_response])
    chain = prompt | model | StrOutputParser()

    text_summaries = []
    table_summaries = []
    if texts and summary_text:
        if isinstance(texts[0], Document):
            texts = [t.page_content for t in texts]
        
        text_summaries = chain.batch(texts, {'max_concurrency':1})
    else:
        text_summaries = texts

    if tables:
        if isinstance(tables[0], Document):
            tables = [t.page_content for t in tables]
        table_summaries = chain.batch(tables, {'max_concurrency':1})

    return text_summaries, table_summaries


def generate_image_summaries(image_paths: Sequence[str]) -> Tuple[List[str], List[str]]:
    """
    Generates summaries for a list of images.

    Args:
        image_paths (Sequence[str]): A list of image paths.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing the base64 encoded images and the image summaries.
    """
    model = GeminiImageExtractor(custom_prompt=IMAGE_SUMMARIZE_PROMPT)
    image_summaries = []
    b64_images = []
    for image in tqdm(sorted(image_paths)):
        image_summaries.append(model.invoke(image))
        b64_images.append(encode_image(get_image(image)))

    return b64_images, image_summaries


# Main process functions
def process_data(data_dict: Dict) -> Tuple[List[Document], List[str]]:
    """
    Processes the data dictionary and generates summaries for texts, tables, and images.

    Args:
        data_dict (Dict): A dictionary containing the data to be processed.

    Returns:
        Tuple[List[Document], List[str]]: A tuple containing the processed documents and their summaries.
    """
    # extract data from dict
    texts = [Document(page_content=v['text'], metadata={'source': k, 'type': 'text', 'title': v['title']}) for k, v in data_dict.items()]

    tables = []
    for k, v in data_dict.items():
        for table in v['table']:
            tables.append(Document(page_content=table, metadata={'source': k, 'type': 'table', 'title': v['title']}))

    # chunking texts
    # chunker = GeminiChunker()
    # texts = chunker.split_documents(texts)

    # generate summaries for texts, tables
    text_summaries, table_summaries = generate_text_summaries(texts=texts, tables=tables, summary_text=True)

    # generate summaries for images
    images = []
    image_summaries = []
    for k, v in data_dict.items():
        if v['image_path']:
            b64_images, summaries = generate_image_summaries(v['image_path'])
            images += [Document(page_content=image, metadata={'source': k, 'type': 'image', 'title': v['title']}) for image in b64_images]
            image_summaries += summaries

    docs = texts + tables + images
    summaries = text_summaries + table_summaries + image_summaries

    return docs, summaries


def ingest_data(documents: Sequence[Document], summaries: Sequence[str]) -> Dict:
    """
    Ingests the processed documents and summaries into a vector store and document store.

    Args:
        documents (Sequence[Document]): A sequence of processed documents.
        summaries (Sequence[str]): A sequence of summaries for the documents.

    Returns:
        Dict: A dictionary mapping hashed URLs to embedding IDs.
    """
    # initialize vector store and docstore
    vector_db = PineconeVectorDB(index_name=os.environ['PINECONE_INDEX'],
                                 embedding=CohereEmbeddings(model=EMBEDDING_MODEL))
    vectorstore = vector_db.get_vectorstore()

    docstore = MongoDBStore(connection_string=os.environ['MONGODB_ATLAS_CLUSTER_URI'],
                            db_name=os.environ['MONGODB_DB_NAME'],
                            collection_name=os.environ['MONGODB_COLLECTION_NAME'])
    
    # generate id and map summaries to documents
    id_key = 'doc_id'

    doc_ids = [str(uuid.uuid4()) for _ in range(len(documents))]
    doc_summaries = [
        Document(page_content=s, metadata={id_key: doc_ids[i]}) \
        for i, s in enumerate(summaries)
    ]

    # ingest summaries to vector store
    embedding_ids = vectorstore.add_documents(doc_summaries)

    # ingest documents to docstore
    map_id = {} # it is used to map hashed url - embedding ids
    for d, e_id in zip(documents, embedding_ids):
        hash_source = sha256(d.metadata['source'].encode()).hexdigest()
        if hash_source not in map_id:
            map_id[hash_source] = []

        map_id[hash_source].append(e_id)

    docstore.mset(list(zip(doc_ids, documents)))

    return map_id
