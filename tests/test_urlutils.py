import pytest
from unittest import mock
from src.urlutils import scrape_url, keyword_filter, clean_urls, date_filter, remove_duplicates
import requests
from bs4 import BeautifulSoup

# Sample URLs for testing
TEST_URL = "https://example.com"
INVALID_URL = "https://invalid-url-that-does-not-exist.com"

# Mocking the requests.get function
@pytest.fixture
def mock_requests_get():
    with mock.patch("requests.get") as mock_get:
        mock_get.return_value.text = """
        <html>
        <body>
        <a href="https://example.com/rtt-data-2022-23">RTT Data 2022-23</a>
        <a href="https://example.com/rtt-data-2023-24">RTT Data 2023-24</a>
        <a href="https://example.com/rtt-data-2024-25">RTT Data 2024-25</a>
        <a href="https://example.com/other-data-2022-23">Other Data 2022-23</a>
        </body>
        </html>
        """
        yield mock_get

# Test for scrape_url function
def test_scrape_url(mock_requests_get):
    """
    Test for scrape_url function:
    - Mocks the requests.get function to return a sample HTML with anchor tags.
    - Checks if scrape_url correctly extracts href attributes from anchor tags.
    """
    urls = scrape_url(TEST_URL)
    assert len(urls) == 4
    assert all(url.startswith("https://example.com/") for url in urls)

# Test for keyword_filter function
def test_keyword_filter():
    """
    Test for keyword_filter function:
    - Checks if keyword_filter filters URLs based on the presence of specified keywords.
    """
    urls = [
        "https://example.com/test-data/rtt-data-2022-23",
        "https://example.com/test-data/rtt-data-2023-24",
        "https://example.com/test-data/rtt-data-2024-25",
        "https://example.com/other-data-2022-23",
    ]
    keywords = ["rtt-data", "test-data"]

    filtered_urls = keyword_filter(urls, keywords)
    assert len(filtered_urls) == 3
    assert all(keyword in url for url in filtered_urls for keyword in keywords)

# Test for clean_urls function
def test_clean_urls():
    """
    Test for clean_urls function:
    - Checks if clean_urls removes trailing slashes and filters out non-HTTP/HTTPS URLs.
    """
    urls = [
        "https://example.com/",
        "http://example.com/path/",
        "ftp://example.com/file",
        "invalid-url"
    ]
    cleaned_urls = clean_urls(urls)
    assert len(cleaned_urls) == 2
    assert all(url.startswith(("http://", "https://")) for url in cleaned_urls)

# Test for date_filter function
def test_date_filter():
    """
    Test for date_filter function:
    - Checks if date_filter filters URLs based on the start year extracted from the URL.
    """
    urls = [
        "https://example.com/rtt-data-2022-23",
        "https://example.com/rtt-data-2023-24",
        "https://example.com/rtt-data-2024-25",
    ]
    start_year = 2023

    filtered_urls = date_filter(urls, start_year)
    assert len(filtered_urls) == 2
    assert all(url.endswith("2023-24") or url.endswith("2024-25") for url in filtered_urls)

# Test for remove_duplicates function
def test_remove_duplicates():
    """
    Test for remove_duplicates function:
    - Checks if remove_duplicates removes duplicate elements from a list.
    """
    l = [1, 2, 2, 3, 4, 4, 5]
    unique_list = remove_duplicates(l)
    assert len(unique_list) == 5
    assert sorted(unique_list) == [1, 2, 3, 4, 5]


