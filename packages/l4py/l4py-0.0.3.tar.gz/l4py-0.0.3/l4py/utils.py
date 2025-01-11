import logging
import os

_LOG_LEVEL_PREFIX = 'PYTHON_LOG_LEVEL_'
_LOG_LEVEL_ROOT_KEY = f'{_LOG_LEVEL_PREFIX}ROOT'
_LOG_LEVEL_LOGGER_KEY_FORMAT = f'{_LOG_LEVEL_PREFIX}{{}}'

logging_env_vars = [
    {'key': key, 'value': value}
    for key, value in os.environ.items()
    if key.startswith(_LOG_LEVEL_PREFIX)
]
logging_env_vars.sort(key=lambda item: item['key'])


def get_app_name() -> str:
    return os.environ.get('PYTHON_APP_NAME', 'python-app')


def get_log_level_root() -> str:
    return os.environ.get(_LOG_LEVEL_ROOT_KEY, logging.INFO)


def get_log_level(logger_name: str) -> str:
    log_level = get_log_level_root()
    for key, value in [(v['key'], v['value']) for v in logging_env_vars]:
        if key.startswith(_LOG_LEVEL_PREFIX):
            logger_name_for_level = _LOG_LEVEL_LOGGER_KEY_FORMAT.format(logger_name)
            if key == logger_name_for_level:
                return value
            elif (logger_name_for_level).startswith(key + '.'):
                log_level = value
    return log_level


if __name__ == '__main__':
    logger_name = 'logger.name'
    os.environ.setdefault(f'{_LOG_LEVEL_PREFIX}logger', 'WARN')
    os.environ.setdefault(f'{_LOG_LEVEL_PREFIX}logger.name', 'INFO')
    os.environ.setdefault(f'{_LOG_LEVEL_PREFIX}logger.name_not', 'DEBUG')
    os.environ.setdefault(f'{_LOG_LEVEL_PREFIX}logger.name_n', 'FATAL')

    print(get_log_level('logger'))
    print(get_log_level('logger.name'))
    print(get_log_level('logger.name_not'))
    print(get_log_level('logger.name_n'))
    print(get_log_level('logger.name_naaaaa'))

    print(logging.getLevelNamesMapping())