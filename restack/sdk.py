import logging
import temporalio.client
from temporalio import worker, activity as job, workflow
import os

class restack:
    def __init__(self, temporal_url=None):
        self.temporal_url = temporal_url or os.getenv("TEMPORAL_URL", "localhost:7233")
        self.client = None
        self.worker = None

    async def connect(self):
        self.client = await temporalio.client.Client.connect(self.temporal_url)
        logging.info("Connected to Temporal server.")

    async def container(self, workflows, jobs):
        await self.connect() 
        self.worker = worker.Worker(
            client=self.client,
            task_queue="restack",
            workflows=workflows,
            activities=jobs,
        )
        logging.info("Worker started...")
        await self.worker.run()

    async def workflow(self, workflow, id, *args, **kwargs):
        await self.connect() 
        handle = await self.client.start_workflow(
            workflow=workflow,
            id=id,
            task_queue="restack",
            *args,
            **kwargs
        )
        return await handle.result()

    async def run(activity, *args, **kwargs):
        return await workflow.execute_activity(
            activity=activity,
            args=args,
            **kwargs
        )
    
    