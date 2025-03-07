import argparse
import asyncio
from prefect import flow
from prefect.runtime import flow_run
from monitor.monitor import Monitor
from scrapers.item import Item
from scrapers import microcenter
from utils.config_loader import load_config

# Load configuration
config = load_config()


def name_5090_condition(item: Item) -> bool:
    return "5090" in item.name


# Default store is Microcenter
store_config = config["stores"]["microcenter"]
store_url = store_config["url"]
fetch_function = microcenter_scraper.get_open_box_items
condition_function = name_5090_condition


def generate_flow_run_name():
    return flow_run.parameters["arguments"].store


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor open box items and notify via Discord.")
    parser.add_argument("--store", type=str, help="Store", required=True)
    parser.add_argument("--min-sleep", type=int, default=5, help="Minimum sleep time in seconds (default: 5s)")
    parser.add_argument("--max-sleep", type=int, default=10, help="Maximum sleep time in seconds (default: 10s)")
    parser.add_argument("--start-hour", type=int, default=0, help="Start hour (default: 0 am)")
    parser.add_argument("--end-hour", type=int, default=0, help="End hour (default: 0 pm)")

    args = parser.parse_args()

    @flow(name=args.store, flow_run_name=generate_flow_run_name)
    async def main(arguments):
        monitor = Monitor(
            fetch_items_func=fetch_function,
            condition_func=condition_function,
            webhook_url=config["discord"]["webhook_url"],
            min_sleep=arguments.min_sleep,
            max_sleep=arguments.max_sleep,
            start_hour=arguments.start_hour,
            end_hour=arguments.end_hour,
            load_cookies=store_config["load_cookies"],
            log_file=f"{arguments.store}.log"
        )

        await monitor.run(store_url)

    asyncio.run(main(args))
