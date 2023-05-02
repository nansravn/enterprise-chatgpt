import glob
import os
import json
import numpy as np
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
    parser = argparse.ArgumentParser(description="Compute comparison statistics.")
    parser.add_argument("url", type=str, help="The URL of the scrapped website.")
    return parser.parse_args()


def write_frequency_statistics(diff_folder, txt_folder, stats_folder):
    """
    Loads all the txt files in a folder into memory in a list of strings.

    Args:
        folder_path (str): Path to the folder containing the txt files.

    Returns:
        list: A list of strings, where each string is the content of a txt file.
    """
    json_files = glob.glob(os.path.join(diff_folder, '*.json'))
    for diff_path in json_files:
        basename_int = int(os.path.basename(diff_path).replace('.json', ''))
        with open(diff_path, 'r') as f:
            diff = json.load(f)
        common_list = [i['common'] for i in diff.values()]
        common_list = list(np.concatenate(common_list))    
        stats_dict = {i : common_list.count(i) for i in range(count_lines(basename_int, txt_folder))}
        outputs.write_json(stats_dict, f"{basename_int:04}.json", stats_folder)


# Count the number of lines in the file .txt
def count_lines(idx, txt_folder):
    with open(os.path.join(txt_folder, f"{idx:04}.txt"), 'r', encoding="utf-8") as f:
        lines = f.readlines()
    return len(lines)


if __name__ == '__main__':
    args = parse_args()

    project_io = naming.create_name(args.url)

    diff_folder = os.path.join("data", project_io, "diffs")
    txt_folder = os.path.join("data", project_io, "content-stage1")
    stats_folder = path.create_folder(os.path.join("data", project_io, "stats"))

    write_frequency_statistics(diff_folder, txt_folder, stats_folder)
