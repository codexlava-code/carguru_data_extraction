import logging, json
from typing import List, Set, Optional

from bs4 import BeautifulSoup
from pydantic import HttpUrl
from memoization import cached,CachingAlgorithmFlag

from app.config.config import settings
from app.utils.slack_notifier import SlackClient
from app.api.dealerhip_data import DealershipDataAPI
from app.models.schemas import DealershipData, Dealership, DealershipDetails

class DealershipScraper:
    """
    This class provides functionalities to manage and scrape dealership data. It includes methods
    for loading dealership information from files, fetching and posting dealership information to
    an API, and extracting dealership details from HTML data. The class uses caching to optimize
    frequently accessed operations.

    Purpose:
    - Process dealership data from different sources including JSON files, APIs, and web scraping.
    - Perform data transformation and communicate with external APIs for data updates.
    - Provide support for optimized operations through caching.

    Usage:
    - Load dealership data from a local JSON file into data models.
    - Retrieve existing dealership IDs and deduplicate them with new data before posting updates.
    - Extract dealership information from HTML structure for detailed analysis.

    :ivar slack_notifier: Notifier for sending logs or error messages to Slack.
    :type slack_notifier: SlackNotifier
    :ivar logger: Logger instance for recording processes and errors.
    :type logger: logging.Logger
    """
    def __init__(self, ):
        self.slack_notifier = SlackClient()


    @cached(ttl=600, algorithm=CachingAlgorithmFlag.LFU, thread_safe=True)
    def load_dealerships_from_file(self, file_path: str) -> List[Dealership]:
        """
        Load dealership data from a JSON file and parse it into a list of Dealership objects.

        This function reads a JSON file from the provided file path, parses the content,
        and creates instances of Dealership based on the parsed data. The function is
        cached with a TTL of 10 minutes using an LFU caching algorithm. Thread safety
        is also ensured.

        :param file_path: Path to the JSON file containing dealership data.
        :type file_path: str

        :return: A list of Dealership objects parsed from the JSON file.
        :rtype: List[Dealership]
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            dealerships_json = json.load(file)
        return [Dealership(**item) for item in dealerships_json]


    @cached(ttl=300, max_size=1000, algorithm=CachingAlgorithmFlag.LRU, thread_safe=True)
    def get_existing_dealership_ids(self, dealership_data: List[Dealership]) -> Set[str]:
        """
        Retrieves the set of existing dealership IDs from the DealershipDataAPI, filtered by their availability.

        This function leverages in-memory caching with an LRU (Least Recently Used)
        algorithm to improve performance when repeatedly fetching dealership IDs.
        The caching parameters, such as time-to-live (TTL) and maximum cache size,
        are configured to reduce redundant network calls to the DealershipDataAPI.

        :param slack_obj: A Slack client instance used to access dealership data.
        :type slack_obj: SlackClient

        :return: A set containing IDs of all existing dealerships retrieved through the
            DealershipDataAPI.
        :rtype: Set[str]
        """
        return {dealership.id for dealership in dealership_data if dealership.id}


    def post_new_dealerships(self, dealerships: List[Dealership],existing_ids: Set[str]) -> List[bool]:
        """
        Post new dealerships to the API and track their posting results.

        This function iterates through a given list of dealerships. For each dealership that
        does not have its ID in the provided `existing_ids` set, it attempts to post the
        dealership's information using a relevant API. Dealerships with IDs already in the
        `existing_ids` set are skipped. The function records success or failure for each
        post attempt in a results list, which it finally returns.

        :param slack_obj: The SlackClient object used to manage Slack-related communication
          or notifications during posting.
        :type slack_obj: SlackClient
        :param dealerships: A list of dealership objects to be posted.
        :type dealerships: List[Dealership]
        :param existing_ids: A set of dealership IDs that already exist and should therefore
          not be re-posted.
        :type existing_ids: Set[str]
        :return: A list of booleans indicating the result of each dealership posting attempt,
          where `True` represents successful posting and `False` represents a failed or
          skipped operation.
        :rtype: List[bool]
        """
        post_results = []
        for dealership in dealerships:
            if dealership.id not in existing_ids:
                result = DealershipDataAPI.post_dealership(self.slack_notifier, [dealership])
                post_results.append(result)
                logging.info(f"Posted {dealership.name} (ID: {dealership.id}): Success = {result}")
            else:
                logging.error(f"Skipped {dealership.name} (ID: {dealership.id}) as it already exists.")
                post_results.append(False)

        return post_results


    @cached(ttl=180, max_size=500, algorithm=CachingAlgorithmFlag.FIFO, thread_safe=True)
    def fetch_dealership_data(self) -> List[DealershipData]:
        """
        Fetches dealership data and processes it to create a list of `DealershipData` objects.

        This function interacts with external APIs and local files to retrieve, post, and
        process dealership information. It utilizes caching for efficient repeated access.
        Raw dealership data is fetched from an external API, while new dealership data may
        be loaded from a local file and posted to a system. The result is a consolidated list
        of dealership information ready for further use.

        :cached: This function is cached with the following parameters:
            - ttl=180 (time-to-live in seconds)
            - max_size=500 (maximum size of the cache)
            - algorithm=CachingAlgorithmFlag.FIFO (First-In-First-Out eviction policy)
            - thread_safe=True (ensures thread safety in a multithreaded environment)

        :return: A list of `DealershipData` objects containing processed dealership information.
        :rtype: List[DealershipData]
        """
        dealership_data = DealershipDataAPI.get_dealership(self.slack_notifier)

        # # get existing dealership id
        # existing_ids = self.get_existing_dealership_ids(dealership_data)
        #
        # #Load dealerships from file
        # dealerships_to_post = self.load_dealerships_from_file(settings.DEALERSHIP_FILE_PATH)
        #
        # #Post new dealerships
        # post_results = self.post_new_dealerships(dealerships_to_post, existing_ids)

        dealerships = [
            DealershipData(
                dealership_id=dealer.id,
                inventory_source_id=dealer.inventory_source_id,
                dealership_name=dealer.name,
                url=dealer.inventory_source.url,
                category=dealer.inventory_source.category
            ) for dealer in dealership_data
        ]

        return dealerships

    @cached(ttl=3600, max_size=100, algorithm=CachingAlgorithmFlag.LRU, thread_safe=True)
    def extract_dealership_data(self, soup_data: BeautifulSoup, url: HttpUrl, dealership_name: str) -> Optional[DealershipDetails]:
        """
        Extracts dealership data from the provided BeautifulSoup object, URL, and dealership name.

        This method processes the content of a dealership web page represented as a BeautifulSoup
        object to extract and populate data into a `DealershipDetails` object. It attempts to
        retrieve information such as title, link, address, phone, hours of operation, and logo
        from the provided HTML structure.

        :param soup_data: Parsed HTML document of the dealership web page.
        :type soup_data: BeautifulSoup
        :param url: Fully qualified URL of the dealership.
        :type url: HttpUrl
        :param dealership_name: Name of the dealership for identification and logging.
        :type dealership_name: str
        :return: An instance of `DealershipDetails` containing the extracted data, or `None` if an error occurs.
        :rtype: Optional[DealershipDetails]
        :raises Exception: When any issue occurs during the extraction process, logs the error
                           and optionally notifies via a Slack channel if configured.
        """
        try:
            data = DealershipDetails(
                title=(soup_data.select_one("div.dealerDetailsHeader h1.dealerName").get_text(strip=True)
                       if soup_data.select_one("div.dealerDetailsHeader h1.dealerName") else None),
                link=(soup_data.select_one("p.dealerWebLinks a").get_text(strip=True)
                      if soup_data.select_one("p.dealerWebLinks a") else None),
                address=(' '.join(
                    soup_data.select_one('div.dealerDetailsInfo').find_all(string=True, recursive=False)).strip()
                         if soup_data.select_one('div.dealerDetailsInfo') else None),
                phone=(soup_data.select_one("span.dealerSalesPhone").get_text(strip=True)
                       if soup_data.select_one("span.dealerSalesPhone") else None),
                hours_operation=(soup_data.select_one("div.dealerText").get_text(strip=True)
                                 if soup_data.select_one("div.dealerText") else None),
                logo=(soup_data.select_one("div.dealerLogo img").get("src")
                      if soup_data.select_one("div.dealerLogo img") else None)
            )
            logging.info(f"Successfully extracted dealership data for {dealership_name} from URL {url}")

            return data
        except Exception as e:
            error_message = (
                f"Error❌: Extracting Dealership Details {dealership_name}, URL: {url},ERROR: {str(e)}"
            )
            logging.error(error_message)
            if self.slack_notifier:
                self.slack_notifier.send_message(
                    message=error_message,
                    channel_id=settings.SLACK_CHANNEL
                )
            return None

