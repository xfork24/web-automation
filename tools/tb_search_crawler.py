# coding: utf-8
# !./bin/python
# 给定搜索关键字，抓取指定页面数的商品基本信息，更新如下表：product_info, product_sales, shop_info

from core import *

SEARCH_KEYS = ['哪吒咤2之魔童闹海']
NUM_OF_PAGES_TO_PARSE = 1
UPDATE_ID = 'tb_search_crawler'
LOG_FILE_NAME = './logs/tb_search_crawler.log'


def main():
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    login_taobao()
    for key in SEARCH_KEYS:
        try:
            crawl_taobao_search_results(key, NUM_OF_PAGES_TO_PARSE, SEARCH_SALE_ORDER, UPDATE_ID)
        except Exception as e:
            logger.error(f'get unhandled exception {e}, just continue')
            traceback.print_exc()
            continue
    cleanup()


if __name__ == '__main__':
    main()
