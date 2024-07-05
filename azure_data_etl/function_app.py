import json
import logging
import azure.functions as func
from langchain_core.documents import Document
from langchain_community.storage import MongoDBStore

from modules.scraper.scrape import crawl
from azure_helper_functions import *
from data_process_functions import process_data, ingest_data


# TODO: Only implemented ADD operation, not yet implemented DELETE and UPDATE yet


app = func.FunctionApp()


@app.schedule(
    schedule="0 0 * * * *", arg_name="myTimer", run_on_startup=True, use_monitor=False
)
def AdmissionDataETL(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")

    # define essential variables
    container_name = "hcmus-admission-data"
    sitemap_blob_name = "sitemap.json"
    map_id_blob_name = "map_id.json"
    local_sitemap_file_path = "./data/sitemap.json"

    # get BlobServiceClient
    blob_service_client = get_blob_service_client()

    # initialize container, blob client
    container_client = initialize_container_client(
        blob_service_client=blob_service_client, container_name=container_name
    )
    sitemap_blob_client = initialize_blob_client(
        blob_service_client=blob_service_client,
        container_name=container_name,
        blob_name=sitemap_blob_name,
        local_blob_path=local_sitemap_file_path,
    )

    # read blob
    sitemap = read_azure_json_blob(sitemap_blob_client)

    # crawl
    logging.info('Start crawling data...')
    updated_sitemap, data_dict = crawl(sitemap)
    logging.info('Complete crawling')
    # there's new data
    if data_dict:
        logging.info('New data found, updating sitemap...')

        # update sitemap file
        logging.info('Update sitemap file')
        write_azure_json_blob(updated_sitemap, blob_client=sitemap_blob_client)

        # proceed data
        logging.info('Start processing data...')
        documents, summaries = process_data(data_dict=data_dict)
        logging.info('Complete processing data')

        # ingest data
        logging.info('Start ingesting data...')
        map_id = ingest_data(documents=documents, summaries=summaries)
        logging.info('Complete ingesting data')

        # create map_id blob client
        map_id_blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=map_id_blob_name
        )

        # upload map_id
        logging.info('Uploading map_id...')
        map_id_str = json.dumps(map_id, indent=4)
        map_id_blob_client.upload_blob(map_id_str)
        logging.info('Uploaded map_id')