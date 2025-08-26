import logging
import os
import sys
import re


class SensitiveDataFormatter(logging.Formatter):
    @staticmethod
    def _filter(s):
        s = re.sub(r'-auth "(.*?)"', r'-auth "uxxxxx:pxxxxx"', s)
        s = re.sub(r'-u "(.*?)"', r'-u "uxxxxx:pxxxxx"', s)
        s = re.sub(r'"Authorization: Bearer (.*?)"', r'"Authorization: Bearer xxxxxxxxxxxxxxxxxx"', s)
        return s

    def format(self, record):
        original = logging.Formatter.format(self, record)
        return self._filter(original)


def build_logging(log_file, log_level):
    try:
        format_str = "%(asctime)s - %(filename)s - %(module)s - %(funcName)s - line:%(lineno)d - %(process)d - %(thread)d - %(levelname)s - %(message)s"

        # stream handler
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(SensitiveDataFormatter(format_str))

        # file handler
        file_handler = logging.FileHandler(log_file, 'a')
        file_handler.setFormatter(SensitiveDataFormatter(format_str))

        application_log = logging.getLogger(__name__)
        application_log.handlers = []
        application_log.addHandler(stream_handler)
        application_log.addHandler(file_handler)

        application_log.setLevel(log_level)

        return application_log
    except Exception as e:
        logging.shutdown()
        raise e


def get_log_level(log_level):
    logging_level = {'FATAL': logging.FATAL, 'CRITICAL': logging.CRITICAL, 'ERROR': logging.ERROR, 'WARNING': logging.WARNING, 'INFO': logging.INFO, 'DEBUG': logging.DEBUG, 'NOTSET': logging.NOTSET}

    try:
        return logging_level.get(log_level.upper())
    except Exception as e:
        raise e


def setup_kcaf_product_service_logging(kcaf_service_dict: dict, service: str, module: str, log_level_from_command_line: str, log_path: str):
    log_file_name = module + '.log'

    logging_path = log_path + service + '/'

    if os.path.exists(logging_path) and os.path.isdir(logging_path):
        pass
    else:
        os.makedirs(logging_path)
    log_file = os.path.join(logging_path + log_file_name)

    if log_level_from_command_line is None:
        log_level = kcaf_service_dict['logging_level']
    else:
        log_level = log_level_from_command_line
    logging_level = get_log_level(log_level)

    return build_logging(log_file, logging_level)


def setup_kcaf_server_service_logging(service_name: str, module: str, log_level: str, log_path: str):
    log_file_name = module + '.log'

    logging_path = log_path + service_name + '/'

    if os.path.exists(logging_path) and os.path.isdir(logging_path):
        pass
    else:
        os.makedirs(logging_path)
    log_file = os.path.join(logging_path + log_file_name)

    logging_level = get_log_level(log_level)

    return build_logging(log_file, logging_level)
