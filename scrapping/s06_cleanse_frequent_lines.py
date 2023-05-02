import os
import json
from utils import naming, path, outputs
import glob
import argparse

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns
    -------
    argparse.Namespace
        An object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Webpage cleansing.")
    parser.add_argument("url", type=str, help="The URL of the scrapped website.")
    return parser.parse_args()

# Read the json with the lines to be cleansed
def read_stats(idx, total_urls, dir="cleansing"):
    with open(os.path.join(dir, f"{idx:04}.json"), 'r') as f:
        stats = json.load(f)
    # Normalize the stats
    for key in stats:
        stats[key] = stats[key] / total_urls
    return stats
    
# Read the webpage
def read_webpage(url_idx, dir="webpages"):
    with open(os.path.join(dir, f"{url_idx:04}.txt"), 'r', encoding="utf-8") as f:
        return f.readlines()
    
# Write the cleansed webpage, only for the lines that are not common for more than 20% of the files
def write_webpage(url_idx, stats, lines, dir="kb"):
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(os.path.join(dir, f"{url_idx:04}.txt"), 'w', encoding="utf-8") as f:
        for idx, line in enumerate(lines):
            if stats[str(idx)] < 0.2:
                f.write(line)


def write_kb(stats_folder, txt_folder, kb_folder):
    """
    Loads all the txt files in a folder into memory in a list of strings.

    Args:
        folder_path (str): Path to the folder containing the txt files.

    Returns:
        list: A list of strings, where each string is the content of a txt file.
    """
    stats_files = glob.glob(os.path.join(stats_folder, '*.json'))
    n_urls = len(stats_files)
    for stats_path in stats_files:
        basename_int = int(os.path.basename(stats_path).replace('.json', ''))
        stats = read_stats(basename_int, n_urls, stats_folder)
        lines = read_webpage(basename_int, txt_folder)
        write_webpage(basename_int, stats, lines, kb_folder)


if __name__ == '__main__':
    args = parse_args()

    project_io = naming.create_name(args.url)

    stats_folder = os.path.join("data", project_io, "stats")
    txt_folder = os.path.join("data", project_io, "content-stage1")
    out_folder = path.create_folder(os.path.join("data", project_io, "content-stage2"))

    write_kb(stats_folder, txt_folder, out_folder)
