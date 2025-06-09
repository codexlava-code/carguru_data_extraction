import json

from win32trace import flush

from main import MyFramework
from app.config.config import settings
from app.src.carguru_dealership.dealership_scraper import DealershipScraper
from app.src.carguru_vehicle.vehicle_scraper import VehicleScraper
from app.utils.utils import Utils
import logging

app = MyFramework()


# Add a simple middleware for logging requests.
def log_requests(path, method, data):
    print(f"Received {method} request at {path} with data: {data}")


app.add_middleware(log_requests)


@app.route('/scrape', methods=['GET'])
def scrape_run(request_data):
    logging.info("Scraper API job started.")
    dealership_obj = DealershipScraper()
    dealerships_list = dealership_obj.fetch_dealership_data()
    vehicle_obj = VehicleScraper()
    dealerships_data, vehicle_data = vehicle_obj.handle_scraping(dealerships_list, dealership_obj)
    Utils.save_to_csv(vehicle_data, settings.RESOURCES_VEHICLE)
    return {
            "message": len(vehicle_data) if vehicle_data else 0,
            "status": 200,
            "timestamp": Utils.get_current_timestamp(),
            "version": "1.0",
            "service": "CarGuru Scraper API"
        }


@app.route('/scrape/<task>', methods=['GET'])
def scrape_task(data, task):
    """Run a specific scraping task by name."""

    logging.info(f"Scraper API job for task `{task}` started.")
    if task == "dealership":
        dealership_obj = DealershipScraper()
        data = dealership_obj.fetch_dealership_data()
        return {"status": "dealership complete", "count": len(data) if data else 0}
    elif task == "vehicle":
        dealership_obj = DealershipScraper()
        dealerships_list = dealership_obj.fetch_dealership_data()
        vehicle_obj = VehicleScraper()
        dealerships_data, vehicle_data = vehicle_obj.handle_scraping(dealerships_list, dealership_obj)
        Utils.save_to_csv(vehicle_data, settings.RESOURCES_VEHICLE)
        return {"status": "vehicle done", "records": len(vehicle_data) if vehicle_data else 0}
    else:
        return {"error": "unknown task"}


@app.route("/", methods=["GET"])
def index(request_data):
    # setup_logging()
    print("hello this is me dfsd")
    logging.info("hello this is me fsdfsdf")
    return {
        "message": "Welcome Home! apdfsdi",
        "status": 200,
        "timestamp": Utils.get_current_timestamp(),
        "version": "1.0",
        "service": "CarGuru Scraper API"
    }
