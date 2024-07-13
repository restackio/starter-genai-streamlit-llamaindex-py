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
        self.temporal_url = "temporal:7233"
        self.client = None
        self.worker = None

    async def connect(self):
        try:
            self.client = await temporalio.client.Client.connect(self.temporal_url)
            logger.info(f"Connected to Temporal server at {self.temporal_url}.")
        except Exception as e:
            try:
              self.client = await temporalio.client.Client.connect("localhost:7233")
              logger.info(f"Connected to Temporal server at locahost:7233.")
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

    async def run(self, activity, *args, **kwargs):
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

        logger.info(f"docker_build::{name}:: Building image...")
        
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
                    logger.info(f"docker_build::{name}:: {line.decode().strip()}")
                else:
                    break
        
        await build_process.wait()

    async def docker_run(name, script_dir=None, ports=None, hot_reload=True, logs=True, network="restack_network"):
        
        
        network_command = ["docker", "network", "create", network]
        try:
            logger.info(f"docker_run::{name}:: Checking docker network...")
            await asyncio.create_subprocess_exec(*network_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        except Exception as e:
            logger.error(f"Failed to create docker network {network}: {e}")
            return
        
        # Remove the existing container if it exists
        remove_command = ["docker", "rm", "-f", name]

        try:
            logger.info(f"docker_run::{name}:: Removing exisiting container...")
            remove_process = await asyncio.create_subprocess_exec(*remove_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await remove_process.wait()
        except Exception as e:
            logger.error(f"Failed to remove docker container {name}: {e}")
            return

        run_command = ["docker", "run", "--name", name, "--network", network, "-d"]
        if ports:
            for port in ports:
                run_command.extend(["-p", f"{port}:{port}"])
        if hot_reload:
            logger.info(f"docker_run::{name}:: Local volume mounting for hot-reloading...")
            if script_dir:
              script_dir = os.path.abspath(script_dir)
              run_command.extend(["-v", f"{script_dir}:/app"])
        run_command.append(f"{name}-image")
        
        try:
            logger.info(f"docker_run::{name}:: Creating container with command {run_command}...")
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