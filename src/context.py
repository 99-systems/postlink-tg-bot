from src.services import PlacesAPI, OTPService
from src.config import config

places_api = PlacesAPI(config.PLACES_BASE_URL, config.PLACES_API_KEY)
otp_service = OTPService(config.OTP_SERVICE_URL, config.OTP_API_KEY)
