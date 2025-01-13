import logging


def setup_logger(name, log_file, level=logging.INFO):

    formatter = logging.Formatter("{asctime} - {levelname} - {message}",
                                  style="{",
                                  datefmt="%Y-%m-%d %H:%M")

    log_console_handler = logging.StreamHandler()
    log_file_handler = logging.FileHandler(log_file,
                                           mode="a",
                                           encoding="utf-8")

    log_console_handler.setFormatter(formatter)
    log_file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(log_console_handler)
    logger.addHandler(log_file_handler)
    logger.setLevel(10)

    return logger
