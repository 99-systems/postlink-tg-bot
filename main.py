import asyncio
import src.app as app

async def main():
   await app.run()

if __name__=='__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f'main.py error: {e}')