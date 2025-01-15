from typing import Optional

from quant.domain.ticker.entity.ticker_action import TickerAction
from quant.domain.ticker.repository.ticker_action_repository import TickerActionRepository as ITickerActionRepository
from quant.infrastructure.database.orm.ticker_action_po import TickerActionPO
from quant.infrastructure.database.ticker_action import TickerActionDatasourcePostgresql


class TickerActionRepository(ITickerActionRepository):

    def __init__(self, ticker_action_datasource_postgresql: TickerActionDatasourcePostgresql):
        self._ticker_action_datasource_postgresql = ticker_action_datasource_postgresql

    def insert(self, ticker_action: TickerAction):
        return self._ticker_action_datasource_postgresql.insert(self._convert_entity_to_po(ticker_action))

    def m_insert(self, ticker_action_list: list[TickerAction]):
        return self._ticker_action_datasource_postgresql.m_insert(
            self._convert_entity_list_to_po_list(ticker_action_list))

    def get_all(self, symbol: str) -> list[TickerAction]:
        return self._convert_po_list_to_entity_list(self._ticker_action_datasource_postgresql.get_all(symbol))

    def get_by_date(self, symbol: str, start_date: str, end_date: str) -> list[TickerAction]:
        return self._convert_po_list_to_entity_list(
            self._ticker_action_datasource_postgresql.get_by_date(symbol, start_date, end_date))

    def get_latest_action(self, symbol: str) -> Optional[TickerAction]:
        record = self._ticker_action_datasource_postgresql.get_latest(symbol)
        if record is None:
            return None

        return self._convert_po_to_entity(self._ticker_action_datasource_postgresql.get_latest(symbol))

    def _convert_entity_to_po(self, entity: TickerAction) -> TickerActionPO:
        return TickerActionPO(
            symbol=entity.symbol,
            time=entity.time,
            dividend=entity.dividend,
            stock_split=entity.stock_split,
        )

    def _convert_entity_list_to_po_list(self, entity_list: list[TickerAction]) -> list[TickerActionPO]:
        return list(map(self._convert_entity_to_po, entity_list))

    def _convert_po_to_entity(self, record: TickerActionPO) -> TickerAction:
        return TickerAction(
            id=record.id,
            symbol=record.symbol,
            time=record.time,
            dividend=record.dividend,
            stock_split=record.stock_split,
        )

    def _convert_po_list_to_entity_list(self, record_list: list[TickerActionPO]) -> list[TickerAction]:
        return list(map(self._convert_po_to_entity, record_list))
