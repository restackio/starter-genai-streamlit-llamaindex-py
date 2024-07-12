from restack.sdk import service
import os

async def serve(name, script, docker=False, port=8501):
    if docker:
        script_filename = os.path.basename(script)
        dockerfile_content = f"""
FROM python:3.9-slim
WORKDIR /restack
COPY restack/ .
WORKDIR /app
COPY {os.path.dirname(script)}/ .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE {port}
CMD ["streamlit", "run", "{script_filename}", "--server.port={port}", "--server.address=0.0.0.0"]
        """
        await service.docker_build(name, dockerfile_content)
        await service.docker_run(name, ports=[port])
    else:
        command = ["streamlit", "run", script, f"--server.port={port}", "--server.address=0.0.0.0"]
        await service.local_run(command, name)