from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

import pandas as pd
import yfinance as yf
from loguru import logger

from quant.domain.yfinance_ticker.entity.ticker_history import TickerHistory
from quant.domain.yfinance_ticker.entity.ticker import Ticker
from quant.domain.yfinance_ticker.entity.ticker_action import TickerAction
from quant.domain.yfinance_ticker.repository.yfinance_repository import YFinanceRepository as IYFinanceRepository


@dataclass
class _HistoryRequest:
    start_date: Optional[str]
    end_date: Optional[str]
    interval: str


class YFinanceRepository(IYFinanceRepository):
    def __init__(self):
        pass

    def get_ticker(self, ticker: str) -> Ticker:
        ticker = yf.Ticker(ticker)
        ticker_info = ticker.info
        result = Ticker(
            symbol=ticker_info["symbol"],
            exchange=ticker_info["exchange"],
            quote_type=ticker_info["quoteType"],
            short_name=ticker_info["shortName"],
            long_name=ticker_info["longName"],
        )
        return result

    def get_ticker_price_history(self, symbol: str, start_date: Optional[str], end_date: Optional[str],
                                 interval_list: list[str]) -> list[TickerHistory]:
        """
        Get historical price history from Yahoo Finance
        :param symbol: str, such as 'AAPL'
        :param start_date: str, YYYY-MM-DD, if start date is none, will query all days before end_date
        :param end_date: str, YYYY-MM-DD, if end date is none, will query all days after start_date
                                        if both start_date and end_date are none, will query all days before today
        :param interval_list: [1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo], cannot be none
        :return: list[History] records
        """

        ticker = yf.Ticker(symbol)
        ticker.history(start=start_date, end=end_date)
        request_list: list[_HistoryRequest] = []

        for interval in interval_list:
            request = _HistoryRequest(
                start_date=start_date,
                end_date=end_date,
                interval=interval,
            )
            request_list.append(request)

        return self._get_ticker_price_history_internal(symbol=symbol, request_list=request_list)

    def get_ticker_actions(self, symbol: str) -> list[TickerAction]:
        ticker = yf.Ticker(symbol)
        return ticker.actions.apply(self._ticker_action_dataframe_tow_to_ticker_action, axis=1,
                                    args=(symbol,)).to_list()

    def _get_ticker_price_history_internal(self, symbol: str, request_list: list[_HistoryRequest]) -> list[
        TickerHistory]:
        result: list[TickerHistory] = []
        ticker = yf.Ticker(symbol)

        for request in request_list:
            if request is None:
                continue

            if request.start_date is None and request.end_date is None:
                pd_frames = ticker.history(interval=request.interval, period="max")
            else:
                start_date_datetime = pd.to_datetime(request.start_date)
                end_date_datetime = pd.to_datetime(request.end_date)
                pd_frames = ticker.history(interval=request.interval, start=start_date_datetime, end=end_date_datetime)

            if pd_frames is None:
                logger.warning(f"pd_frames is None got from request {request}")
                continue

            history_list = pd_frames.apply(self._dataframe_row_to_history, axis=1,
                                           args=(symbol, request.interval)).tolist()

            result.extend(history_list)

        result.sort(key=lambda x: x.time, reverse=False)
        return result

    def _dataframe_row_to_history(self, row: pd.Series, symbol: str, interval: str) -> TickerHistory:
        return TickerHistory(
            symbol=symbol,
            time=row.name,
            interval=interval,
            open=Decimal(row["Open"]).quantize(Decimal(".01")),
            high=Decimal(row["High"]).quantize(Decimal(".01")),
            low=Decimal(row["Low"]).quantize(Decimal(".01")),
            close=Decimal(row["Close"]).quantize(Decimal(".01")),
            volume=Decimal(row["Volume"]),
        )

    def _ticker_action_dataframe_tow_to_ticker_action(self, row: pd.Series, symbol: str) -> TickerAction:
        return TickerAction(
            symbol=symbol,
            time=row.name,
            dividend=Decimal(row["Dividends"]).quantize(Decimal(".000001")),
            stock_split=Decimal(row["Stock Splits"]).quantize(Decimal(".0001")),
        )
