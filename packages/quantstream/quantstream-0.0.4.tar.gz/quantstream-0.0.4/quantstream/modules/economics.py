"""Pull economic data from the St. Louis Federal Reserve's FRED API."""

import pandas as pd
import requests
import datetime
from quantstream.config import GLOBAL_API_KEYS


def get_fred_series(
    series_id: str, start_date: datetime.date, end_date: datetime.date
) -> pd.DataFrame:
    """
    Pulls economic data from the St. Louis Federal Reserve's FRED API.

    Args:
        series_id (str): The FRED series ID.
        start_date (datetime.date): The start date for the data.
        end_date (datetime.date): The end date for the data.

    Returns:
        pd.DataFrame: The economic data.
    """
    api_key = GLOBAL_API_KEYS.get("FRED")
    if not api_key:
        raise ValueError("FRED API key is required to proceed.")

    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json&observation_start={start_date}&observation_end={end_date}"
    response = requests.get(url)
    data = response.json()

    if "error_message" in data:
        raise ValueError(data["error_message"])

    df = pd.DataFrame(data["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df
