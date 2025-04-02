# coding: utf-8
# !./bin/python
# 给定店铺链接，抓取店铺所有在售的商品，并更新如下表：product_info, product_sales, shop_info
# 或者，给定店铺链接和某个属于该店铺的商品ID列表，在店铺页面抓取该商品信息，并更新如下表：product_info, product_sales, shop_info

from core import *

SHOP_LINK = 'https://store.taobao.com/shop/view_shop.htm?appUid=RAzN8HWMHTzkvAS4XQz45FwxsqFwfLEkvHweQFi7uwBmoEYNGN7&spm=a21n57.1.item.20'
PRODUCT_IDS = ['899821701800']
LOG_FILE_NAME = './logs/tb_shop_crawler.log'
UPDATE_ID = 'tb_shop_crawler'


def main():
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    login_taobao()
    try:
        craw_taobao_shop_page(SHOP_LINK, SHOP_SALE_ORDER, UPDATE_ID, PRODUCT_IDS)
    except Exception as e:
        logger.error(f'get unhandled exception {e}, just continue')
        traceback.print_exc()
    cleanup()


if __name__ == '__main__':
    main()
