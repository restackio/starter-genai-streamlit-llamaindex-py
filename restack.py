from restack.sdk import stack

@stack.defn
async def stack_up(self):
    
    temporal = await self.service(
        name='temporal',
        image='starter-temporal-image:latest',
        build_context='.',
        dockerfile='./docker/Dockerfile.temporal',
        ports=['7233:7233', '8233:8233']
    )
    
    backend = await self.service(
        name='backend',
        image='starter-backend-image:latest',
        build_context='.',
        dockerfile='./docker/Dockerfile.backend',
        environment=['TEMPORAL_URL=temporal:7233'],
        depends_on=[temporal['name']]
    )
    
    frontend = await self.service(
        name='frontend',
        image='starter-frontend-image:latest',
        build_context='.',
        dockerfile='./docker/Dockerfile.frontend',
        ports=['8501:8501'],
        environment=['TEMPORAL_URL=temporal:7233'],
        depends_on=[backend['name'], temporal['name']]
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(stack_up())