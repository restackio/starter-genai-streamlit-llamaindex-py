from restack.sdk import service

async def serve(name, script_dir, script_filename, hot_reload=True, port=8501):
    if not await service.docker_check():
        return
    file_watcher_option = "--server.fileWatcherType=watchdog" if hot_reload else ""
    dockerfile_content = f"""
FROM python:3.9-slim
WORKDIR /restack
COPY restack/ .
WORKDIR /app
COPY {script_dir}/ .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE {port}
CMD ["streamlit", "run", "{script_filename}", "--server.port={port}", "--server.address=0.0.0.0", "{file_watcher_option}"]
    """
    await service.docker_build(name, dockerfile_content, logs=True)
    await service.docker_run(name, script_dir, ports=[port], hot_reload=hot_reload, logs=True)