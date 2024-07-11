import pytest
import os
import tempfile
import zipfile
import requests
from unittest import mock
from src.fileutils import download_file


@pytest.fixture
def mock_requests_get():
    with mock.patch("requests.get") as mock_get:
        yield mock_get




def test_download_file(mock_requests_get):
    """
    Test for download_file function:
    - Mocks requests.get to simulate downloading a file.
    - Checks if download_file correctly saves the downloaded file to the specified path.
    """
    url = "https://example.com/mockfile.txt"
    save_dir = tempfile.mkdtemp()
    mock_content = b"Mock file content"

    # Mock requests.get to return mock content
    mock_requests_get.return_value.iter_content.return_value = [mock_content]
    mock_requests_get.return_value.status_code = 200

    # Call download_file function
    download_file(url, save_dir)

    # Verify the file is saved correctly
    saved_file_path = os.path.join(save_dir, "mockfile.txt")
    assert os.path.exists(saved_file_path)

    with open(saved_file_path, "rb") as f:
        assert f.read() == mock_content


@pytest.mark.xfail(reason='File does not exist')
def test_download_file_failure(mock_requests_get):
    """
    Test for download_file function failure case:
    - Mocks requests.get to simulate a failed download request.
    - Uses xfail to mark the test as expected to fail.
    """
    url = "https://example.com/nonexistentfile.txt"
    save_dir = tempfile.mkdtemp()

    # Mock requests.get to return a 404 error
    mock_requests_get.return_value.status_code = 404
    download_file(url, save_dir)