import os
from pathlib import Path

def root_dir(caller_file: str, levels_up: int = 2) -> Path:
    """
    Return the absolute path to the project root, relative to the calling file.

    Args:
        caller_file (str): The __file__ of the calling script.
        levels_up (int): Number of directory levels to go up from caller_file.

    Returns:
        Path: Absolute path to the computed root directory.
    """
    current_dir = Path(caller_file).resolve()
    for _ in range(levels_up):
        current_dir = current_dir.parent
    return current_dir
