import os
import json
import logging
from temporalio import activity
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PERSIST_DIR = "./storage"

@activity.defn
async def create_or_load_index(api_key: str):
    logger.info("Starting create_or_load_index activity.")
    try:
        logger.info(f"Recreating index in {PERSIST_DIR}.")
        
        # Set the OpenAI API key
        openai.api_key = api_key
        
        # Ensure the storage directory exists
        os.makedirs(PERSIST_DIR, exist_ok=True)

        # Load documents and create a new index
        documents = SimpleDirectoryReader(input_dir="./data").load_data()
        index = VectorStoreIndex.from_documents(documents)
        
        # Persist the new index
        index.storage_context.persist(persist_dir=PERSIST_DIR)

        return True

    except Exception as e:
        logger.exception(f"Failed to create or load index: {e}")
        raise

@activity.defn
async def query_index(query: str):
    logger.info(f"Starting query_index activity with query: {query}")
    try:
        # Load the index from the persisted directory
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        
        query_engine = index.as_query_engine()
        result = query_engine.query(query)
        logger.info(f"Query result: {result}")
        
        return result
    except Exception as e:
        logger.exception(f"Failed to query index: {e}")
        raise