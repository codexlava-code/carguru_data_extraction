from typing import List

import requests, logging, json, os
from datetime import datetime
from app.config.config import settings
from app.models.schemas import Dealership


class DealershipDataAPI:
    def __init__(self):
        """Initialize Slack client with bot token and signing secret."""

    @staticmethod
    def post_dealership(slack_obj, data_batch: List[Dealership]) -> bool:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        api_url = settings.DEALERSHIP_API_URL

        try:
            # Properly serialize pydantic models (correct way)
            serialized_data = json.loads(data_batch[0].model_dump_json())
            print(serialized_data)
            response = requests.post(api_url, json=serialized_data, headers=headers)
            response.raise_for_status()

            success_message = (
                f"✅ Successfully posted {len(data_batch)} dealerships at "
            )
            logging.info(success_message)
            return True

        except requests.RequestException as errr:
            error_message = (
                f"❌ Error posting dealership data at "
                f"Error details: {str(errr)}\n"
                f"Payload: {json.dumps(data_batch, indent=1)}"
            )
            logging.error(error_message)
            if slack_obj:
                slack_obj.send_message(
                    message=error_message,
                    channel_id=settings.SLACK_CHANNEL
                )
            return False

    @staticmethod
    def get_dealership(slack_obj) -> List[Dealership]:
        api_url = settings.DEALERSHIP_API_URL
        headers = {"Accept": "application/json"}

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            dealerships = response.json()

            dealership_models = [Dealership(**dealer) for dealer in dealerships]
            logging.info(
                f"✅ Successfully retrieved {len(dealership_models)} dealerships at "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            return dealership_models

        except requests.RequestException as error:
            error_message = (
                f"❌ Error retrieving dealership data at "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Error details: {str(error)}"
            )
            logging.error(error_message)
            if slack_obj:
                slack_obj.send_message(
                    message=error_message,
                    channel_id=settings.SLACK_CHANNEL
                )
            return []
