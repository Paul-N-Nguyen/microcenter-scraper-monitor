import httpx
from bs4 import BeautifulSoup
from prefect import task, flow
from prefect.logging import get_run_logger
from scrapers.item import Item


@task(name="Microcenter Get Open Box Items", retries=3, retry_delay_seconds=2)
async def get_open_box_items(url: str, load_cookies='') -> list[Item]:
    """
    Returns a list of items
    :param url: str, URL
    :param load_cookies: str, path to serialized cookies
    :return: List of items
    """
    logger = get_run_logger()
    # Attempt to mimic an actual browser
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "sec-ch-device-memory": "8",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-arch": "\"x86\"",
        "sec-ch-ua-full-version-list": "\"Not(A:Brand\";v=\"99.0.0.0\", \"Google Chrome\";v=\"133.0.6943.127\", \"Chromium\";v=\"133.0.6943.127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": "\"\"",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e}")
        raise

    soup = BeautifulSoup(response.text, 'html.parser')
    items = []
    for product in soup.select('.product_wrapper'):
        name = product.select_one('.h2').text.strip()
        price = '$' + product.select_one('.upperOB').next_sibling.text.strip()
        link = f"https://www.microcenter.com{product.select_one('.h2 a')['href']}"

        item = Item(name=name, price=price, button_state="Available", link=link)
        items.append(item)

        logger.info(f"{item.name} - {item.price}")
        logger.info(f"{item.link}")
        logger.info("-" * 40)

    return items


if __name__ == "__main__":
    URL = "https://www.microcenter.com/search/search_results.aspx?Ntk=all&sortby=match&prt=clearance&N=4294966938&myStore=false"

    @flow(name="Microcenter Open Box")
    def main(url):
        get_open_box_items(url)

    main(URL)
