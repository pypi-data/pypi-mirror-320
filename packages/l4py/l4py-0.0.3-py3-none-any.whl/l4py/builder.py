import logging
import os
import platform
from logging.handlers import RotatingFileHandler

from l4py import utils
from l4py.formatters import TextFormatter, JsonFormatter


class LogBuilder:
    __text_formatter = TextFormatter()
    __json_formatter = JsonFormatter()

    __console_format = None
    __console_json = False
    __console_level = None

    __file = None
    __file_format = None
    __file_json = True
    __file_level = None
    __file_max_size = 10 * 1024 * 1024  # 10 MB (default)
    __file_max_count = 5  # Default 5 backup files

    def text_formatter(self, text_formatter: logging.Formatter) -> 'LogBuilder':
        self.__text_formatter = text_formatter
        return self

    def json_formatter(self, json_formatter: logging.Formatter) -> 'LogBuilder':
        self.__json_formatter = json_formatter
        return self

    def console_format(self, format_str: str) -> 'LogBuilder':
        self.__console_format = format_str
        return self

    def console_json(self, value: bool) -> 'LogBuilder':
        self.__console_json = value
        return self

    def console_level(self, level: int) -> 'LogBuilder':
        self.__console_level = level
        return self

    def file(self, file_name: str) -> 'LogBuilder':
        self.__file = file_name
        return self

    def file_format(self, format_str: str) -> 'LogBuilder':
        self.__file_format = format_str
        return self

    def file_json(self, value: bool) -> 'LogBuilder':
        self.__file_json = value
        return self

    def file_level(self, level: int) -> 'LogBuilder':
        self.__file_level = level
        return self

    def file_max_size_mb(self, size_in_mb: int) -> 'LogBuilder':
        self.__file_max_size = size_in_mb * 1024 * 1024
        return self

    def file_max_count(self, count: int) -> 'LogBuilder':
        self.__file_max_count = count
        return self

    def build(self, logger_name: str = 'python-app') -> logging.Logger:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        console_handler = self.__build_console_handler(logger_name)
        logger.addHandler(console_handler)

        if self.__file:
            file_handler = self.__build_file_handler(logger_name)
            logger.addHandler(file_handler)

        return logger

    def __build_console_handler(self, logger_name: str) -> logging.Handler:
        console_handler = logging.StreamHandler()
        log_level = self.__console_level
        if log_level is None:
            log_level = utils.get_log_level(logger_name)
        console_handler.setLevel(log_level)
        if self.__console_format:
            console_formatter = logging.Formatter(self.__console_format)
        elif self.__console_json:
            console_formatter = self.__json_formatter
        else:
            console_formatter = self.__text_formatter
        console_handler.setFormatter(console_formatter)
        return console_handler

    def __build_file_handler(self, logger_name: str) -> logging.Handler:
        file_handler = RotatingFileHandler(
            self.__file,
            maxBytes=self.__file_max_size,
            backupCount=self.__file_max_count
        )
        log_level = self.__file_level
        if log_level is None:
            log_level = utils.get_log_level(logger_name)
        file_handler.setLevel(log_level)
        if self.__file_format:
            file_formatter = logging.Formatter(self.__file_format)
        elif self.__file_json:
            file_formatter = self.__json_formatter
        else:
            file_formatter = self.text_formatter
        file_handler.setFormatter(file_formatter)
        return file_handler


class DjangoLogBuilder:
    __text_formatter = TextFormatter()
    __json_formatter = JsonFormatter()

    __console_json = False

    __file = f'{utils.get_app_name()}-{platform.uname()}.log'
    __file_json = True
    __file_max_size = 10 * 1024 * 1024  # 10 MB (default)
    __file_max_count = 5  # Default 5 backup files

    def console_json(self, value: bool) -> 'DjangoLogBuilder':
        self.__console_json = value
        return self

    def file(self, file_name: str) -> 'DjangoLogBuilder':
        self.__file = file_name
        return self

    def file_json(self, value: bool) -> 'DjangoLogBuilder':
        self.__file_json = value
        return self

    def file_max_size_mb(self, size_in_mb: int) -> 'DjangoLogBuilder':
        self.__file_max_size = size_in_mb * 1024 * 1024
        return self

    def file_max_count(self, count: int) -> 'DjangoLogBuilder':
        self.__file_max_count = count
        return self

    def build_config_4_django(self, django_log_level=None, show_sql=False) -> dict:
        django_log_level = django_log_level if django_log_level else utils.get_log_level_root()
        django_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': self.__file,
                    'maxBytes': self.__file_max_size,
                    'backupCount': self.__file_max_count,
                    'formatter': 'json',
                },
            },
            'root': {
                'level': utils.get_log_level_root(),
                "handlers": [
                    "console",
                    "file"
                ]
            },
            'loggers': {
                'django': {
                    'level': django_log_level,
                    'propagate': False,
                },
                'django.db.backends': {
                    'handlers': ['console', 'file'],
                    'level': 'DEBUG' if show_sql else django_log_level,
                    'propagate': False,
                },
            },
            'formatters': {
                'json': {
                    '()': f'{JsonFormatter.__module__}.{JsonFormatter.__name__}',
                },
                'default': {
                    '()': f'{TextFormatter.__module__}.{TextFormatter.__name__}',
                },
            },
        }
        return django_config
