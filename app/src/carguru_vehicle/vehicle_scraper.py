import time, logging, random
from math import ceil

from bs4 import BeautifulSoup
from typing import List, Optional
from urllib.parse import urljoin

from concurrent.futures import ThreadPoolExecutor, as_completed

from memoization import cached, CachingAlgorithmFlag

from app.config.config import settings
from app.src.carguru_vehicle.vehicle_data_extraction import VehicleDataExtraction
from app.utils.slack_notifier import SlackClient
from app.config.web_driver import webdriver_pool
from app.api.vehicle_data import VehicleDataAPI
from app.src.carguru_dealership.dealership_scraper import DealershipScraper
from app.src.carguru_vehicle.vehicle_data_processing import VehicleDataProcessing
from app.models.schemas import (
    DealershipDetails,VehicleDetails, VehicleData,DealershipData
)

class VehicleScraper:
    def __init__(self):
        self.slack_notifier = SlackClient()


    def safe_vehicle_process(self, url: str, dealership: DealershipData, extractor: VehicleDataExtraction) -> Optional[DealershipData]:
        retries = 3
        for attempt in range(retries):
            try:
                return extractor.process_vehicle_data(url, dealership)
            except Exception as e:
                logging.warning(f"[Retry {attempt + 1}] Failed to process {url}: {e}")
                time.sleep(random.uniform(1, 2))
        return None


    @cached(ttl=120, max_size=1000, algorithm=CachingAlgorithmFlag.LRU, thread_safe=True)
    def handle_scraping(self, dealerships: List[DealershipData], dealership_obj: DealershipScraper) -> []:
        vehicle_output_data = []
        dealership_data = []

        def scraper_web_data(dealership: DealershipData, retries=settings.MAX_RETRY_ATTEMPTS):
            vehicle_data = []
            try:
                # Try to scrape the dealership, retrying if necessary
                attempt = 0
                while attempt < retries:
                    try:
                        with webdriver_pool.get_driver() as driver:
                            driver.get(str(dealership.url))  # Load dealership URL
                            soup_data = BeautifulSoup(driver.page_source, "lxml")

                            # dealership_details = dealership_obj.extract_dealership_data(soup_data, dealership.url,
                            #                                                             dealership.dealership_name)
                            #
                            # dealership_data.append({
                            #     "dealership_name": dealership.dealership_name,
                            #     "data": dealership_details
                            # })

                            # Process vehicle links
                            vehicle_extractor_obj = VehicleDataExtraction()
                            vehicle_nav_links = vehicle_extractor_obj.get_all_vehicle_links(soup_data, dealership)

                            # # Scrape vehicle data concurrently
                            with ThreadPoolExecutor(max_workers=min(5, settings.MAX_THREAD)) as vehicle_executor:
                                futures = {
                                    vehicle_executor.submit(
                                        self.safe_vehicle_process,
                                        url,
                                        dealership,
                                        vehicle_extractor_obj
                                    ): url for url in vehicle_nav_links
                                }

                                for future in as_completed(futures):
                                    vehicle_url = futures[future]
                                    try:
                                        result = future.result(timeout=60)
                                        if result:
                                            vehicle_data.append(result)
                                    except Exception as err:
                                        logging.error(f"Error processing vehicle {vehicle_url}: {str(err)}")

                            return vehicle_data
                    except Exception as err:
                        logging.error(f"Error scraping dealership {dealership.dealership_name}: {str(err)}")
                        attempt += 1
                        if attempt == retries:
                            raise Exception(
                                f"Failed scraping {dealership.dealership_name} after {retries} attempts")
                        time.sleep(random.uniform(3, 7))  # Random delay before retry

            except Exception as e:
                logging.exception(f"Error scraping dealership {dealership.dealership_name}: {e}")

            return vehicle_data

        # Use thread pool to handle multiple dealerships concurrently
        with ThreadPoolExecutor(max_workers=min(5, settings.MAX_THREAD)) as dealership_executor:
            futures = {
                dealership_executor.submit(scraper_web_data, dealership): dealership
                for dealership in dealerships
            }

            for future in as_completed(futures):
                result = future.result()
                if result:
                    vehicle_output_data.extend(result)

        return [dealership_data, vehicle_output_data]


    def process_vehicle_data_post(self, new_vehicle_data: List[dict]) -> None:

        # get exist vehicle data
        exist_vehicle_data = VehicleDataAPI.get_vehicle(self.slack_notifier)

        # Remove duplicates
        filtered_records = [
            data
            for data in new_vehicle_data
            if not VehicleDataProcessing.is_duplicate_vehicle_data(exist_vehicle_data, data)
        ]

        total_records = len(filtered_records)
        chunk_size = settings.SEND_BATCH_SIZE
        total_batches = ceil(total_records / chunk_size)

        logging.info(
            f"🚀 Total records after filtering: {total_records}, Batch size: {chunk_size}, Total batches: {total_batches}"
        )

        for batch_number in range(total_batches):
            start_idx = batch_number * chunk_size
            end_idx = start_idx + chunk_size
            current_batch = filtered_records[start_idx:end_idx]

            logging.info(
                f"📦 Starting batch {batch_number + 1}/{total_batches}, "
                f"records {start_idx + 1}-{min(end_idx, total_records)}"
            )

            VehicleDataProcessing.process_batch(current_batch, self.slack_notifier)

            logging.info(f"📤 Completed batch {batch_number + 1}/{total_batches}")

        logging.info("🏅 All batches processed successfully.")
