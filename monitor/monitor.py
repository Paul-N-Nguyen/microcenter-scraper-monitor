import time
import random
import hashlib
import logging
from logging.handlers import RotatingFileHandler
import sys
import os
import tempfile
import glob
import asyncio
import shutil
from datetime import datetime
from utils.notifications import send_discord_notification
from prefect import task
from prefect.logging import get_run_logger


class Monitor:
    """
    Monitoring class
    """
    def __init__(self, fetch_items_func, condition_func, webhook_url, log_file, min_sleep=5, max_sleep=10,
                 notify_interval=600, start_hour=None, end_hour=None, load_cookies=''):
        self.fetch_items_func = fetch_items_func  # Function to get items
        self.condition_func = condition_func  # Function to check condition for notification
        self.webhook_url = webhook_url
        self.log_file = log_file
        self.min_sleep = min_sleep
        self.max_sleep = max_sleep
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.load_cookies = load_cookies
        self.notify_interval = notify_interval
        self.last_notification_time = 0
        self.previously_notified = set()
        self.logger = get_run_logger()

    def should_monitor(self) -> bool:
        """
        Checks if the current time is within the allowed monitoring hours.
        :return:
        """
        if not self.start_hour or not self.end_hour:
            return True
        if self.start_hour == self.end_hour:
            return True
        current_hour = datetime.now().hour
        return self.start_hour <= current_hour < self.end_hour

    async def del_temp_profile_dir(self) -> list[str]:
        """
        Generate a temp dir.  From browser class.
        :return: List of paths
        """
        temp_dir = os.path.normpath(tempfile.gettempdir())
        uc_dirs = glob.glob("uc_*", root_dir=temp_dir)

        for d in uc_dirs:
            directory = os.path.join(temp_dir, d)
            for attempt in range(5):
                try:
                    shutil.rmtree(directory, ignore_errors=False)
                    self.logger.debug(
                        "successfully removed temp profile %s" % directory
                    )
                except FileNotFoundError:
                    break
                except (PermissionError, OSError) as e:
                    if attempt == 4:
                        self.logger.debug(
                            "problem removing data dir %s\nConsider checking whether it's there and remove it by hand\nerror: %s",
                            directory,
                            e,
                        )
                    await asyncio.sleep(0.15)
                    continue

        return uc_dirs

    def setup_logger(self) -> logging.Logger:
        """
        Setups logging to stdout and writes to disk
        :return: Logger
        """
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        stdout_handler = logging.StreamHandler(sys.stdout)
        logfile_handler = RotatingFileHandler(os.path.join(log_dir, self.log_file), maxBytes=104857600, backupCount=3)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        stdout_handler.setFormatter(formatter)
        logfile_handler.setFormatter(formatter)

        logger.addHandler(stdout_handler)
        logger.addHandler(logfile_handler)

        return logger

    @staticmethod
    def item_hash(item: dict) -> str:
        """
        Hashes item dictionary
        :param item:
        :return: hash string
        """
        return hashlib.md5((item['title'] + item['price']).encode()).hexdigest()

    @task(name="Monitor")
    async def run(self, url: str) -> None:
        """
        Runs monitor
        :param url: str, URL
        :return: None
        """
        self.logger.info(f"Monitoring {url}...")
        self.logger.info(f"Start hour ({self.start_hour}) - End hour ({self.end_hour})")

        while True:
            if not self.should_monitor():
                self.logger.info("Outside monitoring hours. Sleeping for 10 minutes...")
                time.sleep(1200)  # Sleep for 10 minutes before checking again
                continue

            current_time = time.time()
            items = await self.fetch_items_func(url, self.load_cookies)

            if not items:
                self.logger.info("No items found.")
            else:
                found_new = 0
                for item in items:
                    if self.condition_func(item):
                        item_id = self.item_hash(item)
                        if item_id not in self.previously_notified or (current_time - self.last_notification_time >= self.notify_interval):
                            if self.webhook_url:
                                send_discord_notification(self.webhook_url, item)
                            self.previously_notified.add(item_id)
                            found_new += 1
                            self.logger.info(f"Notified about: {item.name} - {item.price}")
                            self.logger.info(f"Link: {item.link}")
                            self.logger.info("-" * 40)

                if found_new > 0:
                    self.last_notification_time = current_time
                    self.logger.info(f"Sent notifications for {found_new} new GeForce 5090s.")
                else:
                    self.logger.info("No new GeForce 5090s found.")

            await self.del_temp_profile_dir()

            sleep_time = random.randint(self.min_sleep, self.max_sleep)
            self.logger.info(f"Sleeping for {sleep_time} seconds...")
            await asyncio.sleep(sleep_time)
