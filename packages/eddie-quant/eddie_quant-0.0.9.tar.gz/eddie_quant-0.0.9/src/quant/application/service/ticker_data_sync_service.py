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
from quant.domain.yfinance_ticker.repository.yfinance_repository import YFinanceRepository


class TickerDataSyncService:
    def __init__(self, ticker_repository: TickerRepository, yfinance_repository: YFinanceRepository,
                 ticker_history_repository: TickerHistoryRepository,
                 ticker_action_repository: TickerActionRepository, ):
        self._ticker_repository = ticker_repository
        self._yfinance_repository = yfinance_repository
        self._ticker_history_repository = ticker_history_repository
        self._ticker_action_repository = ticker_action_repository

    def add_ticker(self, symbol: str):
        if len(symbol) < 1:
            raise ValueError("symbol is empty")

        try:
            existing_ticker_record = self._ticker_repository.get(symbol)
            if existing_ticker_record is None:
                ticker = self._yfinance_repository.get_ticker(symbol)
                ticker_entity = Ticker(
                    symbol=ticker.symbol,
                    exchange=ticker.exchange,
                    quote_type=ticker.quote_type,
                    short_name=ticker.short_name,
                    long_name=ticker.long_name,
                )

                self._ticker_repository.insert(ticker_entity)
            else:
                logger.warning(
                    f"no record insert, ticker record already exists {existing_ticker_record} for symbol {symbol}")
        except Exception as e:
            raise BaseException(f"failed to add ticker info for {symbol}: {e}")

    def sync_ticker_data(self, symbol: str):
        """
        sync ticker history and action data
        :param symbol: symbol
        :type symbol: string
        :return:
        :rtype:
        """

    def sync_ticker_history(self, symbol: str, start_date: Optional[str], end_date: Optional[str]):
        """
        Update historical price history from Yahoo Finance to db
        :param symbol: str, such as 'AAPL'
        :param start_date: str, YYYY-MM-DD, inclusive, if start date is none, will update all days before end_date (inclusive)
        :param end_date: str, YYYY-MM-DD, exclusive, if end date is none, will update all days after start_date else
                                        if both start_date and end_date are none, will update all days before today (include today)
        """

        if len(symbol) < 1:
            raise ValueError("symbol is empty")

        try:
            self._ticker_repository.get(symbol)
        except Exception as e:
            raise BaseException(f"failed to get ticker info for {symbol}: {e}")

        interval_list = [member.value for member in Interval]
        history_list = self._yfinance_repository.get_ticker_price_history(symbol=symbol, start_date=start_date,
                                                                          end_date=end_date,
                                                                          interval_list=interval_list)
        if history_list is None or len(history_list) == 0:
            logger.info(f"no history data found for {symbol}")
            return
        history_entity_list = [TickerHistory(
            id=-1,
            symbol=h.symbol,
            time=h.time,
            interval=h.interval,
            open=h.open,
            high=h.high,
            low=h.low,
            close=h.close,
            volume=h.volume
        ) for h in history_list]
        try:
            self._ticker_history_repository.m_insert(history_entity_list)
        except Exception as e:
            raise BaseException(f"failed to insert history data {history_list} for {symbol}: {e}")

    def sync_ticker_action(self, symbol: str):
        if len(symbol) < 1:
            raise ValueError("symbol is empty")

        try:
            self._ticker_repository.get(symbol)
        except Exception as e:
            raise BaseException(f"failed to get ticker info for {symbol}: {e}")

        try:
            actions = self._yfinance_repository.get_ticker_actions(symbol)
            if actions is None or len(actions) == 0:
                logger.info(f"no actions for {symbol}")
                return

            latest_existing_action = self._ticker_action_repository.get_latest_action(symbol)
            if latest_existing_action is None:
                logger.info(f"no actions for {symbol} right now, insert full action data")
                self._ticker_action_repository.m_insert(actions)
            else:
                actions_after_latest_date = list[TickerAction](
                    filter(lambda action: action is not None and action.time > latest_existing_action.time, actions))
                if len(actions_after_latest_date) > 0:
                    self._ticker_action_repository.m_insert(actions_after_latest_date)
        except Exception as e:
            logger.error(f"failed to insert actions for {symbol}: {e}")
            raise e

    def sync_full_ticker_history(self, symbol: str):
        return self.sync_ticker_history(symbol, start_date=None, end_date=None)

    def sync_latest_ticker_history(self, symbol: str):
        try:
            latest_data = self._ticker_history_repository.get_latest(symbol)
            if latest_data is None:
                raise Exception(f"failed to get latest data for {symbol}")
            latest_date = TimeUtil.get_date_str(latest_data.time)
            if latest_date is None:
                raise Exception(f"no history data for {symbol}")
        except Exception as e:
            logger.info(f"failed to get history data for {symbol}: {e}")
            raise BaseException(f"failed to get latest date for {symbol}: {e}")

        return self.sync_ticker_history(symbol, start_date=latest_date, end_date=None)
