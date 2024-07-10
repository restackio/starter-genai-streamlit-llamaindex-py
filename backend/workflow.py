from datetime import timedelta
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from restack.sdk import workflow, restack

with workflow.unsafe.imports_passed_through():
    from jobs import create_or_load_index, query_index

@workflow.defn
class PdfWorkflow:
    @workflow.run
    async def workflow(self, query: str, api_key: str) -> str:
        await restack.run(create_or_load_index, (api_key), start_to_close_timeout=timedelta(seconds=300))
        response = await restack.run(query_index, (query), start_to_close_timeout=timedelta(seconds=300))
        return response