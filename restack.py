import asyncio
import sys
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
    
    await self.service(
        name='frontend',
        image='starter-frontend-image:latest',
        build_context='.',
        dockerfile='./docker/Dockerfile.frontend',
        ports=['8501:8501'],
        environment=['TEMPORAL_URL=temporal:7233'],
        depends_on=[backend['name'], temporal['name']]
    )

@stack.defn
async def stack_down(self):
    await self.remove_service(name='frontend')
    await self.remove_service(name='backend')
    await self.remove_service(name='temporal')

if __name__ == "__main__":
    import asyncio
    if len(sys.argv) != 2 or sys.argv[1] not in ["up", "down"]:
        print("Usage: python restack.py [up|down]")
        sys.exit(1)
    
    action = sys.argv[1]
    if action == "up":
        asyncio.run(stack_up())
    elif action == "down":
        asyncio.run(stack_down())