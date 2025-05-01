# SPDX-FileCopyrightText: 2025 deraffe <git@effa.red>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import dataclasses
import logging
import pathlib

import bs4
import httpx
import markdown

log = logging.getLogger(__name__)


@dataclasses.dataclass
class ParsedInfo:
    links: list[httpx.URL]
    images: list[tuple[httpx.URL, str]]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loglevel", default="INFO", help="Loglevel", action="store")
    parser.add_argument("start_url", type=httpx.URL)
    parser.add_argument("destination", type=pathlib.Path, default=pathlib.Path())
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        message = f"Invalid log level: {args.loglevel}"
        raise TypeError(message)
    logging.basicConfig(level=loglevel)
    backup(args.start_url, args.destination)


def backup(start_url: httpx.URL, destination: pathlib.Path) -> None:
    log.info("Backing up %s", start_url)
    mdfile = download(start_url, destination)
    info = parse(mdfile, start_url)
    for image_url, image_alt in info.images:
        download_image(image_url, image_alt, destination)
    for link in info.links:
        backup(link, destination)


def download(
    url: httpx.URL,
    destination: pathlib.Path,
    suffix: str = "/download",
    extension: str = ".md",
) -> pathlib.Path:
    name = get_name(url.path)
    destination_file = destination / (name + extension)
    if destination_file.exists():
        log.debug("Destination file already exists, skipping download")
        return destination_file
    download_url = url.copy_with(path=(url.path + suffix))
    with destination_file.open("w") as dst:
        response = httpx.get(download_url)
        dst.write(response.text)
    return destination_file


def get_name(path: str) -> str:
    pathpath = pathlib.Path(path)
    return str(pathpath.name or pathpath.parent)


def download_image(
    url: httpx.URL,
    alt_text: str,
    destination: pathlib.Path,
    uploads_folder: str = "uploads",
) -> pathlib.Path:
    name = get_name(url.path)
    uploads_path = destination / uploads_folder
    if not uploads_path.exists():
        uploads_path.mkdir()
    destination_file = uploads_path / name
    log.debug("Downloading image %s (%s) to %s", alt_text, url, destination_file)
    if destination_file.exists():
        log.debug("Destination image already exists, skipping download for %s", url)
        return destination_file
    with destination_file.open("wb") as dst:
        response = httpx.get(url)
        dst.write(response.content)
    return destination_file


def parse(mdfile: pathlib.Path, origin_url: httpx.URL) -> ParsedInfo:
    log.debug("Parsing %s from %s", mdfile, origin_url)
    host = origin_url.host
    with mdfile.open("r") as md:
        md_content = md.read()
        html_content = markdown.markdown(md_content)
    soup = bs4.BeautifulSoup(html_content, "html.parser")
    links = []
    for link in soup.find_all("a"):
        href: str = link.get("href")  # pyright: ignore reportAttributeAccessIssue
        if href is None:
            log.debug("Skipping empty link: %s", link)
            continue
        try:
            url = (
                origin_url.copy_with(path=href.strip("#"))
                if href.startswith("/")
                else httpx.URL(href)
            )
        except Exception:
            log.debug("Failed to parse link: %s", link)
            raise
        if url.host != host:
            log.debug("Skipping non-local link: %s", link)
            continue
        if url.path == "":
            log.debug("Skipping root link: %s", link)
            continue
        log.debug("Adding link: %s", link)
        links.append(url)
    images = []
    for img in soup.find_all("img"):
        url = httpx.URL(str(img["src"]))  # pyright: ignore reportIndexIssue
        if url.host == host:
            log.debug("Adding image: %s", img)
            images.append((url, str(img["alt"])))  # pyright: ignore reportIndexIssue
        else:
            log.debug("Skipping non-local image: %s", img)
    return ParsedInfo(links=links, images=images)


if __name__ == "__main__":
    main()
