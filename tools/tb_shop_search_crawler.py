# coding: utf-8
# !./bin/python
# 通过搜索页抓到的商铺链接有些格式为非法，我们通过搜索店铺功能手动fix这些商铺的链接

from core import *

LOG_FILE_NAME = './logs/tb_fix_shop_link.log'
UPDATE_TIME_PERIOD_IN_SECONDS = 86400
SHOP_NAMES = ['一只猫生活店']
UPDATE_ID = 'tb_shop_search_crawler'


def main():
    # scan product_info table in update_ts order and update products within time period
    # only products with empty llm_analysis be updated
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    tb_crawler = Crawler(headless=False)
    tb_crawler.login_taobao()
    for shop_name in SHOP_NAMES:
        try:
            tb_crawler.crawl_taobao_shop_link_by_search(shop_name, UPDATE_ID)
        except Exception as e:
            logger.error(f'get unhandled exception {e}, just continue')
            traceback.print_exc()
            continue
    close_db()


if __name__ == '__main__':
    main()
