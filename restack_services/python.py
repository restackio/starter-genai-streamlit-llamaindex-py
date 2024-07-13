from restack.sdk import service
import logging

logger = logging.getLogger(__name__)


async def run(name, script_dir, script_filename, hot_reload=False):
    if not await service.docker_check():
        return
    dockerfile_content = f"""
FROM python:3.9-slim
WORKDIR /restack
COPY restack/ .
WORKDIR /app
COPY {script_dir}/ .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "{script_filename}"]
    """
    await service.docker_build(name, dockerfile_content, logs=True)
    await service.docker_run(name, script_dir, hot_reload=hot_reload, logs=True)