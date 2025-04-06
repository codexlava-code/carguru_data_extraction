import time
from contextlib import contextmanager
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Settings(BaseSettings):
    # API URLs
    VEHICLE_API_URL: str = Field(default="https://retoolapi.dev/75Qs6K/data", description="Vehicle API URL from environment.")
    DEALERSHIP_API_URL: str = Field(default="https://retoolapi.dev/e3CVBf/data", description="Dealership API URL from environment.")

    # Slack configurations
    SLACK_BOT_TOKEN: str = Field(default="xoxb-8104347625139-8544713643409-37Z4UzEIkGpUA5ArzSUx3Wc6", description="Slack Bot Token from environment.")
    SLACK_SIGNING_SECRET: str = Field(default="ecdfd545eac42f98586bb00519ec5df7", description="Slack Signing Secret from environment.")
    SLACK_CHANNEL: str = Field(default="C08FQ51LEAF", description="Slack Channel ID from environment.")

    # Application behavior with defaults
    MAX_THREAD: int = Field(default=23, description="Maximum number of processing threads.")
    SEND_BATCH_SIZE: int = Field(default=1, description="Batch size of data sent at a time.")
    MAX_RETRY_ATTEMPTS: int = Field(default=2, description="Maximum retry attempts for sending requests.")

    # Selenium configurations
    HEADLESS_MODE: bool = Field(default=True, description="Run Selenium in headless mode")
    PAGE_LOAD_TIMEOUT: int = Field(default=600, description="Timeout for Selenium page loading")
    IMPLICITLY_TIMEOUT: int = Field(default=30, description="Timeout for Selenium Implicitly wait")

    model_config = SettingsConfigDict(env_file=".env.local", env_file_encoding="utf-8")

settings = Settings()