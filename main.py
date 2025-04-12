import logging
from dotenv import load_dotenv

from app.config.config import settings
from app.src.carguru_dealership.dealership_scraper import DealershipScraper
from app.src.carguru_vehicle.vehicle_scraper import VehicleScraper
from app.utils.utils import Utils

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


def main():
    """Main entry point of the scraper module."""
    setup_logging()
    logging.info("Scraper job started.")

    # Get Dealership Data
    dealership_obj = DealershipScraper()
    dealerships_list = dealership_obj.fetch_dealership_data()

    # Get Vehicle Data
    vehicle_obj = VehicleScraper()
    dealerships_data, vehicle_data = vehicle_obj.handle_scraping(dealerships_list, dealership_obj)


    # save dealership data
    # Utils.save_to_csv(dealerships_data, settings.RESOURCES_DEALERSHIP)

    # Save vehicle data
    Utils.save_to_csv(vehicle_data, settings.RESOURCES_VEHICLE)

    # Read vehicle data
    # vehicle_output_data_csv = Utils.read_from_csv(settings.RESOURCES_VEHICLE)
    #
    # # Process the vehicle data to send API
    # vehicle_obj.process_vehicle_data_post(vehicle_output_data_csv)

    logging.info("✅ Scraper job finished successfully.\n\n")


if __name__ == '__main__':
    main()

