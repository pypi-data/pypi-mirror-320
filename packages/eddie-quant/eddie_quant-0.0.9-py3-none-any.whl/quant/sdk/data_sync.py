import os

from quant.application import app_factory
from quant.application.app_factory import Config


class DataSync:
    @staticmethod
    def run():
        database_url = os.environ['DATABASE_URL']
        config = Config(
            sql_alchemy_url=database_url,
        )

        app = app_factory.AppFactory.init_app(config)
        app.update_tickers_data()
