import requests, logging, json, os
from datetime import datetime
from app.config.config import settings

class DealershipData:
    def __init__(self):
        """Initialize Slack client with bot token and signing secret."""

    @staticmethod
    def post_dealership(slack_obj=None, data_batch=None):
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(
                settings.DEALERSHIP_API_URL,
                data=json.dumps(data_batch),
                headers=headers)
            response.raise_for_status()
            logging.info(f"Posted: {len(data_batch)} vehicles")
            return True
        except requests.RequestException as errr:
            err_message = (
                f"Error❌ Error Post vehicle data"
                f"TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, "
                f"ERROR: {str(errr)}"
            )
            slack_obj.send_message(
                message=err_message,
                channel_id=settings.SLACK_CHANNEL
            )
            logging.error(err_message)
            return False

    @staticmethod
    def get_dealership(slack_obj=None):
        headers = {"accept": "application/json"}
        try:
            # response = requests.get(settings.DEALERSHIP_API_URL, headers=headers)
            # response.raise_for_status()
            # return response.json()
            dealerships_api_url = [
                # {
                #   "id": "123e4567-e89b-12d3-a456-426614174000",
                #   "address_id": "223e4567-e89b-12d3-a456-426614174001",
                #   "inventory_source_id": "323e4567-e89b-12d3-a456-426614174002",
                #   "name": "Best Dealership",
                #   "phone_number": "555-123-4567",
                #   "email": "contact@bestdealership.com",
                #   "general_manager": "John Doe",
                #   "website": "http://www.bestdealership.com",
                #   "created_at": "2021-01-01T12:00:00Z",
                #   "updated_at": "2021-01-02T12:00:00Z",
                #   "inventory_source": {
                #     "id": "323e4567-e89b-12d3-a456-426614174002",
                #     "url": "https://www.cargurus.com/Cars/m-Twins-Auto-Sales--Taylor-sp457133",
                #     "category": "car_gurus",
                #     "created_at": "2021-01-01T12:00:00Z",
                #     "updated_at": "2021-01-02T12:00:00Z"
                #   }
                # },
                {
                    "id": "423e4567-e89b-12d3-a456-426614174003",
                    "address_id": "523e4567-e89b-12d3-a456-426614174004",
                    "inventory_source_id": "623e4567-e89b-12d3-a456-426614174005",
                    "name": "Quality Cars",
                    "phone_number": "555-987-6543",
                    "email": "info@qualitycars.com",
                    "general_manager": "Jane Smith",
                    "website": "http://www.qualitycars.com",
                    "created_at": "2021-02-01T12:00:00Z",
                    "updated_at": "2021-02-02T12:00:00Z",
                    "inventory_source": {
                        "id": "623e4567-e89b-12d3-a456-426614174005",
                        "url": "https://www.cargurus.com/Cars/m-Rogers-Auto-Sales-Inc-sp340683",
                        # https://www.cargurus.com/Cars/m-Carrio-MotorCars-sp385771
                        "category": "car_gurus",
                        "created_at": "2021-02-01T12:00:00Z",
                        "updated_at": "2021-02-02T12:00:00Z"
                    }
                }
            ]
            return dealerships_api_url
        except requests.RequestException as errr:
            err_message = (
                f"Error❌ Error get dealership data"
                f"TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                f"ERROR: {str(errr)}"
            )
            slack_obj.send_message(
                message=err_message,
                channel_id=settings.SLACK_CHANNEL
            )
            logging.error(err_message)
            return []