"""
Module: fileutils

This module provides utility functions for downloading files from URLs and extracting zip files.

Functions:
- download_file(url: str, save_path: str) -> None:
    Download a file from a URL and save it to the specified path.

- unzip_file(zip_file: str, extract_dir: str) -> None:
    Extract a zip file to a specified directory.

Dependencies:
- os: For interacting with the operating system, such as path manipulation.
- urllib.parse.urlparse: For parsing URLs.
- requests: For making HTTP requests, used to download files.
- zipfile: For handling zip files, used to extract zip archives.

Usage:
Import this module to use its functions for downloading files from URLs and extracting zip files.
"""

import os
from urllib.parse import urlparse
import requests



def download_file(url: str, save_path: str) -> None:
    """
    Download a file from a URL and save it to the specified path.

    Parameters:
    - url (str): The URL of the file to download.
    - save_path (str): The path where the file should be saved locally.
    """
    file_name = os.path.basename(urlparse(url).path)
    save_path = os.path.join(save_path, file_name)
    response = requests.get(url, stream=True,timeout=120)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
