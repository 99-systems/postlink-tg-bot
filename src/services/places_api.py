import httpx
import json

class PlacesAPI:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url
        self.api_key = api_key


    async def search_text(self, query: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}:searchText",
                json={'textQuery': query},
                headers={
                    'Content-Type': 'application/json',
                    'X-Goog-Api-Key': self.api_key,
                    'X-Goog-FieldMask': '*'
                }
            )
            try:
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": str(e)}
            except json.JSONDecodeError as e:
                return {"error": "Invalid JSON response"}
            except httpx.HTTPStatusError as e:
                return {'error': str(e)}
