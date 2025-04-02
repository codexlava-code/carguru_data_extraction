import time, os, urllib.parse, logging, json
from datetime import datetime
from random import randint
from math import ceil
from bs4 import BeautifulSoup
from typing import List

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from app.config.config import settings
from app.models.models import Vehicle
from app.api.vehicle_data import VehicleData

class VehicleScraper:
    def __init__(self, slack_obj=None):
        """Initialize Slack client with bot token and signing secret."""
        self.slack_notifier = slack_obj


    def extract_dealership_data(self, soup_data, url, dealership_name):
        try:
            title = soup_data.find("div", class_="dealerDetailsHeader").find("h1", class_="dealerName").get_text(
                strip=True) if \
                (soup_data.find("div", class_="dealerDetailsHeader").find("h1", class_="dealerName")) else None
            address = ' '.join(
                soup_data.find('div', class_='dealerDetailsInfo').find_all(string=True, recursive=False)).strip() if \
                (soup_data.find('div', class_='dealerDetailsInfo').find_all(string=True, recursive=False)) else None
            link = soup_data.find("p", class_="dealerWebLinks").find("a").get_text(strip=True) if \
                (soup_data.find("p", class_="dealerWebLinks").find("a")) else None
            phone = soup_data.find("span", class_="dealerSalesPhone").get_text(strip=True) if \
                (soup_data.find("span", class_="dealerSalesPhone")) else None
            hours_operation = soup_data.find("div", class_="dealerText").get_text(strip=True) if \
                (soup_data.find("div", class_="dealerText")) else None
            logo = soup_data.find("div", class_="dealerLogo").find("img").get("src") if \
                (soup_data.find("div", class_="dealerLogo").find("img")) else None

            data = {
                "title": title,
                "link": link,
                "address": address,
                "phone": phone,
                "hours_operation": hours_operation,
                "logo": logo,
            }
            # self.slack_notifier.slack_obj.send_message(
            #     message=f"Success✅: Extracted Dealership Details: NAME: {dealership_name}, URL: {url}, TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            #     channel_id=settings.SLACK_CHANNEL
            # )
            logging.info(f"Successfully extracted dealership data for {dealership_name} from URL {url}")

            return data
        except Exception as e:
            error_message = (
                f"Error❌: Extracting Dealership Details: NAME: {dealership_name}, URL: {url}, "
                f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ERROR: {str(e)}"
            )
            self.slack_notifier.slack_obj.send_message(
                message=error_message,
                channel_id=settings.SLACK_CHANNEL
            )
            logging.error(error_message)
            return None


    def extract_vehicle_links(self, soup_data: BeautifulSoup, base_url: str) -> List[str]:
        vehicle_links = []
        for a_tag in soup_data.find_all('a', {'data-testid': 'car-blade-link'}):
            if a_tag and a_tag.get('href'):
                href = a_tag.get('href')
                full_url = urllib.parse.urljoin(base_url, href)
                vehicle_links.append(full_url)
        return vehicle_links


    def get_total_pages(self, soup_data):
        try:
            span_text = soup_data.find("span", string=lambda text: text and "Page" in text)
            if span_text:
                parts = span_text.text.split()
                if len(parts) >= 4 and parts[-1].isdigit():
                    return int(parts[-1])
        except Exception as e:
            logging.error(f"Error extracting total pages: {e}")
        return 1


    def get_all_vehicle_links(self, soup_data, dealership):
        try:
            max_pages = self.get_total_pages(soup_data)
            logging.info(f"Detected {max_pages} total pages at {dealership.url}")

            all_vehicle_links = []
            for page_num in range(1, max_pages + 1):
                page_url = f"{dealership.url}#resultsPage={page_num}"
                print(f"Getting vehicle links from page {page_url} of {max_pages}...")

                try:
                    with settings.init_driver() as driver:
                        driver.get(page_url)
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )  # Wait until the body tag is loaded

                        soup = BeautifulSoup(driver.page_source, "lxml")

                        vehicle_links = self.extract_vehicle_links(soup, dealership.url)

                        if not vehicle_links:
                            message = "No vehicle links found on this page. Stopping..."
                            logging.warning(message)
                            self.slack_notifier.send_message(
                                message=message,
                                channel_id=settings.SLACK_CHANNEL
                            )
                            break

                        all_vehicle_links.extend(vehicle_links)
                        logging.info(f"Found {len(vehicle_links)} links on Page {page_num}")

                except Exception as e:
                    err_message = (
                        f"Error❌ extracting Vehicle Navigation URL, NAME: {dealership.dealership_name}, "
                        f"URL: {page_url}, TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ERROR: {str(e)}"
                    )
                    self.slack_notifier.send_message(
                        message=err_message,
                        channel_id=settings.SLACK_CHANNEL
                    )
                    logging.error(err_message)

            return all_vehicle_links

        except Exception as e:
            err_message = (
                f"Error❌ extracting dealership navigation, NAME: {dealership.dealership_name}, "
                f"URL: {dealership.url}, TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ERROR: {str(e)}"
            )
            self.slack_notifier.send_message(
                message=err_message,
                channel_id=settings.SLACK_CHANNEL
            )
            logging.error(err_message)


    def extract_vehicle_data(self, soup_data, vehicle_url, dealership):
        """ Extract vehicle data from details page"""
        # title = soup_data.find("div", class_="_titleInfo_uw1k0_49").find("h4").get_text(strip=True) if \
        #     (soup_data.find("div", class_="_titleInfo_uw1k0_49").find("h4")) else None
        try:
            # Features data
            features_data = soup_data.find_all("li", class_="_listItem_1tanl_14") or []
            # Dictionary to store extracted data
            feature_details = {}
            for data in features_data:
                key = None
                value = None
                if data.find("h5"):  # Ensure the <h5> tag exists
                    key = data.find("h5").get_text(strip=True).replace(" ", "_").lower()
                if data.find("p"):  # Ensure the <p> tag exists
                    value = data.find("p").get_text(strip=True)
                if key and value:
                    feature_details[key] = value

            # # # extract dl data to dt
            records_container = soup_data.find("div", class_="_records_1vyus_9", attrs={"data-cg-ft": "listing-vdp-stats"})
            dt_tags = records_container.find("ul").find_all("li") if (
                    records_container and records_container.find("ul")) else []

            overview_details = {}
            for dt_tag in dt_tags:
                key = None
                value = None
                if dt_tag.find("span", class_="_label_zbkq7_7"):  # Check if the key exists
                    key = (
                        dt_tag.find("span", class_="_label_zbkq7_7")
                        .get_text(strip=True)
                        .replace(":", "")
                        .replace(" ", "_")
                        .lower()
                    )
                if dt_tag.find("span", class_="_value_zbkq7_14"):  # Check if the value exists
                    value = dt_tag.find("span", class_="_value_zbkq7_14").get_text(strip=True)
                if key and value:
                    overview_details[key] = value

            # Parse and build the data dictionary

            data = {
                    "dealership_id": dealership.dealership_id,
                    "vin": overview_details.get("vin"),
                    "mileage": int(feature_details.get("mileage").replace(",", "")) if feature_details.get(
                        "mileage") else None,
                    "stock_number": overview_details.get("stock_number"),
                    "description": "",
                    "exterior_color": overview_details.get("exterior_color"),
                    "interior_color": overview_details.get("interior_color"),
                    "model": {
                        "name": overview_details.get("model"),
                        "year": overview_details.get("year"),
                        "trim": overview_details.get("trim"),
                        "body_style": overview_details.get("body_type"),
                        "transmission": feature_details.get("transmission"),
                        "fuel_type": feature_details.get("fuel_type"),
                        "drivetrain": feature_details.get("drivetrain"),
                        "engine": feature_details.get("engine"),
                        "make": {
                            "name": overview_details.get("make"),
                        },
                    },
            }
            return data
        except Exception as e:
            error_message = f"Data construction error 💥 URL: {vehicle_url}, ERROR: {str(e)}"
            self.slack_notifier.send_message(
                message=error_message,
                channel_id=settings.SLACK_CHANNEL
            )
            logging.error(error_message)
            return None

    def process_vehicle_data(self, vehicle_url, dealership):
            try:
                with settings.init_driver() as driver:
                    # Introduce a random delay before loading the page
                    time.sleep(randint(*(2, 5)))

                    driver.get(vehicle_url)
                    WebDriverWait(driver, 20).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.CLASS_NAME, "_dealInfo_uw1k0_70")),
                            EC.presence_of_element_located((By.CLASS_NAME, "_listItem_1tanl_14")),
                            EC.presence_of_element_located((By.CLASS_NAME, "_records_1vyus_9")),
                        )
                    )
                    soup_data = BeautifulSoup(driver.page_source, 'lxml')

                    # Extract detailed vehicle information
                    detailed_vehicle_data = self.extract_vehicle_data(soup_data, vehicle_url, dealership)
                    if detailed_vehicle_data is None:
                        raise ValueError("Vehicle detailed data extraction returned None")

                    # price
                    price_section = soup_data.find("div", class_="_dealInfo_uw1k0_70")
                    price = None  # Default to None if price is not found
                    if price_section and price_section.find("h5", class_="WoAzt"):
                        price = price_section.find("h5", class_="WoAzt").get_text(strip=True).replace("$", "").replace(",","")


                    final_vehicle_data = Vehicle(
                        inventory_source_id=dealership.inventory_source_id,
                        listing_url=vehicle_url,
                        status="available",
                        price=float(price) if price else None,  # Gracefully handle None price,
                        vehicle_data=detailed_vehicle_data if detailed_vehicle_data else None,
                    ).__dict__

                    # print(json.dumps(final_vehicle_data, indent=1))
                # success_message = (
                #     f"Success✅: Extracted Vehicle Data "
                #     f"VIN: {vin}, URL: {url}, DEALERSHIP: {dealership.dealership_name}, "
                #     f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                # )
                # self.slack_notifier.send_message(
                #     message=success_message,
                #     channel_id=settings.SLACK_CHANNEL
                # )
                # logging.info(success_message)

                return final_vehicle_data

            except Exception as e:
                error_message = (
                    f"Error❌: Extracting Vehicle Data, URL: {vehicle_url}, DEALERSHIP: {dealership.dealership_name}, "
                    f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ERROR: {str(e)}"
                )
                self.slack_notifier.send_message(
                    message=error_message,
                    channel_id=settings.SLACK_CHANNEL
                )
                logging.error(error_message)
                return None

            finally:
                success_message = (
                    f"Success✅: Extracted Vehicle Data Driver Closed "
                    f"VIN: {vehicle_url}, URL: {vehicle_url}, DEALERSHIP: {dealership.dealership_name}, "
                    f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                self.slack_notifier.send_message(
                    message=success_message,
                    channel_id=settings.SLACK_CHANNEL
                )
                logging.info(success_message)
                driver.quit()

    def is_duplicate_vehicle_data(self, existing_records, new_entry):
        try:
            for record in existing_records:
                if record.get("listing_url") == new_entry.get("listing_url"):
                    raise ValueError(
                        f"Duplicate found:  URL: {new_entry.get('listing_url')}")
            return False

        except ValueError as ve:
            print(f"Error duplicate data: {ve}")
            error_message = (
                f"Error❌: Duplicate vehicle data, "
                f"URL: {new_entry.get('listing_url')},"
                f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, "
                f"ERROR: {str(ve)}"
            )
            self.slack_notifier.send_message(
                message=error_message,
                channel_id=settings.SLACK_CHANNEL
            )
            logging.error(error_message)
            return True

    def process_and_send_batches(self,vehicle_existing_data, vehicle_output_data, slack_obj):
        non_duplicates = [
            item for item in vehicle_output_data
            if not self.is_duplicate_vehicle_data(vehicle_existing_data, item)
        ]
        # print(f"Filtered {len(vehicle_output_data) - len(non_duplicates)} duplicate records.")

        logging.info(f"Filtered {len(vehicle_output_data) - len(non_duplicates)} duplicate records.")
        total_records = len(non_duplicates)
        total_batches = ceil(total_records / settings.SEND_BATCH_SIZE or None)

        for batch_number in range(total_batches):
            start_idx = batch_number * settings.SEND_BATCH_SIZE
            end_idx = min(start_idx + settings.SEND_BATCH_SIZE, total_records)
            batch_data = [data for data in non_duplicates[start_idx:end_idx]]
            print(batch_data)
            logging.info(f"Sending Batch {batch_number + 1}/{total_batches} (Records {start_idx + 1}-{end_idx})")

            for data in batch_data:
                attempt = 0
                success = False
                while attempt < settings.MAX_RETRY_ATTEMPTS and not success:
                    success = VehicleData.post_vehicle_data(self.slack_notifier, data)
                    attempt += 1
                    if not success:
                        logging.warning(f"Retrying... Attempt {attempt}/{settings.MAX_RETRY_ATTEMPTS}")
                        time.sleep(2)

                if not success:
                    logging.error(f"Failed to send batch starting at record {start_idx + 1}")

