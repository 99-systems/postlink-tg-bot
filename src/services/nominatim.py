import httpx

class NominatimService:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url


    async def search_by_city(self, query: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search?city={query}&format=jsonv2",
                headers={
                    'Content-Type': 'application/json',
                    'Accept-Language': 'en-US; q=0.5'
                }
            )
            return response.json()
        
    async def search(self, query: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search?q={query}&format=jsonv2",
                headers={
                    'Content-Type': 'application/json',
                    'Accept-Language': 'en-US; q=0.5'
                }
            )
            return response.json()
        
    async def reverse(self, lat: float, lon: float) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/reverse?lat={lat}&lon={lon}&format=jsonv2",
                headers={
                    'Content-Type': 'application/json',
                    'Accept-Language': 'en-US; q=0.5'
                }
            )
            return response.json()
