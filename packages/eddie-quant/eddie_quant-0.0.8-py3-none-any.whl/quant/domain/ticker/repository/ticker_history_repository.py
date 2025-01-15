from abc import ABC, abstractmethod

from typing_extensions import Optional

from quant.domain.ticker.entity.ticker_history import TickerHistory


class TickerHistoryRepository(ABC):
    @abstractmethod
    def insert(self, price_record: TickerHistory):
        pass

    @abstractmethod
    def m_insert(self, price_records: list[TickerHistory]):
        pass

    @abstractmethod
    def get_all(self, symbol: str) -> list[TickerHistory]:
        pass

    @abstractmethod
    def get_by_date(self, symbol: str, start_date: str, end_date: str) -> list[TickerHistory]:
        pass

    @abstractmethod
    def get_latest(self, symbol: str) -> Optional[TickerHistory]:
        pass
