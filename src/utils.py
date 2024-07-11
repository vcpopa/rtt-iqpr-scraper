"""
Module: utils

This module provides utility functions for general-purpose tasks such as directory creation,
database connections, and credential retrieval from Azure KeyVault.

Functions:
- connection() -> Iterator[Engine]:
    Context manager to create and manage a database connection using SQLAlchemy.

- create_directory(directory_path: str) -> None:
    Creates a directory if it does not already exist.

- get_credential(name: str) -> str:
    Retrieves a credential value from Azure KeyVault using Azure Identity.

Exceptions:
- KeyVaultError: Custom exception raised when a credential is not found or is empty.

Dependencies:
- os: For interacting with the operating system, specifically for directory manipulation.
- contextlib.contextmanager: For defining context managers in Python.
- urllib: For URL manipulation and parsing.
- typing.Iterator: Type hint for an iterator.
- sqlalchemy.create_engine: For creating SQLAlchemy database engine.
- sqlalchemy.engine.Engine: Represents an open database connection.
- azure.identity.DefaultAzureCredential: Provides credentials from Azure environment.
- azure.keyvault.secrets.SecretClient: Client library to interact with Azure KeyVault.

Usage:
Import this module to use its functions for managing database connections, directory creation,
and retrieving credentials securely from Azure KeyVault.
"""

import os
import re
from contextlib import contextmanager
import urllib
from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class KeyVaultError(Exception):
    """Custom exception raised for KeyVault errors."""

    pass


@contextmanager
def connection() -> Iterator[Engine]:
    """
    Context manager to create and close a database connection.

    Loads database connection parameters from environment variables, creates
    a SQLAlchemy engine, and yields the engine. The engine is closed when the
    context is exited.

    Returns:
        Iterator[Engine]: An iterator that yields a SQLAlchemy Engine.
    """

    connstr = get_credential("public-dataflow-connectionstring")
    params = urllib.parse.quote_plus(connstr)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    try:
        yield engine
    finally:
        engine.dispose()


def create_directory(directory_path: str) -> None:
    """
    Create a directory if it does not exist.

    Parameters:
    - directory_path (str): The path of the directory to create.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def get_credential(name: str) -> str:
    """
    Retrieves a credential value from Azure KeyVault.

    Parameters:
    - name (str): The name of the credential inside KeyVault.

    Returns:
    - credential (str): The retrieved credential value.

    Raises:
    - KeyVaultError: If credential is not found or is empty.
    """
    kv_uri = "https://qvh-keyvault.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=kv_uri, credential=credential)
    credential_value = client.get_secret(name).value
    if not credential_value:
        raise KeyVaultError(
            "Credential value not found or empty, please check KeyVault."
        )
    return credential_value


def extract_date_from_filename(filename):
    # Define the regex pattern to match the date
    # Assuming the date format is a three-letter month followed by a two-digit day (e.g., Mar24)
    pattern = r'([A-Za-z]{3}\d{2})'
    
    # Search for the pattern in the filename
    match = re.search(pattern, filename)
    
    # If a match is found, return it
    if match:
        return match.group(1)
    else:
        return None
