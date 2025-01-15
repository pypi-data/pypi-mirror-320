from abc import ABC, abstractmethod
from typing import Optional

from quant.domain.ticker.entity.ticker_action import TickerAction


class TickerActionRepository(ABC):
    @abstractmethod
    def insert(self, ticker_action: TickerAction):
        pass

    @abstractmethod
    def m_insert(self, ticker_action_list: list[TickerAction]):
        pass

    @abstractmethod
    def get_all(self, symbol: str) -> list[TickerAction]:
        pass

    @abstractmethod
    def get_by_date(self, symbol: str, start_date: str, end_date: str) -> list[TickerAction]:
        pass

    @abstractmethod
    def get_latest_action(self, symbol: str) -> Optional[TickerAction]:
        pass
