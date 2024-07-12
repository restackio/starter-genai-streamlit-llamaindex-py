import asyncio
import sys
from restack.sdk import restack, service
from restack_services import streamlit, python, temporal

class Stack:
    
    async def stack_init(self):
        await temporal.serve("temporal")

    async def stack_start(self, docker=False):
        await python.run("backend", "backend/backend.py", docker)
        await streamlit.serve("frontend", "frontend/frontend.py", docker)

    async def stack_down(self):
        await service.remove(name='frontend')
        await service.remove(name='backend')
        await service.remove(name='temporal')

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ["init", "dev", "docker", "down"]:
        print("Usage: python restack.py [init|dev|docker|down]")
        sys.exit(1)
    
    action = sys.argv[1]

    sdk = restack()
    stack = Stack()
    if action == "init":
        asyncio.run(stack.stack_init())
    if action == "dev":
        asyncio.run(stack.stack_start(docker=False))
    elif action == "docker":
        asyncio.run(stack.stack_start(docker=True))
    elif action == "down":
        asyncio.run(stack.stack_down())