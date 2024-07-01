"""
Module: urlutils

This module provides utility functions for URL scraping, filtering, and cleaning.

Functions:
- scrape_url(url: str) -> List[str]:
    Scrapes all anchor ('a') tags from the given URL and returns a list of href attributes.

- keyword_filter(urls: List[str], keywords: List[str]) -> List[str]:
    Filters URLs based on the presence of all specified keywords.

- clean_urls(urls: List[str]) -> List[str]:
    Cleans URLs by removing trailing slashes and filtering out non-HTTP/HTTPS URLs.

- date_filter(urls: List[str], start_year: int) -> List[str]:
    Filters URLs based on the start year, extracting the year range from the URL.

- remove_duplicates(l: List[Any]) -> List[Any]:
    Removes duplicate elements from a list and returns the unique elements.

Dependencies:
- requests: For making HTTP requests.
- BeautifulSoup (from bs4): For parsing HTML and extracting data from web pages.
- typing.List, typing.Any: For type annotations in function signatures.

Usage:
Import this module to use its functions for processing URLs in web scraping and data extraction tasks.
"""
from typing import List, Any
import requests
from bs4 import BeautifulSoup


def scrape_url(url: str) -> List[str]:
    """
    Scrapes all anchor ('a') tags from the given URL and returns a list of href attributes.

    Parameters:
    - url (str): The URL of the web page to scrape.

    Returns:
    - List[str]: A list of URLs found within the anchor tags on the web page.
    """
    response = requests.get(url,timeout=120)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    links = [link["href"] for link in links]
    return links


def keyword_filter(urls: List[str], keywords: List[str]) -> List[str]:
    """
    Filters URLs based on the presence of all specified keywords.

    Parameters:
    - urls (List[str]): List of URLs to filter.
    - keywords (List[str]): List of keywords to check within each URL.

    Returns:
    - List[str]: Filtered list of URLs that contain all specified keywords.
    """
    return [url for url in urls if all(keyword in url for keyword in keywords)]


def clean_urls(urls: List[str]) -> List[str]:
    """
    Cleans URLs by removing trailing slashes and filtering out non-HTTP/HTTPS URLs.

    Parameters:
    - urls (List[str]): List of URLs to clean.

    Returns:
    - List[str]: Cleaned list of URLs without trailing slashes and non-HTTP/HTTPS URLs.
    """
    cleaned_urls = [
        url.rstrip("/") for url in urls if url.startswith(("http://", "https://"))
    ]
    return cleaned_urls


def date_filter(urls: List[str], start_year: int) -> List[str]:
    """
    Filters URLs based on the start year, extracting the year range from the URL.

    Parameters:
    - urls (List[str]): List of URLs to filter based on date.
    - start_year (int): The starting year to filter URLs.

    Returns:
    - List[str]: Filtered list of URLs that match or exceed the specified start year.
    """
    filtered_urls = []
    for url in urls:
        year_range_part = url.split("rtt-data-")[-1]
        if "-" in year_range_part:
            start, _ = map(int, year_range_part.split("-"))
            if start >= start_year:
                filtered_urls.append(url)

        else:
            print(f"Skipping URL due to missing hyphen: {url}")
    return filtered_urls


def remove_duplicates(l: List[Any]) -> List[Any]:
    """
    Removes duplicate elements from a list and returns the unique elements.

    Parameters:
    - l (List[Any]): List from which duplicates should be removed.

    Returns:
    - List[Any]: List containing only unique elements from the input list.
    """
    return list(set(l))
