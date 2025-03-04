# coding: utf-8
# !./bin/python
# 给定店铺链接，抓取店铺所有在售的商品，并更新如下表：commodity_info, commodity_sales, shop_info

from taobao import *

SHOP_LINK = 'https://store.taobao.com/shop/view_shop.htm?appUid=RAzN8HWRxZTrW5haRwSz3Yk69AKoC7RPhnSPiAEbhP4zsxBGsoZ&amp;spm=a21n57.1.item.2'
LOG_FILE_NAME = './logs/tb_shop_crawler.log'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    craw_taobao_shop_page(SHOP_LINK)
