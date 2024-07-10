import asyncio
import logging
import temporalio.client
from temporalio import worker
from activities import create_or_load_index, query_index
from workflow import PdfWorkflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_worker():
    client = await temporalio.client.Client.connect("localhost:7233")
    logger.info("Connected to Temporal server.")
    async with worker.Worker(
        client,
        task_queue="index-task-queue",
        workflows=[PdfWorkflow],
        activities=[create_or_load_index, query_index],
    ):
        logger.info("Worker started...")
        await asyncio.Event().wait()

if __name__ == "__main__":
    logger.info("Starting worker...")
    asyncio.run(run_worker())
    logger.info("Worker stopped.")