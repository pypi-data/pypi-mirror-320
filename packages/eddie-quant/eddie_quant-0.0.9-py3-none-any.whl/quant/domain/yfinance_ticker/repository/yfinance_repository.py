from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from quant.domain.yfinance_ticker.entity.ticker_history import TickerHistory
from quant.domain.yfinance_ticker.entity.ticker import Ticker
from quant.domain.yfinance_ticker.entity.ticker_action import TickerAction


@dataclass
class _HistoryRequest:
    start_date: Optional[str]
    end_date: Optional[str]
    interval: str


class YFinanceRepository(ABC):

    @abstractmethod
    def get_ticker(self, ticker: str) -> Ticker:
        pass

    @abstractmethod
    def get_ticker_price_history(self, symbol: str, start_date: Optional[str], end_date: Optional[str],
                                 interval_list: list[str]) -> list[TickerHistory]:
        pass

    @abstractmethod
    def get_ticker_actions(self, symbol: str) -> list[TickerAction]:
        pass
