import os
import json
import logging
from typing import Optional, Dict
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


def initialize_container_client(blob_service_client: BlobServiceClient,
                                container_name: str,
                                force_recreate: Optional[bool] = False) -> ContainerClient:
    """
    Initializes a container client for Azure Blob Storage.

    Args:
        blob_service_client (BlobServiceClient): The BlobServiceClient object to interact with Azure Blob Storage.
        container_name (str): The name of the container to initialize.
        force_recreate (Optional[bool], optional): Whether to force recreate the container if it already exists. Defaults to False.

    Returns:
        ContainerClient: The ContainerClient object for the specified container.
    """
    container_client = blob_service_client.get_container_client(container_name)
    if container_client.exists() and force_recreate:
        logging.info(f'Deleting existing container "{container_name}"')
        blob_service_client.delete_container(container_name)

    if not container_client.exists():
        logging.info('Creating new container.')

        container_client = blob_service_client.create_container(container_name)

    return container_client


def initialize_blob_client(blob_service_client: BlobServiceClient,
                           container_name: str,
                           blob_name: str,
                           local_blob_path: Optional[str] = None,
                           overwrite: Optional[bool] = True) -> BlobClient:
    """
    Initializes a blob client for Azure Blob Storage.

    Args:
        blob_service_client (BlobServiceClient): The BlobServiceClient object to interact with Azure Blob Storage.
        container_name (str): The name of the container to initialize.
        blob_name (str): The name of the blob to initialize.
        local_blob_path (Optional[str], optional): The path to the local blob file. Defaults to None.
        overwrite (Optional[bool], optional): Whether to overwrite the blob if it already exists. Defaults to True.

    Returns:
        BlobClient: The BlobClient object for the specified blob.
    """
    if not blob_service_client.get_container_client(container_name).exists():
        raise Exception(f'Container "{container_name}" does not exist. Please create the container first.')
    
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    if not blob_client.exists():
        logging.error(f'Blob "{blob_name}" does not exist.')
        if local_blob_path:
            try:
                with open(local_blob_path, 'rb') as data:
                    blob_client.upload_blob(data, overwrite=overwrite)
                    logging.info(f'Uploaded blob "{blob_name}" from local file "{local_blob_path}"')
                
            except Exception as error:
                logging.error(f'Failed to upload local blob: {error}')
                logging.info('Return an empty blob client!')
            
    else:
        logging.info(f'Blob "{blob_name}" already exists.')        

    return blob_client

def get_blob_service_client() -> BlobServiceClient:
    """
    Retrieves the BlobServiceClient object to interact with Azure Blob Storage.

    This function reads the connection string from the environment variable 'AzureWebJobsStorage'.
    If the connection string indicates the use of development storage, it retrieves the connection string
    from 'AZURE_DEVELOPMENT_CONNECTION_STR' environment variable. Otherwise, it uses the provided connection string.

    Returns:
        BlobServiceClient: The BlobServiceClient object to interact with Azure Blob Storage.
    """
    connect_str = os.environ['AzureWebJobsStorage']
    if connect_str == "UseDevelopmentStorage=true":
        blob_service_client = BlobServiceClient.from_connection_string(os.environ['AZURE_DEVELOPMENT_CONNECTION_STR'])
    else:
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    return blob_service_client


def read_azure_json_blob(blob_client: Optional[BlobClient] = None,
                         container: Optional[str] = None,
                         blob: Optional[str] = None) -> Dict:
    if not blob_client:
        if not (container and blob):
            raise ValueError("Either blob_client or both container and blob must be provided")
        
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(container=container, blob=blob)

    try:
        stream_downloader = blob_client.download_blob()
    except Exception as error:
        logging.error(f'Failed to download blob: {error}')
        return None
    
    json_data = json.loads(stream_downloader.readall())

    return json_data


def write_azure_json_blob(data: Dict,
                          blob_client: Optional[BlobClient] = None,
                          container: Optional[str] = None,
                          blob: Optional[str] = None,
                          overwrite: Optional[bool] = True) -> None:
    if not blob_client:
        if not (container and blob):
            raise ValueError("Either blob_client or both container and blob must be provided")
        
        blob_service_client = get_blob_service_client()
        if not blob_service_client.get_container_client(container).exists():
            raise Exception("Container does not exist.")

        blob_client = blob_service_client.get_blob_client(container=container, blob=blob)

    json_string = json.dumps(data, indent=4)
    blob_client.upload_blob(json_string, overwrite=overwrite)
