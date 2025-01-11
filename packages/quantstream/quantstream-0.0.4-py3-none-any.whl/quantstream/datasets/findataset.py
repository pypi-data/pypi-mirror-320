import numpy as np
import xarray as xr
import plotly.graph_objects as go
from typing import Any, List, Dict
from collections import defaultdict


@xr.register_dataarray_accessor("")
class FinDataset(xr.Dataset):
    """_summary_

    Args:
        xr (_type_): _description_

    Raises:
        ValueError: _description_
        KeyError: _description_
        ValueError: _description_
        ValueError: _description_

    Returns:
        _type_: _description_
    """

    __slots__ = ()

    def __init__(
        self,
        data_vars=None,
        coords=None,
        attrs=None,
    ):
        super().__init__(data_vars, coords, attrs)

    @property
    def name(self):
        """
        str: The name of the dataset.
        """
        return self.attrs.get("name")

    @name.setter
    def name(self, value):
        self.attrs["name"] = value

    @classmethod
    def from_json(cls, data: List[Dict[str, Any]]) -> "FinDataset":
        """
        Create a FinDataset from JSON-like data.

        Args:
            data (List[Dict[str, Any]]): A list of dictionaries containing financial data.
                                        Each dictionary should represent a data point with
                                        keys as column names and values as corresponding data.

        Raises:
            KeyError: If neither 'date' nor 'timestamp' column is found in the data.

        Returns:
            FinDataset: A new FinDataset object containing the processed data.
        """
        if (
            not data
            or not isinstance(data, list)
            or not all(isinstance(item, dict) for item in data)
        ):
            raise ValueError("Input must be a non-empty list of dictionaries")

        raw_data = defaultdict(list)
        for row in data:
            for col, val in row.items():
                raw_data[col].append(val)

        try:
            if "date" in raw_data:
                index = np.array(raw_data.pop("date"), dtype="datetime64[ns]")
            elif "timestamp" in raw_data:
                index = np.array(raw_data.pop("timestamp"), dtype="datetime64[ns]")
            else:
                raise KeyError("No date or timestamp column found in data.")
        except ValueError as e:
            raise ValueError(
                f"Error converting date/timestamp to numpy array: {str(e)}"
            )

        try:
            data_vars = {
                col: xr.DataArray(raw_data[col], dims="time", coords={"time": index})
                for col in raw_data.keys()
            }
        except ValueError as e:
            raise ValueError(f"Error creating xarray DataArray: {str(e)}")

        return cls(data_vars)

    def plot_candlestick(
        self, from_date: np.datetime64 = None, to_date: np.datetime64 = None
    ) -> go.Figure:
        """
        Plot a candlestick chart.
        """
        data = self.to_dataframe().reset_index()

        if from_date:
            data = data[data.time >= from_date]
        if to_date:
            data = data[data.time <= to_date]

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=data.time,
                    open=data.open,
                    high=data.high,
                    low=data.low,
                    close=data["close"],
                    name="Candlestick",
                )
            ]
        )

        return fig
