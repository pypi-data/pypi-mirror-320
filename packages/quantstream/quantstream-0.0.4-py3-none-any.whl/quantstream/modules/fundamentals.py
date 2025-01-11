from quantstream.decorators.api_validation import validate_api_key
import typing
from quantstream.config import GLOBAL_API_KEYS

from fmpsdk import (
    company_profile,
    key_executives,
    income_statement,
    balance_sheet_statement,
    cash_flow_statement,
    market_capitalization,
    historical_market_capitalization,
)


@validate_api_key("fmp")
def get_company_profile(symbol: str) -> typing.Optional[typing.List[typing.Dict]]:
    """_summary_

    Args:
        symbol (str): _description_

    Returns:
        typing.Optional[typing.List[typing.Dict]]: _description_
    """
    apikey = GLOBAL_API_KEYS["fmp"]
    data = company_profile(apikey, symbol)
    return data


@validate_api_key("fmp")
def get_key_executives(symbol: str) -> typing.Optional[typing.List[typing.Dict]]:
    """_summary_

    Args:
        symbol (str): _description_

    Returns:
        typing.Optional[typing.List[typing.Dict]]: _description_
    """
    apikey = GLOBAL_API_KEYS["fmp"]
    data = key_executives(apikey, symbol)
    return data


@validate_api_key("fmp")
def get_income_statement(
    symbol: str,
    period: str = "annual",
    limit: int = 10,
    download: bool = False,
) -> typing.Union[typing.List[typing.Dict], None]:
    """_summary_

    Args:
        symbol (str): _description_
        period (str, optional): _description_. Defaults to "annual".
        limit (int, optional): _description_. Defaults to 10.
        download (bool, optional): _description_. Defaults to False.

    Returns:
        typing.Union[typing.List[typing.Dict], None]: _description_
    """
    apikey = GLOBAL_API_KEYS["fmp"]
    data = income_statement(apikey, symbol, period, limit, download)
    return data


@validate_api_key("fmp")
def get_balance_sheet_statement(
    symbol: str,
    period: str = "annual",
    limit: int = 10,
    download: bool = False,
) -> typing.Union[typing.List[typing.Dict], None]:
    """_summary_

    Args:
        symbol (str): _description_
        period (str, optional): _description_. Defaults to "annual".
        limit (int, optional): _description_. Defaults to 10.
        download (bool, optional): _description_. Defaults to False.

    Returns:
        typing.Union[typing.List[typing.Dict], None]: _description_
    """
    apikey = GLOBAL_API_KEYS["fmp"]
    data = balance_sheet_statement(apikey, symbol, period, limit, download)
    return data


@validate_api_key("fmp")
def get_cash_flow_statement(
    symbol: str,
    period: str = "annual",
    limit: int = 10,
    download: bool = False,
) -> typing.Union[typing.List[typing.Dict], None]:
    """_summary_

    Args:
        symbol (str): _description_
        period (str, optional): _description_. Defaults to "annual".
        limit (int, optional): _description_. Defaults to 10.
        download (bool, optional): _description_. Defaults to False.

    Returns:
        typing.Union[typing.List[typing.Dict], None]: _description_
    """
    apikey = GLOBAL_API_KEYS["fmp"]
    data = cash_flow_statement(apikey, symbol, period, limit, download)
    return data


@validate_api_key("fmp")
def get_market_capitalization(symbol: str) -> typing.Optional[typing.List[typing.Dict]]:
    """_summary_

    Args:
        symbol (str): _description_

    Returns:
        typing.Optional[typing.List[typing.Dict]]: _description_
    """
    apikey = GLOBAL_API_KEYS["fmp"]
    data = market_capitalization(apikey, symbol)
    return data


@validate_api_key("fmp")
def get_historical_market_capitalization(
    symbol: str, limit: int = 10
) -> typing.Optional[typing.List[typing.Dict]]:
    """_summary_

    Args:
        symbol (str): _description_
        limit (int, optional): _description_. Defaults to 10.

    Returns:
        typing.Optional[typing.List[typing.Dict]]: _description_
    """
    apikey = GLOBAL_API_KEYS["fmp"]
    data = historical_market_capitalization(apikey, symbol, limit)
    return data
