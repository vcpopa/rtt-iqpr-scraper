import pytest
import os
import tempfile
import zipfile
import requests
from unittest import mock
from src.fileutils import download_file, unzip_file


@pytest.fixture
def mock_requests_get():
    with mock.patch("requests.get") as mock_get:
        yield mock_get


@pytest.fixture
def mock_zipfile():
    # Create a mock zipfile.ZipFile instance
    mock_zipfile_instance = mock.MagicMock(spec=zipfile.ZipFile)

    # Mock extractall method to simulate extraction
    def mock_extractall(extract_dir):
        # Create a mock file to simulate extraction
        with open(os.path.join(extract_dir, "mockfile.txt"), "wb") as f:
            f.write(b"Mock file content")

    mock_zipfile_instance.side_effect = lambda file, mode: mock_zipfile_instance
    mock_zipfile_instance.extractall = mock.MagicMock(side_effect=mock_extractall)

    return mock_zipfile_instance


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


def test_unzip_file(mock_zipfile):
    """
    Test for unzip_file function:
    - Mocks the zipfile.ZipFile instance to simulate extracting a zip file.
    - Checks if unzip_file correctly extracts the contents of the zip file to the specified directory.
    """
    zip_file = "mockfile.zip"
    extract_dir = tempfile.mkdtemp()

    # Create a mock zip file
    mock_zip_file_path = os.path.join(extract_dir, zip_file)
    with zipfile.ZipFile(mock_zip_file_path, "w") as zf:
        zf.writestr("mockfile.txt", b"Mock file content")

    # Call unzip_file function
    unzip_file(mock_zip_file_path, extract_dir)

    # Verify the extracted file content
    extracted_file_path = os.path.join(extract_dir, "mockfile.txt")
    assert os.path.exists(extracted_file_path)
    with open(extracted_file_path, "rb") as f:
        assert f.read() == b"Mock file content"


@pytest.mark.xfail(reason="Zip file is invalid")
def test_unzip_file_invalid_zip(mock_zipfile):
    """
    Test for unzip_file function failure case:
    - Mocks the zipfile.ZipFile instance to simulate extracting an invalid zip file.
    - Uses xfail to mark the test as expected to fail.
    """
    zip_file = "invalid_zip_file.zip"
    extract_dir = tempfile.mkdtemp()

    # Mock extractall method to raise a BadZipFile exception
    mock_zipfile.extractall.side_effect = zipfile.BadZipFile("Invalid zip file")
    unzip_file(zip_file, extract_dir)
