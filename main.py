import logging, os, json, pandas as pd
from typing import List, Set

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from datetime import datetime

from app.api.dealerhip_data import DealershipDataAPI
from app.config.config import settings
from app.config.web_driver import webdriver_pool, WebDriver
from app.api.vehicle_data import VehicleDataAPI
from app.utils.slack_notifier import SlackClient
from app.models.schemas import DealershipData, Dealership, VehicleData
from app.src.scraper import VehicleScraper

# Load environment variables from .env file
load_dotenv()

def setup_logging():
    logging.basicConfig(
        filename="app/logs/app.log",
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def load_dealerships_from_file(file_path: str) -> List[Dealership]:
    """Load dealership data from JSON file into Pydantic models."""
    with open(file_path, 'r', encoding='utf-8') as file:
        dealerships_json = json.load(file)
    return [Dealership(**item) for item in dealerships_json]


def get_existing_dealership_ids(slack_obj: SlackClient) -> Set[str]:
    """Fetch the current dealership IDs from the API."""
    existing_dealerships = DealershipDataAPI.get_dealership(slack_obj)
    return {dealership.id for dealership in existing_dealerships if dealership.id}

def post_new_dealerships(
        slack_obj: SlackClient,
        dealerships: List[Dealership],
        existing_ids: Set[str]
) -> List[bool]:
    """Post only dealerships whose IDs don't exist."""
    post_results = []
    for dealership in dealerships:
        if dealership.id not in existing_ids:
            result = DealershipDataAPI.post_dealership(slack_obj,[dealership])
            post_results.append(result)
            logging.info(f"Posted {dealership.name} (ID: {dealership.id}): Success = {result}")
        else:
            logging.error(f"Skipped {dealership.name} (ID: {dealership.id}) as it already exists.")
            post_results.append(False)

    return post_results


def fetch_dealership_data(slack_obj: SlackClient) -> List[DealershipData]:
    # Get Dealership
    raw_dealerships = DealershipDataAPI.get_dealership(slack_obj)

    # file_path = 'app/resources/dealership_data.json'

    # Load existing IDs
    # existing_ids = get_existing_dealership_ids(slack_obj)

    # Load dealerships from file
    # dealerships_to_post = load_dealerships_from_file(file_path)

    # Post new dealerships
    # post_results = post_new_dealerships(slack_obj, dealerships_to_post, existing_ids)

    # print(raw_dealerships)

    dealerships = [
        DealershipData(
            dealership_id=dealer.id,
            inventory_source_id=dealer.inventory_source_id,
            dealership_name=dealer.name,
            url=dealer.inventory_source.url,
            category=dealer.inventory_source.category
        ) for dealer in raw_dealerships
    ]

    return dealerships


def handle_scraping(dealerships: List[DealershipData], scraper, slack_obj: SlackClient) -> List[VehicleData]:
    """Scrape vehicle data using concurrent processing."""
    vehicle_output_data = []
    dealership_data = []

    try:
        for dealership in dealerships:
            logging.info(f"Processing dealership: {dealership.dealership_name}")

            with webdriver_pool.get_driver() as driver:
                driver.get(str(dealership.url))

                soup_data = BeautifulSoup(driver.page_source, "lxml")

                #Get the dealership details information
                dealership_details = scraper.extract_dealership_data(soup_data, dealership.url, dealership.dealership_name)

                dealership_data.append({
                    "dealership_name":dealership.dealership_name,
                    "data":dealership_details
                })
                vehicle_nav_links = scraper.get_all_vehicle_links(soup_data, dealership)

            logging.info(f"{len(vehicle_nav_links)} vehicle links found for {dealership.dealership_name}")

            # Concurrent scraping vehicle details
            with ThreadPoolExecutor(max_workers=settings.MAX_THREAD) as executor:
                futures = {
                    executor.submit(scraper.process_vehicle_data, url, dealership): url
                    for url in vehicle_nav_links
                }

                for future in as_completed(futures):
                    vehicle_url = futures[future]
                    try:
                        result = future.result()
                        if result:
                            vehicle_output_data.append(result)
                    except Exception as err:
                        error_message = (
                            f"❌ Error scraping vehicle data.\n"
                            f"URL: {vehicle_url}\n"
                            f"Dealership: {dealership.dealership_name}\n"
                            f"Error: {str(err)}"
                        )
                        logging.error(error_message)
                        if slack_obj:
                            slack_obj.send_message(
                                message=error_message,
                                channel_id=settings.SLACK_CHANNEL
                            )
    finally:
        webdriver_pool.shutdown_pool()
        logging.info("✅ Successfully Web Driver shutdown.")

    return vehicle_output_data

def save_to_csv(data, file_path):
    """Save scraped data to CSV."""
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    logging.info(f"Successfully saved scraped data to {file_path}")


def read_from_csv(file_path):
    """Read vehicle data from CSV."""
    df = pd.read_csv(file_path)
    logging.info(f"Successfully read data from {file_path}")
    return df.to_dict(orient="records")


def main():
    """Main entry point of the scraper module."""
    setup_logging()
    logging.info("Scraper job started.")

    slack_obj = SlackClient()

    scraper = VehicleScraper(slack_obj)

    # dealerships = fetch_dealership_data(slack_obj)
    #
    # vehicle_data = handle_scraping(dealerships, scraper, slack_obj)
    #
    # print(vehicle_data)
    # csv_path = "app/resources/cargurus_cars_data.csv"
    # save_to_csv(vehicle_data, csv_path)

    # vehicle_output_data_csv = read_from_csv(csv_path)
    #
    # vehicle_existing_data = VehicleDataAPI.get_vehicle(slack_obj)
    # scraper.process_and_send_batches(vehicle_existing_data, vehicle_output_data_csv)

    logging.info("✅ Scraper job finished successfully.\n\n")


if __name__ == '__main__':
    main()

