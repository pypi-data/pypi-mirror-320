"""Top level configuration for QuantStream API keys and other user=specific settings"""

import sqlite3
import os
from typing import Dict

GLOBAL_API_KEYS = {}


def set_api_key(api_key: str, service: str) -> None:
    """Set the API key for a specific service.

    Args:
        api_key (str): The API key to set.
        service (str): The name of the service for which the API key is being set.
    """
    GLOBAL_API_KEYS[service] = api_key
    os.environ[f"{service.upper()}_API_KEY"] = api_key


def set_fmp_api_key(api_key: str) -> None:
    """Set the API key for the Financial Modeling Prep service.

    Args:
        api_key (str): The API key to set.
    """
    set_api_key(api_key, "fmp")


def show_api_keys() -> Dict:
    """Show all API keys that have been set.

    Returns:
        Dict: A dictionary containing all API keys that have been set.
    """
    return GLOBAL_API_KEYS


def create_project_database(location: str, db_name: str) -> None:
    """Create a new SQLite database for a project.

    Args:
        location (str): The location where the database should be created.
        db_name (str): The name of the database.
    """
    # make sure the database doesn't already exist
    if os.path.exists(os.path.join(location, db_name)):
        raise FileExistsError("Database already exists at the specified location.")

    if not os.path.exists(location):
        os.makedirs(location)

    conn = sqlite3.connect(os.path.join(location, db_name))
    conn.close()
    # set the database location and name in the global settings
    GLOBAL_API_KEYS["database"] = os.path.join(location, db_name)
