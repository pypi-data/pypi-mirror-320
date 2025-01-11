import xarray as xr
import numpy as np


class Portfolio:
    """_summary_"""

    def __init__(self):
        self.data = xr.Dataset()

    def add_security(self, symbol, from_date=None, to_date=None):
        """_summary_

        Args:
            symbol (_type_): _description_
            from_date (_type_, optional): _description_. Defaults to None.
            to_date (_type_, optional): _description_. Defaults to None.
        """
        security_data = self.fmp.get_daily(symbol, from_date, to_date)
        self.data = xr.merge(
            [self.data, security_data.expand_dims({"security": [symbol]})]
        )

    def get_metric(self, metric, securities=None):
        """_summary_

        Args:
            metric (_type_): _description_
            securities (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        if securities:
            return self.data[metric].sel(security=securities)
        return self.data[metric]

    def compare_technicals(self, technical, securities=None):
        # Implement comparison logic here
        pass

    def calculate_metrics(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        # add default risk-free rate to attrs
        self.data.attrs["risk_free_rate"] = 0.02
        self.data.attrs["annual_trading_days"] = 252

        self.data["cumulative_return"] = xr.DataArray(
            np.zeros(self.data["close"].shape), dims=self.data["close"].dims
        )
        self.data["avg_daily_return"] = xr.DataArray(
            np.zeros(self.data["close"].shape), dims=self.data["close"].dims
        )
        self.data["std_dev"] = xr.DataArray(
            np.zeros(self.data["close"].shape), dims=self.data["close"].dims
        )
        self.data["sharpe_ratio"] = xr.DataArray(
            np.zeros(self.data["close"].shape), dims=self.data["close"].dims
        )
        self.data["annualized_sharpe_ratio"] = xr.DataArray(
            np.zeros(self.data["close"].shape), dims=self.data["close"].dims
        )

        for security in self.data.security:
            security_data = self.data.sel(security=security)
            # TODO: Fix this calculation completely wrong
            daily_returns = (
                security_data["close"].fillna(0) / security_data["close"].shift(time=1)
            ) - 1

            cumulative_return = (1 + daily_returns).cumprod(dim="time") - 1
            cumulative_return = cumulative_return.fillna(0)
            avg_daily_return = daily_returns.mean(dim="time")
            std_dev = daily_returns.std(dim="time")

            risk_free_rate = self.data.attrs["risk_free_rate"]
            annual_trading_days = self.data.attrs["annual_trading_days"]
            excess_return = avg_daily_return - (risk_free_rate / annual_trading_days)
            sharpe_ratio = excess_return / std_dev
            annualized_sharpe_ratio = sharpe_ratio * np.sqrt(annual_trading_days)

            metrics = {
                "cumulative_return": cumulative_return,
                "avg_daily_return": avg_daily_return,
                "std_dev": std_dev,
                "sharpe_ratio": sharpe_ratio,
                "annualized_sharpe_ratio": annualized_sharpe_ratio,
            }

            for metric, value in metrics.items():
                self.data[metric].loc[{"security": security}] = value

    def plot_cumulative_returns(self):
        """plot cumulative returns for each security in the portfolio"""
        self.data["cumulative_return"].plot.line(x="time", hue="security")
