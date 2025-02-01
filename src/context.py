from src.services.places_api import PlacesAPI
import src.config.env_config as env


places_api = PlacesAPI(env.places_base_url, env.places_api_key)
