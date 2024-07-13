import sys
import os
import asyncio
import logging

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from restack.sdk import restack

from jobs import create_or_load_index, query_index
from workflow import PdfWorkflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting backend script...")

async def start_container():
    try:
        sdk = restack()
        await sdk.container(
            workflows=[PdfWorkflow],
            jobs=[create_or_load_index, query_index]
        )
    except Exception as e:
        logger.error(f"Error starting container: {e}")

if __name__ == "__main__":
    logger.info("Starting container...")
    asyncio.run(start_container())
    logger.info("Container stopped.")