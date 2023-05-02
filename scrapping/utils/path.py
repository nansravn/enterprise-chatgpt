import os


def create_folder(folder_name: str) -> str:
    """
    Creates a folder with the given name if it does not already exist.

    Args:
        folder_name (str): The name of the folder to create.

    Returns:
        str: The name of the folder.
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name
