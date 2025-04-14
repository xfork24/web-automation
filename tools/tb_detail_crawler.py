# coding: utf-8
# #!./bin/python
# 抓取某个单一商品（提供商品链接和可选ID）的Detail页面信息，更新product_info表里的对应商品的如下字段：title_imgs, page_imgs, offer_details
# 若商品不存在，则创建新的product_info表记录，并写入商品信息

from core import *

LOG_FILE_NAME = './logs/tb_detail_crawler.log'
PRODUCT_IDS = ['908058032056']
UPDATE_ID = 'tb_detail_crawler'


def main():
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    tb_crawler = Crawler(headless=False)
    tb_crawler.login_taobao()
    for product_id in PRODUCT_IDS:
        try:
            product = ProductInfo.get(ProductInfo.product_id == product_id)
            tb_crawler.craw_taobao_detail_page(product.product_id, product.product_link, UPDATE_ID)
            tb_crawler.download_product_resources(product_id, UPDATE_ID)
        except DoesNotExist:
            logger.error(f'can not find product [{product_id}] in database')
        except Exception as e:
            logger.error(f'get unhandled exception {e}, just continue')
            traceback.print_exc()
            continue
    close_db()


if __name__ == '__main__':
    main()
