import time

from queue import Queue
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from app.config.config import settings

class WebDriver:
    def __init__(self, max_drivers: int = settings.MAX_THREAD):
        self.max_drivers = max_drivers
        self.pool = Queue(maxsize=max_drivers)
        self._init_driver_pool()

    def _create_driver(self):
        options = webdriver.ChromeOptions()
        if settings.HEADLESS_MODE:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-application-cache")
        options.add_argument("--incognito")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
        driver.implicitly_wait(settings.IMPLICITLY_TIMEOUT)
        return driver

    def _init_driver_pool(self):
        for _ in range(self.max_drivers):
            driver = self._create_driver()
            self.pool.put(driver)

    @contextmanager
    def get_driver(self):
        driver = self.pool.get()
        try:
            yield driver
        finally:
            self.pool.put(driver)

    def shutdown_pool(self):
        while not self.pool.empty():
            driver = self.pool.get()
            driver.quit()

    @staticmethod
    def scroll_incrementally(driver, pause_time=1, max_scroll_attempts=1):
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(max_scroll_attempts):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height


webdriver_pool = WebDriver()