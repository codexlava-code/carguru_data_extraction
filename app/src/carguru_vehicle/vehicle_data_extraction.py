import logging
import random
import time
from typing import List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pydantic import HttpUrl
from memoization import cached,CachingAlgorithmFlag
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.config.config import settings
from app.models.schemas import DealershipData, VehicleDetails, Model, Make, VehicleData
from app.config.web_driver import webdriver_pool
from app.utils.slack_notifier import SlackClient


class VehicleDataExtraction:
    def __init__(self, ):
        self.slack_notifier = SlackClient()

    @cached(ttl=3600, max_size=500, algorithm=CachingAlgorithmFlag.LRU, thread_safe=True)
    def extract_vehicle_links_on_page(self, soup_data: BeautifulSoup, base_url: HttpUrl) -> List[str]:
        vehicle_links = [urljoin(str(base_url), tag['href'])
                         for tag in soup_data.find_all('a',
                                                       {'data-testid': 'car-blade-link'},
                                                       href=True) if tag]
        logging.debug(f"Extracted {len(vehicle_links)} carguru_vehicle links.")
        return vehicle_links


    @staticmethod
    @cached(ttl=3600, max_size=100, algorithm=CachingAlgorithmFlag.LRU, thread_safe=True)
    def get_total_pages(soup_data: BeautifulSoup) -> int:
        span_text = soup_data.find("span", string=lambda text: text and "Page" in text)
        if span_text:
            parts = span_text.text.split()
            if len(parts) >= 4 and parts[-1].isdigit():
                return int(parts[-1])
        return 1


    def get_all_vehicle_links(self, soup_data: BeautifulSoup, dealership: DealershipData) -> List[str]:
        all_vehicle_links = []
        total_pages = self.get_total_pages(soup_data)

        logging.info(f"Detected {total_pages} total pages for dealership:"
                     f" {dealership.dealership_name}")

        for page_num in range(1, total_pages + 1):
            page_url = f"{dealership.url}#resultsPage={page_num}"
            logging.info(f"Processing page {page_num} of {total_pages}: {page_url}")

            try:
                with webdriver_pool.get_driver() as driver:
                    # Random delay to mitigate detection or rate-limiting
                    sleep_duration = random.uniform(1, 2)
                    time.sleep(sleep_duration)

                    driver.get(str(page_url))

                    soup_data = BeautifulSoup(driver.page_source, "lxml")
                    vehicle_links_on_page = self.extract_vehicle_links_on_page(soup_data, dealership.url)

                    if not vehicle_links_on_page:
                        message = f"No carguru_vehicle links found on page {page_num}, stopping further processing."
                        logging.warning(message)
                        if self.slack_notifier:
                            self.slack_notifier.send_message(
                                message=message,
                                channel_id=settings.SLACK_CHANNEL
                            )
                        break

                    all_vehicle_links.extend(vehicle_links_on_page)
                    logging.info(f"Found {len(vehicle_links_on_page)} links on Page {page_num}")

            except Exception as exc:
                error_message = (
                    f"Error extracting carguru_vehicle links for dealership '{dealership.dealership_name}', "
                    f"URL: {page_url}, Error: {str(exc)}"
                )
                logging.error(error_message)
                if self.slack_notifier:
                    self.slack_notifier.send_message(
                        message=error_message,
                        channel_id=settings.SLACK_CHANNEL
                    )

        return all_vehicle_links


    @cached(ttl=7200, max_size=1000, algorithm=CachingAlgorithmFlag.LRU, thread_safe=True)
    def extract_vehicle_data(self, soup_data: BeautifulSoup, vehicle_url: HttpUrl, dealership: DealershipData) -> Optional[VehicleDetails]:
        try:
            # Features data
            feature_details = {}
            features_data = soup_data.find_all("li", class_="_listItem_1tanl_14") or []
            for data in features_data:
                key_tag = data.find("h5")
                value_tag = data.find("p")

                key = key_tag.get_text(strip=True).replace(" ", "_").lower() if key_tag else None
                value = value_tag.get_text(strip=True) if value_tag else None
                if key:
                        feature_details[key] = value

            # Overview data
            overview_details = {}
            records_container = soup_data.find(
                "div", class_="_records_1vyus_9", attrs={"data-cg-ft": "listing-vdp-stats"}
            )
            dt_tags = records_container.find("ul").find_all("li") if (
                    records_container and records_container.find("ul")) else []

            for dt_tag in dt_tags:
                key_tag = dt_tag.find("span", class_="_label_zbkq7_7")
                value_tag = dt_tag.find("span", class_="_value_zbkq7_14")

                key = (
                    key_tag.get_text(strip=True)
                    .replace(":", "")
                    .replace(" ", "_")
                    .lower()
                    if key_tag else None
                )
                value = value_tag.get_text(strip=True) if value_tag else None
                if key:
                        overview_details[key] = value

            # Parse and build the data dictionary
            vehicle_data = VehicleDetails(
                    dealership_id=dealership.dealership_id,
                    vin=overview_details.get("vin"),
                    mileage=int(feature_details['mileage'].replace(",", "")) if
                        "mileage" in feature_details else None,
                    stock_number=overview_details.get("stock_number"),
                    description="",
                    exterior_color=overview_details.get("exterior_color"),
                    interior_color=overview_details.get("interior_color"),
                    model=Model(
                        name=overview_details.get("model"),
                        year=overview_details.get("year"),
                        trim=overview_details.get("trim"),
                        body_style=overview_details.get("body_type"),
                        transmission=feature_details.get("transmission"),
                        fuel_type=feature_details.get("fuel_type"),
                        drivetrain=feature_details.get("drivetrain"),
                        engine=feature_details.get("engine"),
                        make=Make(
                            name=overview_details.get("make")
                        )
                    )
            )
            return vehicle_data
        except Exception as e:
            error_message = f"Vehicle Data construction error 💥 URL: {vehicle_url}, ERROR: {str(e)}"
            logging.error(error_message)
            if self.slack_notifier:
                self.slack_notifier.send_message(
                    message=error_message,
                    channel_id=settings.SLACK_CHANNEL
                )
            return None

    def process_vehicle_data(self, vehicle_url: str, dealership: DealershipData) -> Optional[VehicleData]:
            try:
                with webdriver_pool.get_driver() as driver:
                    # Random delay to mitigate detection or rate-limiting
                    sleep_duration = random.uniform(1, 2)
                    logging.info(f"Sleeping {sleep_duration} seconds before accessing {vehicle_url}")
                    time.sleep(sleep_duration)

                    # get driver data
                    driver.get(vehicle_url)
                    webdriver_pool.scroll_incrementally(driver)

                    WebDriverWait(driver, 15).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.CLASS_NAME, "_dealInfo_uw1k0_70")),
                            EC.presence_of_element_located((By.CLASS_NAME, "_listItem_1tanl_14")),
                            EC.presence_of_element_located((By.CLASS_NAME, "_records_1vyus_9")),
                        )
                    )

                    soup_data = BeautifulSoup(driver.page_source, 'lxml')

                    # Extract detailed carguru_vehicle information
                    detailed_vehicle_data = self.extract_vehicle_data(soup_data, vehicle_url, dealership)
                    if detailed_vehicle_data is None:
                        raise ValueError("Vehicle detailed data extraction returned None")

                    # Extract carguru_vehicle price
                    price_section = soup_data.find("div", class_="_dealInfo_uw1k0_70")
                    price = None  # Default to None if price is not found
                    if price_section and price_section.find("h5", class_="WoAzt"):
                        raw_price = price_section.find("h5", class_="WoAzt").get_text(strip=True)
                        if raw_price:
                            price = float(raw_price.replace("$", "").replace(",", "").strip())

                    # Build VehicleData object
                    final_vehicle_data = VehicleData(
                        inventory_source_id=dealership.inventory_source_id,
                        listing_url=vehicle_url,
                        status="available",
                        price=price,
                        vehicle_data=detailed_vehicle_data if detailed_vehicle_data else None,
                    ).model_dump(exclude_none=True)

                    # Successful extraction logging
                    success_message = (
                        f"✅ Successfully extracted carguru_vehicle data for: {dealership.dealership_name}\n"
                        f"URL: {vehicle_url}\n"
                    )
                    logging.info(success_message)
                    # if self.slack_notifier:
                    #     self.slack_notifier.send_message(
                    #         message=success_message,
                    #         channel_id=settings.SLACK_CHANNEL
                    #     )

                    return final_vehicle_data

            except Exception as exc:
                error_message = (
                    f"❌ Error extracting carguru_vehicle data for dealership '{dealership.dealership_name}'\n"
                    f"URL: {vehicle_url}\n"
                    f"Error: {str(exc)}"
                )
                logging.error(error_message)
                if self.slack_notifier:
                    self.slack_notifier.send_message(
                        message=error_message,
                        channel_id=settings.SLACK_CHANNEL
                    )
                return None