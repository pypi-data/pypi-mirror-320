import threading
import time

from loguru import logger

from quant.application.service.ticker_data_service import TickerDataService
from quant.application.service.ticker_data_sync_service import TickerDataSyncService
from quant.domain.ticker.entity.ticker import Ticker


class AppService:
    def __init__(self, ticker_data_sync_service: TickerDataSyncService, ticker_data_service: TickerDataService):
        self.__ticker_data_sync_service = ticker_data_sync_service
        self.__ticker_data_service = ticker_data_service

    def add_ticker(self, symbols: list[str]) -> list[str]:
        """
        Add
        :param symbols:
        :return: failed symbols
        """
        failed_symbols = []
        for symbol in symbols:
            try:
                self.__ticker_data_sync_service.add_ticker(symbol)
            except Exception as e:
                failed_symbols.append(symbol)
                logger.warning(f"failed adding {symbol} to db")

        return failed_symbols

    def update_tickers_data(self):
        tickers = self.__ticker_data_service.get_all_tickers()
        threads = []

        for ticker in tickers:
            t = threading.Thread(target=self.update_ticker_data, args=(ticker.symbol,))
            threads.append(t)
            t.start()
            logger.info(f"start to update ticker data for {ticker.symbol}")
            time.sleep(0.5)

        for t in threads:
            t.join()

        logger.info(f"finish updating ticker data for {[ticker.symbol for ticker in tickers]}")

    def update_ticker_data(self, symbol: str):
        price_history_latest_date = self.__ticker_data_service.get_history_latest_date(symbol=symbol)
        if price_history_latest_date is None:
            self.__ticker_data_sync_service.sync_full_ticker_history(symbol)
        else:
            self.__ticker_data_sync_service.sync_latest_ticker_history(symbol)
        logger.info(f"finish updating ticker history data for {symbol}")

        self.__ticker_data_sync_service.sync_ticker_action(symbol)

    def get_all_tickers(self) -> list[Ticker]:
        return self.__ticker_data_service.get_all_tickers()
