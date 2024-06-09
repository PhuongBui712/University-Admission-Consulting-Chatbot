# TODO:
#  + generalize the loader for various file types
#  + generalize the splitter for various chunking methods
#  + using `unstructured` to enhance preprocessing performance

from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.documents import Document
from langchain_core.embeddings.embeddings import Embeddings

import multiprocessing
from tqdm import tqdm
from typing import List


def remove_non_utf8_characters(text: str):
    # Encode the string into bytes using UTF-8, ignoring errors
    bytes_string = text.encode('utf-8', 'ignore')
    # Decode the bytes back into a string
    clean_string = bytes_string.decode('utf-8')
    return clean_string


def get_num_cpus():
    return multiprocessing.cpu_count()


def load_pdf(file: str):
    docs = PyPDFLoader(file, extract_images=True).load()
    for doc in docs:
        doc.page_content = remove_non_utf8_characters(doc.page_content)

    return docs


class BaseLoader:
    def __init__(self) -> None:
        self.num_processes = get_num_cpus()


class PDFLoader(BaseLoader):
    def __init__(self) -> None:
        super().__init__()

    def call(self, pdf_files: List[str], **kwargs):
        num_processes = min(self.num_processes, kwargs.get('workers', 1))
        with multiprocessing.Pool(num_processes) as pool:
            doc_loaded = []
            total_files = len(pdf_files)
            with tqdm(total=total_files, desc='Loading files', unit='file') as pbar:
                for result in pool.imap_unordered(load_pdf, pdf_files):
                    doc_loaded.extend(result)
                    pbar.update(1)

        return doc_loaded


class TextSplitter:
    def __init__(self, type: str = 'semantic', embedding: Embeddings = None, **splitter_kwargs) -> None:
        if type == 'semantic' and embedding is None:
            raise Exception("Embedding must be provided for semantic chunking")

        self.splitter = SemanticChunker(embedding=embedding,
                                        breakpoint_threshold_type=splitter_kwargs.get('breakpoint_threshold_type',
                                                                                      'percentile'))

    def __call__(self, documents: List[Document]) -> List[Document]:
        return self.splitter.split_documents(documents)
