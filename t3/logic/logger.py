import logging


class Logger(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        print(f"[{record.levelname:7}] {record.msg}")

    @classmethod
    def setup(cls):
        logger = logging.getLogger()
        logger.addHandler(cls())
        logger.setLevel(logging.INFO)
