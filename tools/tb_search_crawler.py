# coding: utf-8
# !./bin/python
# 给定搜索关键字，抓取指定页面数的商品基本信息，更新如下表：product_info, product_sales, shop_info

from taobao import *

QUERY_STRING = '歌曲剪辑消音伴奏降调加主旋律背景配乐音乐音频制作处理混音修音'
NUM_OF_PAGES_TO_PARSE = 10
SALE_ORDER = False
UPDATE_ID = 'tb_search_crawler'
LOG_FILE_NAME = './logs/tb_search_crawler.log'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    craw_taobao_search_page(QUERY_STRING, NUM_OF_PAGES_TO_PARSE, SALE_ORDER, UPDATE_ID)
