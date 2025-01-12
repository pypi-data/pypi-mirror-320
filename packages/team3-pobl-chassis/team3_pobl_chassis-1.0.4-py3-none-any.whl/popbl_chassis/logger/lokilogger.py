import logging
from logging.config import dictConfig
from multiprocessing import Queue
import json

from logging_loki import LokiQueueHandler


class LokiLogger:
    
    @classmethod
    async def create(cls):
        self=LokiLogger()
        return self
    
    @staticmethod
    def create_handler(app_name, app_env, loki_host):
        loki_handler = LokiQueueHandler(
            Queue(),
            url=f"http://{loki_host}:3100/loki/api/v1/push",
            tags={"app": app_name, "env": app_env},
            version="1",
        )
        return  loki_handler

    @staticmethod
    def setup_logging(loki_handler: LokiQueueHandler, json_formatter):

        logging_config = {
            "version": 1,
            "formatters": {
                "json": {
                    "()": json_formatter
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "level": "DEBUG",
                },
                "loki": {
                    "()": lambda: loki_handler,
                    "formatter": "json",
                    "level": "INFO",
                }
            },
            "loggers": {
                "app_logger": {
                    "level": "DEBUG",
                    "handlers": ["console", "loki"],
                    "propagate": False
                }
            }
        }
        dictConfig(logging_config)
        return logging.getLogger("app_logger")