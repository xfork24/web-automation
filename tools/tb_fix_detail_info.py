# coding: utf-8
# #!./bin/python
# 获取product_info表中更新时间在一段时间内的商品记录，若它的img和offer详细信息缺失，则抓取并更新product_info表

from taobao import *

LOG_FILE_NAME = './logs/tb_fix_detail_info.log'
UPDATE_TIME_PERIOD_IN_SECONDS = 86400
UPDATE_ID = 'tb_fix_detail_info'
ForceUpdate = False

if __name__ == '__main__':
    # scan product_info table in update_ts order and update products within time period
    # only products with empty info will be updated
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    start_ts = int(time.time()) - UPDATE_TIME_PERIOD_IN_SECONDS
    products = ProductInfo.select().where(ProductInfo.update_ts > start_ts).order_by(ProductInfo.update_ts)
    logger.info(f'get {len(products)} products to be updated by applying update_ts > {start_ts}')
    login_taobao()
    for product in products:
        if product.title_imgs != '' and product.page_imgs != '' and product.details != '' and not ForceUpdate:
            logger.info(f'product [{product.product_id}] information already updated, just ignore')
            continue
        logger.info(f'update product [{product.product_id}] with link [{product.product_link}]')
        try:
            craw_taobao_detail_page(product.product_link, product.product_id, UPDATE_ID)
        except Exception:
            logger.error('get unhandled exception while crawling product, just print error and continue')
            traceback.print_exc()
            continue
