# coding: utf-8
# !./bin/python

import math
import sys
import logging
import easyocr
import pytesseract
from json import dumps, loads
from PIL import Image
from core.exceptions import PriceOCRError
from jsondiff import diff

TESSERACT_PRICE_OCR_CONFIG = '--psm 7 --oem 1 tessedit_char_whitelist=0123456789.'
PYOCR_PRICE_ALLOW_LIST = '0123456789.'


def init_logger(log_format, file, level, debug):
    if debug:
        logging.basicConfig(format=log_format, stream=sys.stdout, level=level)
    else:
        logging.basicConfig(format=log_format, filename=file, level=level)
    logging.info(
        f'logger inited with format={log_format}, file={"sys.stdout" if debug else file}, level={level}, debug = {debug}')


def get_logger(module_name=__name__):
    logger = logging.getLogger(module_name)
    return logger


def json_dumps(content):
    return dumps(content, ensure_ascii=False)


def json_loads(content):
    return loads(content)


def json_diff(a, b):
    return diff(a, b, marshal=True)


def resize_image(file_path):
    img = Image.open(file_path)
    ratio = max(1, math.ceil(800 / img.size[0]), math.ceil(800 / img.size[1]))
    img.resize((img.size[0] * ratio, img.size[1] * ratio)).save(file_path)


class OcrParser:
    def __init__(self):
        self.logger = get_logger()
        self.logger.info('initialize EasyOCRReader ...')
        self.easyOcrReader = easyocr.Reader(['en'])

    def parse_price_ocr_by_pytesseract(self, image_file_path, config=TESSERACT_PRICE_OCR_CONFIG):
        price_raw = pytesseract.image_to_string(Image.open(image_file_path), config=config).strip(' \t\r\n')
        price = 0 if price_raw == '' else int(float(price_raw) * 100)
        if price == 0:
            msg = f'parse_price_ocr_by_pytesseract failed with price_raw={price_raw} while handling file={image_file_path}, config={config}'
            self.logger.error(msg)
            raise PriceOCRError(msg)
        self.logger.info(
            f'parse_price_ocr_by_pytesseract parsed price_raw={price_raw}, price={price} while handling file={image_file_path}, config={config}')
        return price

    def parse_price_ocr_by_pyocr(self, image_file_path, allowlist=PYOCR_PRICE_ALLOW_LIST):
        result = self.easyOcrReader.readtext(image_file_path, allowlist=allowlist)
        if len(result) != 1:
            msg = f'parse_price_ocr_by_pyocr failed with result={result} while parsing {image_file_path}, allowlist={allowlist}'
            self.logger.error(msg)
            raise PriceOCRError(msg)
        price_raw = result[0][1].strip(' \t\r\n')
        price = 0 if price_raw == '' else int(float(price_raw) * 100)
        if price == 0:
            msg = f'parse_price_ocr_by_pyocr failed with result={result}, price_raw={price_raw} while parsing {image_file_path}, allowlist={allowlist}'
            self.logger.error(msg)
            raise PriceOCRError(msg)
        self.logger.info(
            f'parse_price_ocr_by_pyocr parsed result={result}, price_raw={price_raw}, price={price} while parsing {image_file_path}, allowlist={allowlist}')
        return price

    def par_price_ocr(self, image_file_path):
        try:
            return self.parse_price_ocr_by_pyocr(image_file_path)
        except PriceOCRError:
            pass
        try:
            return self.parse_price_ocr_by_pytesseract(image_file_path)
        except PriceOCRError:
            pass
        raise PriceOCRError()
