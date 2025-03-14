# coding: utf-8
# #!./bin/python
# 抓取某个单一商品（提供商品链接和可选ID）的Detail页面信息，更新product_info表里的对应商品的如下字段：title_imgs, page_imgs, details
# 若商品不存在，则创建新的product_info表记录，并写入商品信息

from taobao import *

LOG_FILE_NAME = './logs/tb_detail_crawler.log'
UPDATE_ID = 'tb_detail_crawler'
PRODUCT_IDS = ['885720370978', '885754626983', '887311224888']

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    login_taobao()
    for product_id in PRODUCT_IDS:
        try:
            product = ProductInfo.get(ProductInfo.product_id == product_id)
            craw_taobao_detail_page(product.product_link, product.product_id, UPDATE_ID)
        except DoesNotExist:
            logger.error(f'can not find product [{product_id}] in database')
