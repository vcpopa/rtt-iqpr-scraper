"""
Main script for NHS England Statistics Data Processing

This script performs the following operations:
1. Scrapes URLs from the NHS England statistics page related to RTT waiting times.
2. Cleans and filters URLs based on keywords and start year.
3. Removes duplicate URLs and prepares a list of all ZIP file URLs found.
4. Downloads ZIP files into a 'zips' directory.
5. Extracts contents of ZIP files into an 'extracted' directory.
6. Loads extracted CSV files into a SQL database table named 'QVHRTTData'.

Dependencies:
- `urlutils` module: Provides functions for scraping, cleaning, filtering URLs.
- `fileutils` module: Provides functions for downloading and unzipping files.
- `utils` module: Provides utility functions like creating directories.
- `pandas` library: Used for reading CSV files into DataFrames and exporting to SQL.
- `os` module: Provides functions for interacting with the operating system.
- `connection` function: Custom function to establish a connection to the SQL database.

Constants:
- `BASE_URL`: Base URL of the NHS England statistics page for RTT waiting times.
- `KEYWORDS`: Keywords used for filtering URLs.
- `START_YEAR`: Start year for filtering URLs based on date.

Usage:
- Execute this script to automate the process of downloading, extracting, and loading NHS England RTT data into a SQL database.

Note: Make sure all dependencies are installed and configured properly before running the script.
"""

import os
import pandas as pd
from urlutils import (
    scrape_url,
    clean_urls,
    keyword_filter,
    date_filter,
    remove_duplicates,
)
from fileutils import download_file
from utils import create_directory, connection


# config constants
BASE_URL = (
    "https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/"
)
KEYWORDS = ["rtt-data", "statistical-work-areas"]
START_YEAR = 2023
RTT_TABLE="QVHRTTData"
SCHEMA="scd"


if __name__ == "__main__":
    urls = scrape_url(BASE_URL)
    urls = clean_urls(urls)
    urls = keyword_filter(urls, KEYWORDS)
    urls = date_filter(urls, START_YEAR)
    urls = remove_duplicates(urls)
    all_xlsx_urls = []
    for url in urls:
        zip_urls = scrape_url(url)
        zip_urls = [zip_url for zip_url in zip_urls if zip_url.endswith(".xlsx") and "incomplete-provider" in zip_url.lower()]
        all_xlsx_urls.extend(zip_urls)
    all_xlsx_urls = remove_duplicates(all_xlsx_urls)
    create_directory("files")
    for xlsx_url in all_xlsx_urls:
        download_file(url=xlsx_url, save_path="files")
    xlsx_files = os.listdir("files")
    total_rows=0
    for index, file in enumerate(xlsx_files):
        if index == 0:
            if_exists = "replace"
        else:
            if_exists = "append"
        df = pd.read_excel(f"files/{file}",skiprows=13)
        df = df.iloc[:, 1:]
        df=df[df['Treatment Function Code']=='C_999']
        rows=len(df)
        print(f"Loading  {rows} rows")
        with connection() as conn:
            df.to_sql(
                con=conn,
                name=RTT_TABLE,
                schema=SCHEMA,
                if_exists=if_exists,
                index=False,
            )
            total_rows+=rows
            print(f"{file} loaded to SQL...")
    print(f"All data loaded: {total_rows} rows")
