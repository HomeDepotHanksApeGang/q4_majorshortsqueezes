import enum
import pandas as pd
import yfinance as yf
from typing import Callable, Dict, List, Optional, Set

from q4_majorshortsqueezes import get_tickers_fixed as gt


"""
A Panda's data frame with columns:
Open, High, Low, Close, Adj Close, Volume, date_id, OC-High, OC-Low
"""
TickerHistory = pd.DataFrame


class TickerContainer:
    """A container to store historical ticker data.

    The container only store tickers that meet all of the added criteria.
    """
    def __init__(self, ):
        self._criteria: List[Callable[[TickerHistory], bool]] = []
        self.__stored_tickers: Dict[str, TickerHistory] = {}

    def add_criterion(self, criterion: Callable[[TickerHistory], bool]):
        self._criteria.append(criterion)

    def store_ticker(self, ticker: str, ticker_history: TickerHistory):
        if all(criterion(ticker_history) for criterion in self._criteria):
            self.__stored_tickers[ticker] = ticker_history

    def get_stored_tickers(self) -> Dict[str, TickerHistory]:
        return self.__stored_tickers


def load_ticker_history(ticker: str, start_date: Optional[str]) -> TickerHistory:
    """Loads a ticker data from Yahoo Finance, adds a data index column data_id and Open-Close High/Low columns.

    Args:
        ticker: The stock ticker.
        start_date: Start date to load stock ticker data formatted YYYY-MM-DD.
                    If `None` is given the max date range will be used.

    Returns:
        A Panda's data frame with columns Open, High, Low, Close, Adj Close, Volume, date_id, OC-High, OC-Low.
    """
    df_data = yf.download(ticker, start=start_date, progress=False)

    df_data["date_id"] = (df_data.index.date - df_data.index.date.min()).astype(
        "timedelta64[D]"
    )
    df_data["date_id"] = df_data["date_id"].dt.days + 1

    df_data["OC_High"] = df_data[["Open", "Close"]].max(axis=1)
    df_data["OC_Low"] = df_data[["Open", "Close"]].min(axis=1)

    return df_data


def load_ticker_history_from_csv(file_path: str) -> TickerHistory:
    """Load a tickers historical price data from the given csv.

    Attention:
    The loaded dataframes are not fully identical with the ones downloaded.
    When loaded from csv a new column `date` exists which is stored in the data series as
    tuples when loading the data from `yfinance`.

    Args:
        file_path: The path to the comma-separated csv file that contains the historical price data.

    Returns:
        A Panda's data frame with columns Date, Open, High, Low, Close, Adj Close, Volume, date_id, OC-High, OC-Low.
    """
    # TODO: Make the format identical with `yfinance` loading
    return pd.read_csv(file_path)


def retrieve_tickers_with_get_all_tickers_package(nyse: bool = False,
                                                  nasdaq: bool = False,
                                                  amex: bool = False,
                                                  min_market_cap: int = 0) -> Set[str]:
    tickers = set(gt.get_tickers(NYSE=nyse, NASDAQ=nasdaq, AMEX=amex))
    if min_market_cap:
        tickers_filtered = set(gt.get_tickers_filtered(mktcap_min=min_market_cap))
        tickers = tickers.intersection(tickers_filtered)
    return tickers
