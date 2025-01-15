from loguru import logger


class LoggerConfig:
    def __init__(self):
        _PATH = "./log/info.log"

        logger.add(sink=_PATH, format="{time} {level} {message}", rotation="1 day")
