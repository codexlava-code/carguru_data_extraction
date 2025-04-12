import logging, pandas as pd
from typing import List

from memoization import cached, CachingAlgorithmFlag

from app.config.config import settings

class Utils:
    @staticmethod
    def save_to_csv(data: List[dict], file_path: str)-> None:
        """Save scraped data to CSV."""
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        logging.info(f"Successfully saved scraped data to {file_path}")


    @cached(ttl=180, max_size=50, algorithm=CachingAlgorithmFlag.LFU, thread_safe=True)
    @staticmethod
    def read_from_csv(file_path: str) -> List[dict]:
        """Read carguru_vehicle data from CSV."""
        df = pd.read_csv(file_path)
        logging.info(f"Successfully read data from {file_path}")
        return df.to_dict(orient="records")
