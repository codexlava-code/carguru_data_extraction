import logging, os, json, pandas as pd

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from datetime import datetime

from app.api.dealerhip_data import DealershipData
from app.config.config import settings
from app.api.vehicle_data import VehicleData
from app.utils.slack_notifier import SlackClient
from app.models.models import Dealership
from app.src.scraper import VehicleScraper

# load the dotenv file
load_dotenv()

def setup_logging():
    logging.basicConfig(
        filename="app/logs/app.log",
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def main():
    setup_logging()
    logging.info("Scraper job started.")
    slack_obj = SlackClient()  # Initialize actual Slack object here

    dealerships_json = DealershipData.get_dealership(slack_obj)

    dealerships = [Dealership(
        dealership_id=d["id"],
        inventory_source_id=d["inventory_source_id"],
        dealership_name=d["name"],
        url=d["inventory_source"]["url"],
        category=d["inventory_source"]["category"]
    ) for d in dealerships_json]
    # print(dealerships)
    scraper = VehicleScraper(slack_obj)

    vehicle_output_data = []
    dealership_data = []
    vehicle_navigation_list = []

    with settings.init_driver() as driver:
        for dealership in dealerships:
            print(dealership.url)
            driver.get(dealership.url)
            soup_data = BeautifulSoup(driver.page_source, "lxml")

            # Get the dealership details information
            # dealership_details = scraper.extract_dealership_data(soup_data, dealership.url, dealership.dealership_name)
            # dealership_data.append({
            #     "dealership_name":dealership.dealership_name,
            #     "data":dealership_details
            # })

            # Get the vehicle link list
            vehicle_navigation_links = scraper.get_all_vehicle_links(soup_data, dealership)
            # vehicle_navigation_list.append(vehicle_navigation_links)
            print(len(vehicle_navigation_links))
            # Get the vehicle data from vehicle url page
            with ThreadPoolExecutor(settings.MAX_THREAD) as executor:
                futures = {executor.submit(scraper.process_vehicle_data,url, dealership): url
                           for url in vehicle_navigation_links}

                # Collect results as they complete
                for future in as_completed(futures):
                    vehicle_url = futures[future]

                    try:
                        result = future.result()  # Get the result of the scraping function
                        if result:
                            # print(f"vehicle data{result}")
                            vehicle_output_data.append(result)

                    except Exception as e:
                        error_message = (
                            f"Error❌: Process Vehicle Data, URL: {vehicle_url}, DEALERSHIP: {dealership.dealership_name}, "
                            f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ERROR: {str(e)}"
                        )
                        slack_obj.send_message(
                            message=error_message,
                            channel_id=settings.SLACK_CHANNEL
                        )
                        logging.error(error_message)

    # print(json.dumps(vehicle_output_data))

    # Save vehicle output data to csv
    path_to_csv = "app/resources/cargurus_cars_data.csv"
    df = pd.DataFrame(vehicle_output_data)
    df.to_csv(path_to_csv, index=False)

    # # read vehicle output data to csv
    df = pd.read_csv(path_to_csv)
    vehicle_output_data_csv = df.to_dict(orient="records")

    vehicle_existing_data = VehicleData.get_vehicle(slack_obj)
    scraper.process_and_send_batches(vehicle_existing_data, vehicle_output_data_csv, slack_obj)

    logging.info("Scraper job finished successfully.")


if __name__ == '__main__':
    main()

