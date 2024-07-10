from datetime import timedelta
from temporalio import workflow
with workflow.unsafe.imports_passed_through():
    from activities import create_or_load_index, query_index

@workflow.defn
class PdfWorkflow:
    @workflow.run
    async def run(self, query: str, api_key: str) -> str:
        persist_dir = await workflow.execute_activity(create_or_load_index, (api_key), start_to_close_timeout=timedelta(seconds=300))
        response = await workflow.execute_activity(query_index, (query), start_to_close_timeout=timedelta(seconds=300))
        return response