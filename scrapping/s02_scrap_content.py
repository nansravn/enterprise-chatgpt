import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import json
from urllib.parse import unquote
import re
from utils import naming, path, outputs
from multiprocessing import Process, Queue, Pool
import argparse


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns
    -------
    argparse.Namespace
        An object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Scrap website content')
    parser.add_argument('url', type=str, help='URL to scrape')
    parser.add_argument('--n-jobs', type=int, default=16, help='Number of jobs to run in parallel')
    return parser.parse_args()

def get_website_text(url):
    # Make a GET request to the URL
    response = requests.get(url)

    # Get the text content from the response
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()

    # Remove leading and trailing whitespaces for all the lines
    text = "\n".join([line.strip() for line in text.split('\n')])

    # Replace consecutive occurrences of "\n", "\t", or " " with a single character
    for char in ['\n', '\t', ' ']:
        text = re.sub(f'[{char}]+', f'{char}', text)

    # Text can't start or end with a line break or spaces
    text = text.strip()
    return text

def generate_output_filename(url: str) -> str:
    """
    Generate a filename for the output file based on the URL.

    Parameters
    ----------
    url : str
        The URL to generate the filename from.

    Returns
    -------
    str
        The generated filename.
    """
    path = urlparse(url).path
    file_name = path.replace('/', '-') + ".txt"
    file_name = unquote(file_name)

    # Make sure that filename starts with a letter, removing leading special characters
    while not file_name[0].isalpha():
        file_name = file_name[1:]
    return file_name

def process_url(url_tuple):
    url, idx, out_path = url_tuple
    text = get_website_text(url)
    outputs.write_url_content_txt(text,  f"{idx:04}.txt", out_path)
    return True


if __name__ == '__main__':
    args = parse_args()

    project_io = naming.create_name(args.url)
    # Create a folder to store the PDF files
    out_path = path.create_folder(os.path.join("data", project_io, "content-stage1"))

    # If urls.json exists, load all urls from it and write the text of each page to a file
    urls_path = os.path.join("data", project_io, "metadata", "urls.json")
    if os.path.exists(urls_path):
        with open(urls_path, 'r') as file:
            urls = json.load(file)['urls']
            queue = Queue()
            for idx, url in enumerate(urls):
                queue.put((url, idx, out_path))
            pool = Pool(processes=args.n_jobs)
            results = []
            while not queue.empty():
                url_tuple = queue.get()
                result = pool.apply_async(process_url, args=(url_tuple,))
                results.append(result)
            pool.close()
            pool.join()
    else:
        text = get_website_text('https://www.vale.com/opportunities-for-professionals')
        print(text)