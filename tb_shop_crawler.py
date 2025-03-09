# coding: utf-8
# !./bin/python
# 给定店铺链接，抓取店铺所有在售的商品，并更新如下表：product_info, product_sales, shop_info
# 或者，给定店铺链接和某个属于该店铺的商品ID列表，在店铺页面抓取该商品信息，并更新如下表：product_info, product_sales, shop_info

from taobao import *

SHOP_LINK = 'https://shop436316857.taobao.com/?spm=pc_detail.29232929.shop_block.dshopinfo.510e7dd6F8xYxA'
UPDATE_ID = 'tb_shop_crawler'
PRODUCT_IDS = ['850288018462']
LOG_FILE_NAME = './logs/tb_shop_crawler.log'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    craw_taobao_shop_page(SHOP_LINK, UPDATE_ID, PRODUCT_IDS)
