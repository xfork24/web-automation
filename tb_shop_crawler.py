# coding: utf-8
# !./bin/python
# 给定店铺链接，抓取店铺所有在售的商品，并更新如下表：commodity_info, commodity_sales, shop_info

from taobao import *

SHOP_LINK = 'https://pub3j449bi05z91rrq9g0rdk2cllz3f.taobao.com/shop/view_shop.htm?appUid=RAzN8HWMpyiDM8qfpXyYbtArqUPjk8Tnq8AC3EwXkEQHMJZ6cxJ&spm=a21n57.1.hoverItem.2'
LOG_FILE_NAME = './logs/tb_shop_crawler.log'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    craw_taobao_shop_page(SHOP_LINK)
