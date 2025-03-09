from typing import Optional

from aiogram.types import Message

import src.context as context


async def get_place(query: str, message: Message) -> Optional[dict]:
    if message.location:
        service_response = await context.nominatim_service.reverse(message.location.latitude, message.location.longitude)
        address = service_response.get('address', {})
        place_type = address.get('city') or address.get('town')
        query = f"{place_type}, {address.get('state', '')}, {address.get('country', '')}"

    service_response = await context.nominatim_service.search(query)
    
    if service_response:
        place = next((response_place for response_place in service_response 
                    if response_place['category'] == 'place' and 
                        response_place['type'] in ['village', 'town', 'city']), None)
        
        if not place:
            place = next((response_place for response_place in service_response 
                    if response_place['category'] == 'boundary' and 
                        response_place['type'] == 'administrative'), None)
        return place
    return None