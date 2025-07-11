from src.services import OTPService, NominatimService
from src.config import config

# otp_service = OTPService(config.OTP_SERVICE_URL, config.OTP_API_KEY)
nominatim_service = NominatimService(config.NOMINATIM_API_URL)