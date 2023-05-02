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
    parser = argparse.ArgumentParser(description="Compares text files in a folder and saves the differences to JSON files.")
    parser.add_argument("url", type=str, help="The URL of the scrapped website.")
    return parser.parse_args()

def load_txt_files(folder_path):
    """
    Loads all the txt files in a folder into memory in a list of strings.

    Args:
        folder_path (str): Path to the folder containing the txt files.

    Returns:
        list: A list of strings, where each string is the content of a txt file.
    """
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    txt_files_content = []
    for txt_file in txt_files:
        with open(txt_file, 'r', encoding='utf-8') as f:
            txt_files_content.append(f.readlines())
    basename_int = [int(os.path.basename(txt_file).replace('.txt','')) for txt_file in txt_files]
    # Create a dictionary where basename_int are the keys and txt_files_content are the values
    txt_files_dict = dict(zip(basename_int, txt_files_content))
    # Sort the keys of the dictionary
    txt_files_dict = {k: txt_files_dict[k] for k in sorted(txt_files_dict.keys())}
    return txt_files_dict


def diff(content1, content2):
    """
    Compares two text files and returns a dictionary with the differences.

    The dictionary has two keys: 'equal' and 'different'. The value of each key is a list of line numbers
    that are equal or different between the two files.

    Args:
        file1_path (str): Path to the first file.
        file2_path (str): Path to the second file.

    Returns:
        dict: A dictionary with the differences between the two files.
    """
    equal_lines = []
    different_lines = []

    # Compare files from top to bottom
    for i, (line1, line2) in enumerate(zip(content1, content2)):
        if line1 == line2:
            equal_lines.append(i)
        else:
            pass

    # Compare files from bottom to top
    for i, (line1, line2) in enumerate(zip(reversed(content1), reversed(content2))):
        if line1 == line2:
            equal_lines.append(len(content1) - i - 1)
        else:
            pass

    # Remove duplicates
    equal_lines = sorted(list(set(equal_lines)))

    # Find the lines that are different
    for i in range(len(content1)):
        if i not in equal_lines:
            different_lines.append(i)

    return {'common': equal_lines, 'unique': different_lines}


def compare_all_files(source_path, out_path):
    """
    Compares all text files in a folder with each other and saves the differences to JSON files.

    Args:
        folder_path (str): Path to the folder containing the txt files.
    """
    txt_files_dict = load_txt_files(source_path)
    for basename1, file1_content in txt_files_dict.items():
        diff_dict = {}
        for basename2, file2_content in txt_files_dict.items():
            if basename1 != basename2:
                diff_dict[basename2] = diff(file1_content, file2_content)

        
        outputs.write_json(diff_dict, f"{basename1:04}.json", out_path)


if __name__ == '__main__':
    args = parse_args()

    project_io = naming.create_name(args.url)
    # Create a folder to store the PDF files
    out_path = path.create_folder(os.path.join("data", project_io, "diffs"))
    source_path = os.path.join("data", project_io, "content-stage1")
    # If there exist a webpages folder with .txt files, compare all the txt files in it
    if os.path.exists(source_path):
        compare_all_files(source_path, out_path)
    else:
        pass
