# coding: utf-8
# !./bin/python

import sys
import logging
import pytesseract
from PIL import Image
from taobao.exceptions import PriceOCRGetEmptyError

TESSERACT_PRICE_OCR_OPTIONS = "--psm 6 --oem 3 tessedit_char_whitelist=0123456789."


def init_logger(log_format, file, level, debug):
    if debug:
        logging.basicConfig(format=log_format, stream=sys.stdout, level=level)
    else:
        logging.basicConfig(format=log_format, filename=file, level=level)


def get_logger(module_name=__name__):
    logger = logging.getLogger(module_name)
    return logger


def parse_price_unit(unit):
    if unit == '¥':
        return 'CNY'
    return unit


def parse_price(price):
    return int(float(price) * 100)


def parse_price_ocr(image_file_path):
    price = pytesseract.image_to_string(Image.open(image_file_path), config=TESSERACT_PRICE_OCR_OPTIONS)
    price = price.strip(' \t\r\n')
    try:
        assert (price != '')
    except AssertionError:
        raise PriceOCRGetEmptyError()
    return int(float(price) * 100)
