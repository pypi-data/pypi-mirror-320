import logging
from logging import Logger

def setup_logger(logger_name: str, level: str='INFO') -> Logger:
    """
    Sets up and configures a logger with the specified name and logging level. The logger is
    configured to write logs to the console, and formats log messages including the module
    name, log level, function name, and the message. If the logger already has handlers, it
    does not add new ones.

    The function prevents the logger from propagating messages to the root logger.

    Parameters:
        logger_name (str): The name assigned to the logger.
        level (str, optional): The logging level to set for the logger. Defaults to 'INFO'.
            Supported levels are 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.

    Returns:
        Logger: The configured logger instance.

    Raises:
        ValueError: If the provided log level is invalid.
    """
    if level == 'DEBUG':
        level = logging.DEBUG
    elif level == 'INFO':
        level = logging.INFO
    elif level == 'WARNING':
        level = logging.WARNING
    elif level == 'ERROR':
        level = logging.ERROR
    elif level == 'CRITICAL':
        level = logging.CRITICAL
    else:
        raise ValueError(f"Invalid log level : {level}")

    # 로거 생성
    logger = logging.getLogger(logger_name)

    # 이미 핸들러가 추가된 경우 새로 추가하지 않음
    if not logger.hasHandlers():
        logger.setLevel(level)

        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # 포맷터 설정
        formatter = logging.Formatter('%(module)s / %(levelname)s / func(%(funcName)s) / %(message)s')
        console_handler.setFormatter(formatter)

        # 핸들러를 로거에 추가
        logger.addHandler(console_handler)
    else:
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)
    # 루트 로거로의 전파 방지
    logger.propagate = False
    return logger


mylogger = setup_logger('utils_logger', 'INFO')