import asyncio
from src import app

async def main():
    await app.run()

if __name__=='__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f'main.py error: {e}')