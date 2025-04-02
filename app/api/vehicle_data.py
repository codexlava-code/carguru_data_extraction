import requests, logging, json, os
from datetime import datetime
from app.config.config import settings

class VehicleData:
    def __init__(self):
        """Initialize Slack client with bot token and signing secret."""

    @staticmethod
    def post_vehicle(slack_obj=None, data_batch=None):
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(
                settings.VEHICLE_API_URL,
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
    def get_vehicle(slack_obj=None):
        headers = {"accept": "application/json"}
        try:
            response = requests.get(settings.VEHICLE_API_URL, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as errr:
            err_message = (
                f"Error❌ Error get vehicle data"
                f"TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                f"ERROR: {str(errr)}"
            )
            slack_obj.send_message(
                message=err_message,
                channel_id=settings.SLACK_CHANNEL
            )
            logging.error(err_message)
            return []

