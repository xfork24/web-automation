# coding: utf-8
# #!./bin/python

import re
import traceback
from json import dumps

from taobao import *

LOG_FILE_NAME = './logs/tb_detail_crawler.log'

TAOBAO_COMMODITY_LINK = 'https://item.taobao.com/item.htm?abbucket=9&id=858551205874&ns=1&pisk=gGUseeO0E-UefGB0xRfEOFvH0L0jC67yCIGYZSLwMV3tHkNuhA5cjVrIhJeIBF5GjmHbIVn0bxkZhqN0F6WPzaPgsq0OUT7rzBAgF4YvkjpqpBhjlfQ18M5Tsq0AhB8A4aNgeU3qghhx96GqghLYHcndJjHKMh3YHvnKwb-xk-3AO2hS6ChtDmKppjkpHhLx6e3KGjK9HFHAOWHnMqHYHcLu9FGF1vV16gxvjH_xM5HBkEU1ocM7un8Xllhtf4NtdWPURfisFDl991a7w5UoGrfJcxN4XRl3ha6IJPw_WDgfle0aNkesAl6XRDqLZrnQxTtuZ5e_20UOR6ebp7qoWPBD7AqY9rHUWs8jeuPoRX4VKFHbvoUZjqvOCXa_NrZf498rF1pBcBiklXMPO6tDm3Iu6ZkPUUXoXXcF361B4SmttXGhO6tDmchnTy1CO3zd.&priceTId=2150498517409260645331720e1a90&skuId=5838180867013&spm=a21n57.1.hoverItem.2&utparam=%7B%22aplus_abtest%22%3A%22a290208925248e6d2b601a269d3b98b2%22%7D&xxc=taobaoSearch'
COMMODITY_ID = '858551205874'


if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    craw_taobao_detail_page(TAOBAO_COMMODITY_LINK, COMMODITY_ID)
