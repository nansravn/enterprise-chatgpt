import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from utils import naming, path, outputs
import numpy as np
import argparse
from typing import List


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns
    -------
    argparse.Namespace
        An object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Scrape internal URLs of a website.")
    parser.add_argument("url", type=str, help="The URL of the website to scrape.")
    parser.add_argument("--print-urls", action="store_true", help="Whether to print the resulting URL list.")
    return parser.parse_args()

def get_internal_urls(url: str, print_urls: bool = False) -> List[str]:
    """
    Get all internal URLs of a website.

    Parameters
    ----------
    url : str
        The URL of the website to scrape.
    print_urls : bool, optional
        Whether to print the resulting URL list, by default False.

    Returns
    -------
    List[str]
        A list of all internal URLs of the website.

    Examples
    --------
    >>> get_internal_urls("https://www.vale.com/pt/")
    ['https://www.vale.com/pt/Paginas/default.aspx', 'https://www.vale.com/pt/aboutvale/news/Paginas/default.aspx', ...]
    """
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Get all the links on the page
    links = soup.find_all("a")

    # Extract the href attribute of each link
    urls = []
    for link in links:
        href = link.get("href")
        if href is not None:
            # Parse the URL to get the domain name
            domain = urlparse(href).netloc
            if domain == urlparse(url).netloc:
                urls.append(href)

    # Print the resulting URL list if print_urls is True
    if print_urls:
        print(urls)

    # Return all the URLs that are originated from the initial website
    return urls


if __name__ == "__main__":
    args = parse_args()

    # Create a folder to store the PDF files
    project_io = naming.create_name(args.url)
    metadata_path = path.create_folder(os.path.join("data", project_io, "metadata"))

    # Get all the internal URLs of the website
    urls = list(np.unique(get_internal_urls(args.url, args.print_urls)))
    outputs.write_urls_json(urls, "urls.json", metadata_path)
