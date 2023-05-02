import json
from typing import List
import os


def write_urls_json(urls: List[str], file_name: str, dir_name: str = "metadata") -> None:
    """
    Saves the list of urls as a json file with one single key, "urls".

    Args:
        urls (List[str]): The list of urls to be saved.
        file_name (str): The name of the file to be created.
        dir_name (str): The name of the directory to write the file. Default is "metadata".

    Returns:
        None
    """
    with open(os.path.join(dir_name, file_name), "w") as f:
        f.write(json.dumps({"urls": urls}, indent=4))


def write_url_content_txt(content: str, file_name: str, dir_name: str = "content-stage1") -> None:
    """
    Saves the content of a url as a txt file.

    Args:
        content (str): The content of the url to be saved.
        file_name (str): The name of the file to be created.
        dir_name (str): The name of the directory to write the file. Default is "content-stage1".

    Returns:
        None
    """

    # Write the text to a file in the appropriate folder
    with open(os.path.join(dir_name, file_name), 'w', encoding='utf-8') as fp:
        fp.write(content)


def write_json(input_dict: dict, file_name: str, dir: str) -> None:
    """
    Writes a dictionary to a JSON file.

    Args:
        input_dict (dict): The dictionary to be written to the file.
        file_name (str): The name of the file to be created.
        dir (str): The name of the directory to write the file.

    Returns:
        None
    """
    with open(os.path.join(dir, file_name), "w") as f:
        f.write(json.dumps(input_dict, indent=4))
