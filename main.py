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
        raise TypeError(f"Invalid log level: {args.loglevel}")
    logging.basicConfig(level=loglevel)
    backup(args.start_url, args.destination)


def backup(start_url: httpx.URL, destination: pathlib.Path) -> None:
    log.info("Backing up %s", start_url)
    mdfile = download(start_url, destination)
    info = parse(mdfile, start_url)
    for image_url, image_alt in info.images:
        log.warning("Not downloading image '%s' at %s", image_alt, image_url)
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
    download_url = url.copy_with(path=(url.path + suffix))
    with destination_file.open("w") as dst:
        response = httpx.get(download_url)
        dst.write(response.text)
    return destination_file


def get_name(path: str) -> str:
    pathpath = pathlib.Path(path)
    return str(pathpath.name or pathpath.parent)


def parse(mdfile: pathlib.Path, origin_url: httpx.URL) -> ParsedInfo:
    log.debug("Parsing %s from %s", mdfile, origin_url)
    host = origin_url.host
    with mdfile.open("r") as md:
        md_content = md.read()
        html_content = markdown.markdown(md_content)
    soup = bs4.BeautifulSoup(html_content, "html.parser")
    links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href is None:
            log.debug("Skipping empty link: %s", link)
            continue
        url = (
            origin_url.copy_with(path=href) if href.startswith("/") else httpx.URL(href)
        )
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
        url = httpx.URL(img["src"])
        if url.host == host:
            log.debug("Adding image: %s", img)
            images.append((url, img["alt"]))
        else:
            log.debug("Skipping non-local image: %s", img)
    return ParsedInfo(links=links, images=images)


if __name__ == "__main__":
    main()
