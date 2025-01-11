import logging
from pathlib import Path

from workflow_builder.utils import get_data_stamp

logger = logging.getLogger()

def logger_init(log_dir: Path=None, color=False):
    console_handler = logging.StreamHandler()

    console_handler.setLevel(logging.DEBUG)

    if log_dir is not None:
        file_handler = logging.FileHandler(filename=log_dir / get_data_stamp(), mode='a', encoding='utf8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            fmt='[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        file_handler.close()

        if not logger.handlers:
            logger.addHandler(file_handler)

    if color:
        import colorlog

        log_colors_config = {
            'DEBUG': 'white',  # cyan white
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

        console_formatter = colorlog.ColoredFormatter(
            fmt='%(log_color)s[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S',
            log_colors=log_colors_config
        )
    else:
        console_formatter = logging.Formatter(
            fmt='[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S'
        )

    console_handler.setFormatter(console_formatter)
    console_handler.close()

    if not logger.handlers:
        logger.addHandler(console_handler)