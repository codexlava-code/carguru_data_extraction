import logging, time

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from memoization import cached,CachingAlgorithmFlag

from app.config.config import settings
from app.models.schemas import VehicleData
from app.api.vehicle_data import VehicleDataAPI
from app.utils.slack_notifier import SlackClient


class VehicleDataProcessing:
    @cached(ttl=3600, max_size=10000, algorithm=CachingAlgorithmFlag.LRU, thread_safe=True)
    @staticmethod
    def is_duplicate_vehicle_data(existing_list: List[VehicleData], new_entry: dict) -> bool:
        duplicate = any(
            record['listing_url'] == new_entry['listing_url']
            for record in existing_list
        )
        if duplicate:
            logging.warning(f"⚠️ Duplicate found and skipped: {new_entry['listing_url']}")
        return duplicate



    @staticmethod
    def post_vehicle_with_retry(
            slack_notifier: SlackClient,
            vehicle_data: dict,
            ) -> None:
        max_retry_attempts: int = settings.MAX_RETRY_ATTEMPTS
        attempts = 0
        success = False

        while attempts < max_retry_attempts and not success:
            success = VehicleDataAPI.post_vehicle(slack_notifier, vehicle_data)
            attempts += 1

            if success:
                logging.info(f"✅ Successfully sent data for URL: {vehicle_data['listing_url']} (Attempt {attempts})")
            else:
                logging.warning(
                    f"⚠️ Retry {attempts}/{max_retry_attempts} failed for URL: {vehicle_data['listing_url']}")
                if attempts < max_retry_attempts:
                    time.sleep(2)  # Delay before retrying

        if not success:
            error_message = f"❌ Failed to send data after {attempts} attempts. URL: {vehicle_data['listing_url']}"
            logging.error(error_message)
            if slack_notifier:
                slack_notifier.send_message(message=error_message, channel_id=settings.SLACK_CHANNEL)


    @staticmethod
    def process_batch(vehicle_data_batch: List[dict], slack_notifier) -> None:
        # Using ThreadPoolExecutor for concurrency
        with ThreadPoolExecutor(max_workers=settings.MAX_THREAD) as executor:
            futures = []

            for vehicle_data in vehicle_data_batch:
                # Submit the post_vehicle_with_retry function as a task to the thread pool
                futures.append(
                    executor.submit(VehicleDataProcessing.post_vehicle_with_retry, slack_notifier, vehicle_data))

            # Handle results or exceptions
            for future in as_completed(futures):
                try:
                    future.result()  # Raises exception if the call failed
                except Exception as e:
                    logging.error(f"Error while processing vehicle data: {str(e)}")
                    # Handle the exception, e.g., retry or log to slack
                    if slack_notifier:
                        slack_notifier.send_message(message=f"Error occurred: {str(e)}",
                                                    channel_id=settings.SLACK_CHANNEL)
