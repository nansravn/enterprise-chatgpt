import tiktoken
import os
import json
import glob
from utils import naming, path, outputs
import argparse


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns
    -------
    argparse.Namespace
        An object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Webpage tokenization.")
    parser.add_argument("url", type=str, help="The URL of the scrapped website.")
    parser.add_argument("--model-name", type=str, default="text-davinci-003", help="The name of the LLM model for the tokenization.")
    return parser.parse_args()

def count_tokens(text, encoding):
    num_tokens = len(encoding.encode(text))
    return num_tokens

def write_tokens_metadata(txt_folder, metadata_folder, encoding):
    metadata_dict = {}
    txt_files = glob.glob(os.path.join(txt_folder, '*.txt'))
    # sort the files by name
    txt_files.sort(key=lambda x: int(os.path.basename(x).replace('.txt', '')))
    for txt_path in txt_files:
        with open(txt_path, 'r', encoding="utf-8") as f:
            text = f.read()
        num_tokens = count_tokens(text, encoding)
        basename_int = int(os.path.basename(txt_path).replace('.txt', ''))
        metadata_dict[basename_int] = num_tokens
    with open(os.path.join(metadata_folder, "tokens.json"), "w") as f:
        f.write(json.dumps(metadata_dict, indent=4))

if __name__ == '__main__':
    # Define the URL to scrape
    args = parse_args()
    encoding = tiktoken.encoding_for_model(args.model_name)

    project_io = naming.create_name(args.url)

    txt_folder = os.path.join("data", project_io, "content-stage2")
    metadata_folder = path.create_folder(os.path.join("data", project_io, "metadata"))

    write_tokens_metadata(txt_folder, metadata_folder, encoding)
