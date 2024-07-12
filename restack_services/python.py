from restack.sdk import service
import os
import logging

logger = logging.getLogger(__name__)


async def run(name, script, docker=False):
    if docker:
        script_filename = os.path.basename(script)
        dockerfile_content = f"""
FROM python:3.9-slim
WORKDIR /restack
COPY restack/ .
WORKDIR /app
COPY {os.path.dirname(script)}/ .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "{script_filename}"]
        """
        await service.docker_build(name, dockerfile_content)
        await service.docker_run(name)
    else:
        command = ["python", script]
        logger.info(f"Executing command: {command}")
        await service.local_run(command, name)