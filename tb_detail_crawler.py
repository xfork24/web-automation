# coding: utf-8
# #!./bin/python
# 抓取某个单一商品（提供商品链接和可选ID）的Detail页面信息，更新commodity_info表里的对应商品的如下字段：title_imgs, page_imgs, details
# 若商品不存在，则创建新的commodity_info表记录，并写入商品信息

from taobao import *

LOG_FILE_NAME = './logs/tb_detail_crawler.log'
UPDATE_ID = 'tb_detail_crawler'
TAOBAO_COMMODITY_LINK = 'https://item.taobao.com/item.htm?id=810884615884'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    craw_taobao_detail_page(TAOBAO_COMMODITY_LINK, UPDATE_ID, None)
