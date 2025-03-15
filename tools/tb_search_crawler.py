# coding: utf-8
# !./bin/python
# 给定搜索关键字，抓取指定页面数的商品基本信息，更新如下表：product_info, product_sales, shop_info

from taobao import *

SEARCH_KEYS = ['歌曲剪辑消音伴奏降调加主旋律背景配乐音乐音频制作处理混音修音']
NUM_OF_PAGES_TO_PARSE = 3
SALE_ORDER = False
UPDATE_ID = 'tb_search_crawler'
LOG_FILE_NAME = './logs/tb_search_crawler.log'


def main():
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    login_taobao()
    for key in SEARCH_KEYS:
        try:
            crawl_taobao_search_results(key, NUM_OF_PAGES_TO_PARSE, SALE_ORDER, UPDATE_ID)
        except Exception as e:
            logger.error(f'get unhandled exception {e}, just continue')
            traceback.print_exc()
            continue
    return


if __name__ == '__main__':
    main()
