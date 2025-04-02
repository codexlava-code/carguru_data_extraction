import time

from pydantic import BaseSettings, Field
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Settings(BaseSettings):
    # API URLs
    VEHICLE_API_URL: str = Field(..., description="Vehicle API URL from environment.")
    DEALERSHIP_API_URL: str = Field(..., description="Dealership API URL from environment.")

    # Slack configurations
    SLACK_BOT_TOKEN: str = Field(..., description="Slack Bot Token from environment.")
    SLACK_SIGNING_SECRET: str = Field(..., description="Slack Signing Secret from environment.")
    SLACK_CHANNEL: str = Field(..., description="Slack Channel ID from environment.")

    # Application behavior with defaults
    MAX_THREAD: int = Field(default=10, description="Maximum number of processing threads.")
    SEND_BATCH_SIZE: int = Field(default=1, description="Batch size of data sent at a time.")
    MAX_RETRY_ATTEMPTS: int = Field(default=2, description="Maximum retry attempts for sending requests.")

    # Selenium configurations
    HEADLESS_MODE: bool = Field(default=True, description="Run Selenium in headless mode")
    PAGE_LOAD_TIMEOUT: int = Field(default=600, description="Timeout for Selenium page loading")

    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"

    @staticmethod
    def scroll_incrementally(driver, pause_time=2, max_scroll_attempts=3):
        """Scroll incrementally and wait for content to load."""
        last_height = driver.execute_script("return document.body.scrollHeight")
        for attempt in range(max_scroll_attempts):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:  # Exit if no new content is loaded
                break
            last_height = new_height

    @staticmethod
    def init_driver():
        options = webdriver.ChromeOptions()

        if settings.HEADLESS_MODE:
            options.add_argument("--headless")  # Run without UI

        # Other Chrome options
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-application-cache")  # Disable caching
        options.add_argument("--incognito")  # Use incognito mode

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
        Settings.scroll_incrementally(driver)
        return driver



settings = Settings()