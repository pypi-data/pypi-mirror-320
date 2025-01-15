from datetime import datetime, timedelta
from typing import Optional

from loguru import logger

from quant.common.consts.time import Interval, TimeConfig
from quant.common.utils.time_util import TimeUtil
from quant.domain.ticker.entity.ticker import Ticker
from quant.domain.ticker.entity.ticker_action import TickerAction
from quant.domain.ticker.entity.ticker_history import TickerHistory
from quant.domain.ticker.repository.ticker_action_repository import TickerActionRepository
from quant.domain.ticker.repository.ticker_history_repository import TickerHistoryRepository
from quant.domain.ticker.repository.ticker_repository import TickerRepository


class TickerDataService:
    def __init__(self, ticker_repository: TickerRepository, history_repository: TickerHistoryRepository,
                 ticker_action_repository: TickerActionRepository):
        self.__ticker_repository = ticker_repository
        self.__history_repository = history_repository
        self.__ticker_action_repository = ticker_action_repository

    def get_all_tickers(self) -> list[Ticker]:
        return self.__ticker_repository.get_all()

    def get_tickers_data(self, symbols: list[str]) -> list[Ticker]:
        return self.__ticker_repository.get_by_symbols(symbols)

    def get_ticker_data(self, symbol: str) -> Optional[Ticker]:
        try:
            return self.__ticker_repository.get(symbol=symbol)
        except Exception as e:
            logger.error(f"failed to get ticker info for {symbol}: {e}")
            return None

    def get_history_by_symbol(self, symbol: str, start_date: Optional[str], end_date: Optional[str],
                              interval: str) -> list[TickerHistory]:

        if start_date is None and end_date is None:
            return self.__history_repository.get_all(symbol)
        if start_date is None:
            start_date = TimeConfig.DEFAULT_START_DATE
        if end_date is None:
            current_time = datetime.now(TimeConfig.DEFAULT_TIMEZONE)
            end_datetime = current_time + timedelta(hours=24)  # add one day to include today's data
            end_date = end_datetime.strftime(TimeConfig.DEFAULT_DATE_FORMAT)

        records = self.__history_repository.get_by_date(symbol=symbol, start_date=start_date, end_date=end_date)
        if interval is None:
            return records

        return list(filter(lambda r: r.interval == interval, records))

    def get_history_latest_date(self, symbol: str) -> Optional[str]:
        """
        get latest date from price history
        :param symbol:
        :type symbol:
        :return: return None if there is no history price record
        :rtype:
        """
        latest_data = self.__history_repository.get_latest(symbol=symbol)
        if latest_data is None:
            return None

        return TimeUtil.get_date_str(latest_data.time)

    def get_ticker_all_actions_by_symbol(self, symbol: str) -> list[TickerAction]:
        return self.__ticker_action_repository.get_all(symbol=symbol)

    def get_ticker_actions(self, symbol: str, start_date: Optional[str], end_date: Optional[str]) -> list[TickerAction]:
        if start_date is None and end_date is None:
            return self.__ticker_action_repository.get_all(symbol)
        if start_date is None:
            start_date = TimeConfig.DEFAULT_START_DATE
        if end_date is None:
            current_time = datetime.now(TimeConfig.DEFAULT_TIMEZONE)
            end_datetime = current_time + timedelta(hours=24)  # add one day to include today's data
            end_date = end_datetime.strftime(TimeConfig.DEFAULT_DATE_FORMAT)

        return self.__ticker_action_repository.get_by_date(symbol=symbol, start_date=start_date, end_date=end_date)
