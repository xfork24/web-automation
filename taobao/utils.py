# coding: utf-8
# !./bin/python

import sys
import logging


def init_logger(log_format, file, level, debug):
    if debug:
        logging.basicConfig(format=log_format, stream=sys.stdout, level=level)
    else:
        logging.basicConfig(format=log_format, filename=file, level=level)


def get_logger(module_name=__name__):
    logger = logging.getLogger(module_name)
    return logger
