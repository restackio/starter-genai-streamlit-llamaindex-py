import logging
import temporalio.client
from temporalio import worker, activity as job, workflow
import os
import asyncio
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class restack:
    def __init__(self):
        if os.path.exists('/.dockerenv'):
            self.temporal_url = "temporal:7233"
        else:
            self.temporal_url = "localhost:7233"
        self.client = None
        self.worker = None

    async def connect(self):
        try:
            self.client = await temporalio.client.Client.connect(self.temporal_url)
            logger.info(f"Connected to Temporal server at {self.temporal_url}.")
        except Exception as e:
            logger.error(f"Failed to connect to Temporal server at {self.temporal_url}: {e}")

    async def container(self, workflows, jobs):
        await self.connect()
        if self.client:
            try:
                logger.info("Starting worker...")
                self.worker = worker.Worker(
                    client=self.client,
                    task_queue="restack",
                    workflows=workflows,
                    activities=jobs,
                )
                logger.info("Worker started successfully.")
                await self.worker.run()
            except Exception as e:
                logger.error(f"Failed to start worker: {e}")
        else:
            logger.error("Worker not started due to failed connection.")


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

class service:
    
    async def docker_check():
        try:
            result = subprocess.run(["docker", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                logger.error("Docker daemon is not running.")
                return False
            return True
        except Exception as e:
            logger.error(f"Error checking Docker daemon: {e}")
            return False
    
    async def docker_build(name, dockerfile_content, logs=True):
        dockerfile_path = f"./tmp/Dockerfile.{name}"
        os.makedirs(os.path.dirname(dockerfile_path), exist_ok=True)
        
        with open(dockerfile_path, "w") as dockerfile:
            dockerfile.write(dockerfile_content)
        
        build_command = ["docker", "build", "-t", f"{name}-image", "-f", dockerfile_path, "."]
        build_process = await asyncio.create_subprocess_exec(*build_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        
        if logs:
            while True:
                line = await build_process.stdout.readline()
                if line:
                    logger.info(f"docker_build::{name}:: {line.decode().strip()}")
                else:
                    break
            
            while True:
                line = await build_process.stderr.readline()
                if line:
                    logger.error(f"docker_build::{name}:: {line.decode().strip()}")
                else:
                    break
        
        await build_process.wait()

    async def docker_run(name, ports=None, logs=True):
        # Remove the existing container if it exists
        remove_command = ["docker", "rm", "-f", name]
        try:
            run_process = await asyncio.create_subprocess_exec(*remove_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        except Exception as e:
            logger.error(f"Failed to remove docker container {name}: {e}")
            return

        run_command = ["docker", "run", "--name", name]
        if ports:
            for port in ports:
                run_command.extend(["-p", f"{port}:{port}"])
        run_command.append(f"{name}-image")
        
        try:
            run_process = await asyncio.create_subprocess_exec(*run_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        except Exception as e:
            logger.error(f"Failed to run docker container {name}: {e}")
            return
        
        if logs:
            while True:
                line = await run_process.stdout.readline()
                if line:
                    logger.info(f"docker_run::{name}:: {line.decode().strip()}")
                else:
                    break
            
            while True:
                line = await run_process.stderr.readline()
                if line:
                    logger.error(f"docker_run::{name}:: {line.decode().strip()}")
                else:
                    break
        
        await run_process.wait()

    async def local_run(command, name):
        logger.info(f"local_run::{name}:: Starting {name} with command: {command}")
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        except Exception as e:
            logger.error(f"Failed to start local process {name}: {e}")
            return
        
        while True:
            line = await process.stdout.readline()
            if line:
                logger.info(f"local_run::{name}::stdout:: {line.decode().strip()}")
            else:
                break
        
        while True:
            line = await process.stderr.readline()
            if line:
                logger.error(f"local_run::{name}::stderr:: {line.decode().strip()}")
            else:
                break
        
        return_code = await process.wait()
        logger.info(f"local_run::{name}:: Process exited with return code {return_code}")

    async def remove(name):
        remove_command = ["docker", "rm", "-f", name]
        remove_process = await asyncio.create_subprocess_exec(*remove_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        
        while True:
            line = await remove_process.stdout.readline()
            if line:
                logger.info(f"remove_service::{name}:: {line.decode().strip()}")
            else:
                break
        
        while True:
            line = await remove_process.stderr.readline()
            if line:
                logger.error(f"remove_service::{name}:: {line.decode().strip()}")
            else:
                break
        
        await remove_process.wait()