import logging
import temporalio.client
from temporalio import worker, activity as job, workflow
import os
import docker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class restack:
    def __init__(self, temporal_url=None):
        self.temporal_url = temporal_url or os.getenv("TEMPORAL_URL", "localhost:7233")
        self.client = None
        self.worker = None

    async def connect(self):
        self.client = await temporalio.client.Client.connect(self.temporal_url)
        logger.info("Connected to Temporal server.")

    async def container(self, workflows, jobs):
        await self.connect()
        self.worker = worker.Worker(
            client=self.client,
            task_queue="restack",
            workflows=workflows,
            activities=jobs,
        )
        logger.info("Worker started...")
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

class stack:
    def __init__(self):
        self.services = []
        self.client = self._initialize_docker_client()

    def _initialize_docker_client(self):
        try:
            client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
            client.ping()  # Check if Docker daemon is accessible
            logger.info("Initialized stack instance and connected to Docker daemon.")
            return client
        except docker.errors.DockerException as e:
            logger.error(f"Failed to initialize Docker client or connect to Docker daemon: {e}")
            raise

    @staticmethod
    def defn(func):
        async def wrapper(*args, **kwargs):
            instance = stack()
            logger.info("Starting stack definition.")
            await func(instance, *args, **kwargs)
            await instance.build_and_run_services()
            logger.info("Completed stack definition.")
        return wrapper

    async def service(self, name, image, build_context, dockerfile, ports=None, environment=None, depends_on=None):
        service = {
            'name': name,
            'image': image,
            'build': {
                'context': build_context,
                'dockerfile': dockerfile,
                'args': ['DOCKER_BUILDKIT=1']
            },
            'ports': ports or [],
            'environment': environment or [],
            'depends_on': depends_on or []
        }
        self.services.append(service)
        logger.info(f"Added service: {name}")
        return service

    async def build_and_run_services(self):
        await self._build_and_run_service_group(self.services)

    async def _build_and_run_service_group(self, services):
        for service in services:
            await self._build_and_run_service(service)

    async def _build_and_run_service(self, service):
        name = service['name']
        image = service['image']
        build_context = service['build']['context']
        dockerfile = service['build']['dockerfile']
        ports = {f"{port.split(':')[0]}/tcp": int(port.split(':')[1]) for port in service['ports']}
        environment = {env.split('=')[0]: env.split('=')[1] for env in service['environment']}
        depends_on = service['depends_on']

        try:
            # Check if the image already exists
            if not self.client.images.list(name=image):
                # Build the Docker image
                logger.info(f"Building image for service: {name}")
                image, logs = self.client.images.build(path=build_context, dockerfile=dockerfile, tag=image)
                for log in logs:
                    logger.info(log.get('stream', '').strip())
                logger.info(f"Built image for service: {name}")
            else:
                logger.info(f"Image for service {name} already exists. Skipping build.")

            # Run the Docker container
            self.client.containers.run(
                image,
                detach=True,
                ports=ports,
                environment=environment,
                name=name,
                links={dep: dep for dep in depends_on}
            )
            logger.info(f"Started container for service: {name}")
        except docker.errors.BuildError as e:
            logger.error(f"Failed to build image for service {name}: {e}")
            raise
        except docker.errors.APIError as e:
            logger.error(f"Failed to start container for service {name}: {e}")
            raise