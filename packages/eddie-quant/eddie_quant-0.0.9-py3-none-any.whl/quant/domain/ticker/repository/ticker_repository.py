from abc import ABC, abstractmethod

from quant.domain.ticker.entity.ticker import Ticker


class TickerRepository(ABC):
    @abstractmethod
    def insert(self, ticker: Ticker):
        pass

    @abstractmethod
    def m_insert(self, tickers: list[Ticker]):
        pass

    @abstractmethod
    def get(self, symbol: str) -> Ticker:
        pass

    @abstractmethod
    def get_all(self) -> list[Ticker]:
        pass

    @abstractmethod
    def get_by_symbols(self, symbols: list[str]) -> list[Ticker]:
        pass