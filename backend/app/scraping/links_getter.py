import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from content_getter import get_content_from_url
import os
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent.parent)
print(parent_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from utils import save_json, load_json


def is_valid(url: str) -> bool:
    """
    Checks if a URL is valid by ensuring it has a domain and a scheme.

    Args:
        url (str): The URL to check

    Returns:
        bool: True if the URL is valid, False otherwise
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_site_links_depth1(url: str) -> set[str]:
    """
    Retrieves all first-level links from a given URL.
    A first-level link is a direct link found on the initial page.

    Args:
        url (str): The starting URL to retrieve links from

    Returns:
        set[str]: Set of URLs found on the initial page
    """
    urls = set()
    domain_name = urlparse(url).netloc

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                continue
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not is_valid(href):
                continue
            if href in urls:
                continue
            if domain_name not in href:
                continue
            urls.add(href)
            # print(f"Found URL: {href}")

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")

    return urls


def get_all_site_links(start_url: str, max_pages=1000) -> list[str]:
    """
    Recursively retrieves all links from a website starting from a given URL.

    Args:
        start_url (str): The starting URL to begin crawling
        max_pages (int, optional): Maximum number of pages to crawl. Default is 1000.

    Returns:
        list[str]: Sorted list of all URLs found on the site
    """
    visited = set()
    to_visit = set([start_url])

    while to_visit and len(visited) < max_pages:
        print(len(visited), len(to_visit))
        current_url = to_visit.pop()
        if current_url in visited:
            continue

        # print(f"Crawling: {current_url}")
        visited.add(current_url)

        links = get_all_site_links_depth1(current_url)
        to_visit.update(links - visited)

    visited = sorted(list(visited))
    return visited


def get_all_site_contents(urls: list[str]) -> list[dict]:
    """
    Retrieves the content and title of each provided URL.

    Args:
        urls (list[str]): List of URLs to process

    Returns:
        list[dict]: List of dictionaries containing the title and content of each page
    """
    contents = []
    for idx, url in enumerate(urls):
        print(f"Processing {idx}/{len(urls)}")
        title, content = get_content_from_url(url)
        contents.append({"title": title, "content": content})

    return contents


def get_and_save_site_links(start_url: str, output_filename: str) -> list[str]:
    """
    Retrieves all site links and saves them to a JSON file.

    Args:
        start_url (str): Starting URL for crawling
        output_filename (str): Name of the output file

    Returns:
        list[str]: List of found URLs
    """
    all_site_links = get_all_site_links(start_url)
    save_json(all_site_links, output_filename)
    return all_site_links


def get_and_save_site_contents(input_filename: str, output_filename: str) -> list[dict]:
    """
    Retrieves the content of all pages and saves them to a JSON file.

    Args:
        input_filename (str): Name of the file containing the URLs
        output_filename (str): Name of the output file

    Returns:
        list[dict]: List of contents with their titles
    """
    all_site_links = load_json(input_filename)
    print(f"Processing {len(all_site_links)} URLs")

    contents = get_all_site_contents(all_site_links)
    contents.sort(key=lambda x: x["title"])
    save_json(contents, output_filename)
    return contents


def filter_and_save_useful_contents(
    input_filename: str, output_filename: str, min_length: int = 25
) -> list[dict]:
    """
    Filters the contents to keep only the most useful ones and saves them.

    Args:
        input_filename (str): Name of the file containing the contents
        output_filename (str): Name of the output file
        min_length (int): Minimum length to consider content as useful

    Returns:
        list[dict]: List of filtered contents
    """
    contents = load_json(input_filename)
    contents.sort(key=lambda x: len(x["content"]))
    filtered_contents = contents[min_length:]
    save_json(filtered_contents, output_filename)
    return filtered_contents


if __name__ == "__main__":
    # Exemple d'utilisation
    # get_and_save_site_links("https://docs.mistral.ai", "docs_all_site_links")
    # get_and_save_site_contents("docs_all_site_links", "docs_all_site_contents")
    # filter_and_save_useful_contents("docs_all_site_contents", "all_site_contents")
    pass
