from quantstream.decorators.api_validation import validate_api_key
from fmpsdk import historical_price_full, historical_chart, quote
from quantstream.datasets.findataset import FinDataset
from quantstream.config import GLOBAL_API_KEYS
import typing


@validate_api_key("fmp")
def get_quote(symbol: typing.Union[str, list[str]]) -> typing.Optional[list[dict]]:
    """Retrieve quote information for a given symbol or list of symbols.

    Args:
        apikey (str): The API key for accessing the quote information.
        symbol (typing.Union[str, typing.List[str]]): The symbol or list of symbols for which to retrieve quote information.

    Returns:
        typing.Optional[typing.List[typing.Dict]]: A list of dictionaries containing the quote information for the given symbol(s).
            Each dictionary represents a quote and contains various fields such as symbol, price, volume, etc.
            Returns None if no quote information is available.
    """
    apikey = GLOBAL_API_KEYS["fmp"]
    data = quote(apikey, symbol)
    return data


@validate_api_key("fmp")
def get_intraday(
    symbol: str,
    time_delta: str,
    from_date: str,
    to_date: str,
    lean: bool = False,
) -> "FinDataset":
    """Fetches intraday historical chart data for a given symbol.

    Args:
        symbol (str): The symbol for the stock or security.
        time_delta (str): The time interval for the data (e.g., '1min', '5min', '15min', '30min', '1hour', '4hour).
        from_date (str): The starting date for the data in the format 'YYYY-MM-DD'.
        to_date (str): The ending date for the data in the format 'YYYY-MM-DD'.
        time_series (str, optional): The type of time series data to fetch. Defaults to fmp.default_line_param.

    Returns:
        typing.Optional[typing.List[typing.Dict]]: A list of dictionaries representing the intraday historical chart data.
    """
    apikey = GLOBAL_API_KEYS["fmp"]
    data = historical_chart(apikey, symbol, time_delta, from_date, to_date)
    return FinDataset.from_json(data)


@validate_api_key("fmp")
def get_daily(
    symbol: typing.Union[str, list],
    from_date: str = None,
    to_date: str = None,
    full: bool = False,
) -> "FinDataset":
    """Fetches daily historical stock prices for the specified symbol(s).

    Args:
        apikey (str): The API key for accessing the stock price data.
        symbol (typing.Union[str, typing.List]): The symbol(s) of the stock(s) to fetch data for.
            It can be a single symbol or a list of symbols.
        from_date (str, optional): The starting date for the historical data.
            If not provided, it fetches data from the earliest available date.
        to_date (str, optional): The ending date for the historical data.
            If not provided, it fetches data up to the latest available date.

    Returns:
        typing.Optional[typing.List[typing.Dict]]: A list of dictionaries containing the historical stock prices.
            Each dictionary represents a single day's data and includes information such as the date, open price,
            high price, low price, close price, volume, and adjusted close price.

    Raises:
        ValueError: If the API response indicates an error or an invalid request.

    """
    apikey = GLOBAL_API_KEYS["fmp"]
    data = historical_price_full(apikey, symbol, from_date, to_date)
    ds = FinDataset.from_json(data)

    if full:
        return ds

    return ds[["open", "high", "low", "close", "adjClose", "volume"]]
