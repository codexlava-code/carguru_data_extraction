from typing import List

import requests, logging, json, os
from datetime import datetime
from app.config.config import settings
from app.models.schemas import VehicleData


class VehicleDataAPI:
    @staticmethod
    def post_vehicle(slack_obj, data_batch: dict) -> bool:
        url = settings.VEHICLE_API_URL
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        print(data_batch)
        # payload = [vehicle for vehicle in data_batch]
        # print(payload)
        try:
            response = requests.post(
                url,
                json=data_batch,
                headers=headers)
            response.raise_for_status()

            success_message = (
                f"✅ Successfully posted {len(data_batch)} vehicles at "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            logging.info(success_message)
            return True

        except requests.RequestException as errr:
            error_message = (
                f"❌ Error posting vehicle data at "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Error details: {str(errr)}\n"
                f"Payload: {json.dumps(data_batch, indent=2)}"
            )
            logging.error(error_message)

            if slack_obj:
                slack_obj.send_message(
                    message=error_message,
                    channel_id=settings.SLACK_CHANNEL
                )
            return False


    @staticmethod
    def get_vehicle(slack_obj) -> List[VehicleData]:
        url = settings.VEHICLE_API_URL
        headers = {"Accept": "application/json"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            vehicle_data = response.json()

            # vehicle_models = [VehicleData(**dealer) for dealer in vehicle_data]
            logging.info(
                f"✅ Successfully retrieved {len(vehicle_data)} vehicles at "
            )
            return vehicle_data

        except requests.RequestException as errr:
                err_message = (
                    f"Error❌ Error get vehicle data"
                    f"TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    f"ERROR: {str(errr)}"
                )
                logging.error(err_message)

                if slack_obj:
                    slack_obj.send_message(
                        message=err_message,
                        channel_id=settings.SLACK_CHANNEL
                    )
                return []

