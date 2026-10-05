import logging
import textwrap
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from requests import RequestException

logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

URL = "https://www.12factor.net/"
OUTPUT_DIR = Path("pages")


def send_request(session: requests.Session, url: str) -> requests.Response:
    response = session.get(url, timeout=5)
    response.raise_for_status()
    return response


def get_links(soup: BeautifulSoup) -> list[str]:
    links = []
    for tag in soup.select("h2 a[href]"):
        link = tag["href"].removeprefix("./")  # type: ignore[union-attr]
        links.append(link)
    return links


def get_pages(
    links: list[str], session: requests.Session
) -> tuple[list[str], list[str]]:
    slugs = []
    pages = []
    for link in links:
        url = URL + link
        try:
            response = send_request(session, url)
        except RequestException as e:
            logger.error("Skipping link %s: %s", url, e)
            continue

        soup = BeautifulSoup(response.text, "lxml")

        main_article = soup.select_one("section article")
        if main_article is None:
            logger.warning("Could not find the main article in %s.", link)
            continue

        text = textwrap.fill(
            (main_article.get_text(strip=True, separator=" ")), width=73
        )
        pages.append(text)
        slugs.append(link)

    return pages, slugs


def save_pages(pages: list[str], slugs: list[str]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    for slug, page in zip(slugs, pages, strict=True):
        path = OUTPUT_DIR / f"{slug}.txt"
        try:
            with open(f"{OUTPUT_DIR}/{slug}.txt", "w", encoding="utf-8") as f:
                f.write(page)
        except OSError as e:
            logger.error("Failed to save %s. Error: %s", path, e)


def main() -> None:
    logger.info("Starting the web scraping...")

    with requests.Session() as session:
        logger.info("Fetching the main page...")
        response = send_request(session, URL)
        soup = BeautifulSoup(response.text, "lxml")

        logger.info("Extracting links from the main page...")
        links = get_links(soup)

        logger.info("Found %d links. Fetching pages...", len(links))
        pages, slugs = get_pages(links, session)

        logger.info("Saving pages to files...")
        save_pages(pages, slugs)


if __name__ == "__main__":
    main()
