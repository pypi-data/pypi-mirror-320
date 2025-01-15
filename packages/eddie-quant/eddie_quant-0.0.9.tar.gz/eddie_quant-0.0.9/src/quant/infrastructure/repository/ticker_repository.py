from quant.domain.ticker.entity.ticker import Ticker
from quant.domain.ticker.repository.ticker_repository import TickerRepository as ITickerRepository
from quant.infrastructure.database.orm.ticker_po import TickerPO
from quant.infrastructure.database.ticker import TickerDatasourcePostgresql


class TickerRepository(ITickerRepository):
    def __init__(self, ticker_postgresql_datasource: TickerDatasourcePostgresql):
        self.ticker_postgresql_datasource = ticker_postgresql_datasource

    def insert(self, ticker: Ticker):
        return self.ticker_postgresql_datasource.insert(self._convert_entity_to_po(ticker))

    def m_insert(self, tickers: list[Ticker]):
        return self.ticker_postgresql_datasource.m_insert(self._convert_entity_list_to_po_list(tickers))

    def get(self, symbol: str) -> Ticker:
        return self._convert_po_to_entity(self.ticker_postgresql_datasource.get(symbol))

    def get_all(self) -> list[Ticker]:
        return self._convert_po_list_to_entity_list(self.ticker_postgresql_datasource.get_all())

    def get_by_symbols(self, symbols: list[str]) -> list[Ticker]:
        return self._convert_po_list_to_entity_list(self.ticker_postgresql_datasource.get_by_symbols(symbols))

    def _convert_entity_to_po(self, ticker: Ticker) -> TickerPO:
        return TickerPO(
            id=ticker.id,
            symbol=ticker.symbol,
            exchange=ticker.exchange,
            quote_type=ticker.quote_type,
            short_name=ticker.short_name,
            long_name=ticker.long_name,
        )

    def _convert_entity_list_to_po_list(self, tickers: list[Ticker]) -> list[TickerPO]:
        return list(map(self._convert_entity_to_po, tickers))

    def _convert_po_to_entity(self, po: TickerPO) -> Ticker:
        return Ticker(
            id=po.id,
            symbol=po.symbol,
            exchange=po.exchange,
            quote_type=po.quote_type,
            short_name=po.short_name,
            long_name=po.long_name,
        )

    def _convert_po_list_to_entity_list(self, ticker_po_list: list[TickerPO]) -> list[Ticker]:
        return list(map(self._convert_po_to_entity, ticker_po_list))
