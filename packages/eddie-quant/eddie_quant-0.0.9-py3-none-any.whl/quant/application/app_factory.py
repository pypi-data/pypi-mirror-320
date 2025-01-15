from dataclasses import dataclass

from quant.application.app import AppService
from quant.application.service.ticker_data_service import TickerDataService
from quant.application.service.ticker_data_sync_service import TickerDataSyncService
from quant.infrastructure.database.engine import Engine
from quant.infrastructure.database.ticker import TickerDatasourcePostgresql
from quant.infrastructure.database.ticker_action import TickerActionDatasourcePostgresql
from quant.infrastructure.database.ticker_history import TickerHistoryDatasourcePostgresql
from quant.infrastructure.external_service.yfinance.yfinance import YFinanceRepository
from quant.infrastructure.repository.ticker_action_repository import TickerActionRepository
from quant.infrastructure.repository.ticker_history_repository import TickerHistoryRepository
from quant.infrastructure.repository.ticker_repository import TickerRepository


@dataclass
class Config:
    sql_alchemy_url: str


class AppFactory:
    def __init__(self):
        pass

    @staticmethod
    def init_app(config: Config) -> AppService:
        if not config.sql_alchemy_url:
            raise Exception('sql_alchemy_url must be set in config')

        engine = Engine(config.sql_alchemy_url)
        ticker_datasource_postgresql = TickerDatasourcePostgresql(engine=engine)
        ticker_action_datasource_postgresql = TickerActionDatasourcePostgresql(engine=engine)
        ticker_history_datasource_postgresql = TickerHistoryDatasourcePostgresql(engine=engine)
        ticker_repository = TickerRepository(ticker_postgresql_datasource=ticker_datasource_postgresql)
        ticker_action_repository = TickerActionRepository(
            ticker_action_datasource_postgresql=ticker_action_datasource_postgresql)
        ticker_history_repository = TickerHistoryRepository(
            ticker_history_datasource_postgresql=ticker_history_datasource_postgresql)
        ticker_data_service = TickerDataService(ticker_repository=ticker_repository,
                                                history_repository=ticker_history_repository,
                                                ticker_action_repository=ticker_action_repository)

        yfinance_repository = YFinanceRepository()
        ticker_data_sync_service = TickerDataSyncService(ticker_repository=ticker_repository,
                                                         yfinance_repository=yfinance_repository,
                                                         ticker_history_repository=ticker_history_repository,
                                                         ticker_action_repository=ticker_action_repository)

        app_service = AppService(ticker_data_sync_service=ticker_data_sync_service,
                                 ticker_data_service=ticker_data_service)
        return app_service
