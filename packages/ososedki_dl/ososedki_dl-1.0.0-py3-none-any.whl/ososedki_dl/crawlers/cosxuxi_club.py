"""Downloader for https://cosxuxi.club"""

from pathlib import Path

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from rich.progress import Progress, TaskID

from ososedki_dl.crawlers._common import process_album
from ososedki_dl.crawlers.fapello_is import fetch_media_urls
from ososedki_dl.utils import main_entry

DOWNLOAD_URL = "https://cosxuxi.club"
BASE_URL = ".wp.com/img.nungvl.net/"


def cosxuxi_club_title_extractor(soup: BeautifulSoup) -> str:
    text_div: Tag | NavigableString | None = soup.find("title")
    if not text_div:
        return "Unknown"
    text: str = text_div.text.strip()
    title: str = "Unknown"
    try:
        if ": " in text and " - " in text:
            title = text.split(": ")[1].split(" - ")[0].strip()
    except IndexError:
        print(f"ERROR: Could not extract title from '{text}'")
    return title


def cosxuxi_club_media_filter(soup: BeautifulSoup) -> list[str]:
    # Find all the images inside the div with the class 'contentme'
    content_div: Tag | NavigableString | None = soup.find("div", class_="contentme")
    if not content_div or isinstance(content_div, NavigableString):
        return []
    return [
        img.get("src")
        for img in content_div.find_all("img")
        if BASE_URL in img.get("src")
    ]


@main_entry
async def download_album(
    session: ClientSession,
    album_url: str,
    download_path: Path,
    progress: Progress,
    task: TaskID,
) -> list[dict[str, str]]:
    if album_url.endswith("/"):
        album_url = album_url[:-1]

    title: str = ""
    urls: list = []
    url: str = album_url

    while True:
        # TODO: Dont use fetch_media_urls function, as we need to get the soup
        urls.extend(await fetch_media_urls(session, url))

    return []

    """
    return await process_album(
        session=session,
        album_url=album_url,
        download_path=download_path,
        progress=progress,
        task=task,
        title_extractor=cosxuxi_club_title_extractor,
        media_filter=cosxuxi_club_media_filter,
    )
    """
