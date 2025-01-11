from quantstream.decorators.api_validation import validate_api_key
from fmpsdk import available_commodities, commodities_list
from quantstream.config import GLOBAL_API_KEYS
import typing


@validate_api_key("fmp")
def get_available_commodities() -> typing.Optional[typing.List[typing.Dict]]:
    """Retrieve a list of available commodities from the FMP API.

    Returns:
        typing.Optional[typing.List[typing.Dict]]: A list of dictionaries containing information about available commodities.
            Each dictionary represents a commodity and contains various fields such as symbol, name, etc.
            Returns None if no commodities are available.
    """
    apikey = GLOBAL_API_KEYS["fmp"]
    data = available_commodities(apikey)
    return data


@validate_api_key("fmp")
def get_commodities_list() -> typing.Optional[typing.List[typing.Dict]]:
    """Retrieve a list of commodities from the FMP API.

    Returns:
        typing.Optional[typing.List[typing.Dict]]: A list of dictionaries containing information about commodities.
            Each dictionary represents a commodity and contains various fields such as symbol, name, etc.
            Returns None if no commodities are available.
    """
    apikey = GLOBAL_API_KEYS["fmp"]
    data = commodities_list(apikey)
    return data
