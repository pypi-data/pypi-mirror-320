"""basic time series equations"""

from typing import Union
import numpy as np
import polars as pl
import pandas as pd


# changes over time
def absolute_returns(
    prices: Union[pd.DataFrame, pd.Series, np.ndarray, pl.DataFrame, pl.Series],
    cumulative: bool = True,
) -> Union[pd.Series, np.ndarray, pl.Series]:
    """
    Calculate the absolute return of a series of prices.

    Args:
        prices (Union[pd.DataFrame, pd.Series, np.ndarray, pl.DataFrame, pl.Series]): Prices data.
        cumulative (bool): Whether to return cumulative returns. Default is True.

    Returns:
        Union[pd.Series, np.ndarray, pl.Series]: A Series or array of returns.

    Raises:
        ValueError: If input is not a valid type or contains non-numeric data.
    """
    if isinstance(prices, (pd.DataFrame, pd.Series)):
        rets = prices.diff()
    elif isinstance(prices, np.ndarray):
        rets = np.diff(prices, prepend=np.nan)
    elif isinstance(prices, (pl.DataFrame, pl.Series)):
        rets = prices.diff()
    else:
        raise ValueError(
            "Input must be a pandas DataFrame/Series, numpy array, or Polars DataFrame/Series"
        )

    if cumulative:
        if isinstance(rets, (pd.DataFrame, pd.Series)):
            return rets.cumsum()
        elif isinstance(rets, np.ndarray):
            return np.cumsum(rets)
        else:  # Polars
            return rets.cum_sum()
    return rets


def percentage_returns(prices: pd.DataFrame, cumulative: bool = True) -> pd.DataFrame:
    """
    Calculate the percentage return of a series of prices.

    Args:
        prices (pd.DataFrame): A DataFrame of prices.

    Returns:
        pd.Series: A Series of percentage returns.
    """
    rets = prices.pct_change()
    if cumulative:
        return rets.cumsum()
    return rets


def log_returns(
    prices: pd.DataFrame, cumulative: bool = True, normalize: bool = True
) -> pd.DataFrame:
    """
    Calculate the log return of a series of prices.

    Args:
        prices (pd.DataFrame): A DataFrame of prices.

    Returns:
        pd.Series: A Series of log returns.
    """
    rets = np.log(prices / prices.shift(1))
    if cumulative and normalize:
        return rets.cumsum().apply(np.exp)
    elif cumulative:
        return rets.cumsum()
    return rets


def rolling_statistics():
    pass
