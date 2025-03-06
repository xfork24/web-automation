# coding: utf-8
# !./bin/python

import sys
import logging
import easyocr
import pytesseract
from PIL import Image
from taobao.exceptions import PriceOCRError

TESSERACT_PRICE_OCR_CONFIG = '--psm 7 --oem 1 tessedit_char_whitelist=0123456789.'
PYOCR_PRICE_ALLOW_LIST = '0123456789.'

EasyOcrReader = easyocr.Reader(['en'])


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


def parse_price_ocr_by_pytesseract(image_file_path, config=TESSERACT_PRICE_OCR_CONFIG):
    price = pytesseract.image_to_string(Image.open(image_file_path), config=config).strip(' \t\r\n')
    price = 0 if price == '' else int(float(price) * 100)
    if price == 0:
        raise PriceOCRError()
    return price


def parse_price_ocr_by_pyocr(image_file_path):
    result = EasyOcrReader.readtext(image_file_path, allowlist=PYOCR_PRICE_ALLOW_LIST)
    result_size = len(result)
    if result_size == 0 or result_size > 1:
        raise PriceOCRError()
    price = result[0][1].strip(' \t\r\n')
    price = 0 if price == '' else int(float(price) * 100)
    if price == 0:
        raise PriceOCRError()
    return price
