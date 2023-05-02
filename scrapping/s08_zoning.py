import os
from langchain.text_splitter import TokenTextSplitter
from utils import naming, path, outputs
import glob
import argparse
# from langchain import Tokenizer


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns
    -------
    argparse.Namespace
        An object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Split webpages using a common zoning strategy.")
    parser.add_argument("url", type=str, help="The URL of the scrapped website.")
    parser.add_argument("--chunk-size", type=int, default=1600, help="Maximum number of tokens per text zone")
    parser.add_argument("--chunk-overlap", type=int, default=100, help="Number of overlapping tokens between text zones")
    return parser.parse_args()    

def split_files(txt_dir, out_dir, chunk_size, chunk_overlap):
    """
    Splits the text in each file in a folder into smaller snippets of max_tokens tokens.

    Args:
        folder_path (str): Path to the folder containing the txt files.
        max_tokens (int): Maximum number of tokens per snippet.

    Returns:
        None
    """
    txt_files = glob.glob(os.path.join(txt_dir, '*.txt'))
    text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    print(f"Sourced webpages: {len(txt_files)}")
    total_snippets = 0
    # Loop through each file in the folder
    for txt_path in txt_files:
        basename_int = int(os.path.basename(txt_path).replace('.txt', ''))
        with open(txt_path, "r") as f:
            doc_text = f.read()
        # Split the text into smaller snippets of max_tokens tokens
        snippets = text_splitter.split_text(doc_text)
        total_snippets += len(snippets)
        # Save each snippet to a new file
        for i, snippet in enumerate(snippets):
            # Set the path to the new file
            out_path = os.path.join(out_dir, f"{basename_int}-{i+1}.txt")
            # Write the snippet to the new file
            with open(out_path, "w") as f:
                f.write(snippet)
    print(f"Splitted chunks: {total_snippets}")
    

if __name__ in "__main__":
    args = parse_args()

    project_io = naming.create_name(args.url)

    txt_folder = os.path.join("data", project_io, "content-stage2")
    out_folder = path.create_folder(os.path.join("data", project_io, "content-stage3"))

    split_files(txt_folder, out_folder, args.chunk_size, args.chunk_overlap)
