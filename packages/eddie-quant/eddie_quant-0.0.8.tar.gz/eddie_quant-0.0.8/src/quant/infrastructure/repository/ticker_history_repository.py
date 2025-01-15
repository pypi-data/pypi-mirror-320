from typing import Optional

from quant.domain.ticker.entity.ticker_history import TickerHistory
from quant.domain.ticker.repository.ticker_history_repository import TickerHistoryRepository as ITickerHistoryRepository
from quant.infrastructure.database.ticker_history import TickerHistoryDatasourcePostgresql
from quant.infrastructure.database.orm.ticker_history_po import TickerHistoryPO as TickerHistoryPO


class TickerHistoryRepository(ITickerHistoryRepository):
    def __init__(self, ticker_history_datasource_postgresql: TickerHistoryDatasourcePostgresql):
        self.ticker_history_datasource_postgresql = ticker_history_datasource_postgresql

    def insert(self, price_record: TickerHistory):
        return self.ticker_history_datasource_postgresql.insert(self._convert_entity_to_po(price_record))

    def m_insert(self, price_records: list[TickerHistory]):
        return self.ticker_history_datasource_postgresql.m_insert(self._convert_entity_list_to_po_list(price_records))

    def get_all(self, symbol: str) -> list[TickerHistory]:
        return self._convert_po_list_to_entity_list(self.ticker_history_datasource_postgresql.get_all(symbol))

    def get_by_date(self, symbol: str, start_date: str, end_date: str) -> list[TickerHistory]:
        return self._convert_po_list_to_entity_list(
            self.ticker_history_datasource_postgresql.get_by_date(symbol, start_date, end_date))

    def get_latest(self, symbol: str) -> Optional[TickerHistory]:
        record = self.ticker_history_datasource_postgresql.get_latest(symbol)
        if record is None:
            return None
        return self._convert_po_to_entity(record)

    def _convert_entity_to_po(self, ticker_history: TickerHistory) -> TickerHistoryPO:
        return TickerHistoryPO(
            symbol=ticker_history.symbol,
            time=ticker_history.time,
            interval=ticker_history.interval,

            open=ticker_history.open,
            high=ticker_history.high,
            low=ticker_history.low,
            close=ticker_history.close,
            volume=ticker_history.volume,
        )

    def _convert_entity_list_to_po_list(self, ticker_history_list: list[TickerHistory]) -> list[TickerHistoryPO]:
        return list(map(self._convert_entity_to_po, ticker_history_list))

    def _convert_po_to_entity(self, ticker_history_po: TickerHistoryPO) -> TickerHistory:
        return TickerHistory(
            id=ticker_history_po.id,
            symbol=ticker_history_po.symbol,
            time=ticker_history_po.time,
            interval=ticker_history_po.interval,
            open=ticker_history_po.open,
            high=ticker_history_po.high,
            low=ticker_history_po.low,
            close=ticker_history_po.close,
            volume=ticker_history_po.volume,
        )

    def _convert_po_list_to_entity_list(self, ticker_history_po_list: list[TickerHistoryPO]) -> list[TickerHistory]:
        return list(map(self._convert_po_to_entity, ticker_history_po_list))
