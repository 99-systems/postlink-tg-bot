import httpx

class OTPService:
    
    def __init__(self, otp_service_url, api_key: str) -> None:
        self.otp_service_url = otp_service_url
        self.api_key = api_key
    
    async def send_otp(self, phone_number: str):
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.otp_service_url}/api/v1/otp/send",
                    headers={
                        'Content-Type': 'application/json',
                        'x-api-key': self.api_key
                    },
                    json={'phone_number': phone_number}
                )
                
                response.raise_for_status()
                return response.json()
        
            except httpx.HTTPStatusError as e:
                return {"error": str(e)}
            
    async def verify_otp(self, phone_number: str, otp: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.otp_service_url}/api/v1/otp/verify",
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': self.api_key
                },
                json={'phone_number': phone_number, 'otp_code': otp}
            )
            return response.json()