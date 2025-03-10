# coding: utf-8
# !./bin/python
# 有些商品淘宝在搜索页面并没有展示销量，我们先通过页面搜索，然后再通过店铺内的商品信息来fix这些商品的销量和收入

from taobao import *

LOG_FILE_NAME = './logs/tb_fix_display_sale.log'
UPDATE_TIME_PERIOD_IN_SECONDS = 86400
SEARCH_CRAWL_GAP_IN_SECONDS = 10
SALE_ORDER = False
UPDATE_ID = 'tb_fix_display_sale'

if __name__ == '__main__':
    # scan product_info table to find illegal items with display_sale == -1 within time period
    # fix them by crawling shop page with target product id
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    login_taobao()
    start_ts = int(time.time()) - UPDATE_TIME_PERIOD_IN_SECONDS
    # 先用搜索法
    query = ProductInfo.select().where(ProductInfo.display_sale == -1,
                                       ProductInfo.update_ts > start_ts).order_by(ProductInfo.update_ts)
    ill_product_titles = [(ci.product_id, ci.product_title) for ci in query]
    for ill_product_id, ill_product_title in ill_product_titles:
        try:
            crawl_taobao_search_results(ill_product_title, 1, SALE_ORDER, UPDATE_ID, [ill_product_id])
        except Exception:
            logger.error(
                f'get unhandled exception while crawling search key [{ill_product_title}]')
            traceback.print_exc()
            continue
        time.sleep(SEARCH_CRAWL_GAP_IN_SECONDS)
    # 再用店铺法
    query = ProductInfo.select().where(ProductInfo.display_sale == -1,
                                       ProductInfo.update_ts > start_ts).order_by(ProductInfo.update_ts)
    ill_products = {}
    for ci in query:
        if ci.shop_name not in ill_products.keys():
            ill_products[ci.shop_name] = []
        ill_products[ci.shop_name].append(ci.product_id)
    for k, v in ill_products.items():
        try:
            exist_si = ShopInfo.get(ShopInfo.shop_name == k)
            craw_taobao_shop_page_results(exist_si.shop_link, UPDATE_ID, v)
        except DoesNotExist:
            logger.error(f'ShopInfo item with shop_name=[{k}] do not exist, just ignore')
            continue
        except Exception:
            logger.error(f'get unhandled exception while parse shop [{k}], shop page may be changed, just continue')
            traceback.print_exc()
            continue
