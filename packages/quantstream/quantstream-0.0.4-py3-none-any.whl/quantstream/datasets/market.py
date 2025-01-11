"""A module for market data analysis and retrieval."""

import os


class Market:
    """_summary_"""

    def __init__(self):
        self.data = {}
        self.api_key = os.getenv
