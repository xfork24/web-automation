# coding: utf-8
# !./bin/python
# 通过搜索页抓到的商铺链接有些格式为非法，我们通过搜索店铺功能手动fix这些商铺的链接

from taobao import *

LOG_FILE_NAME = './logs/tb_fix_shop_link.log'
UPDATE_TIME_PERIOD_IN_SECONDS = 86400
UPDATE_ID = 'tb_fix_shop_link'

if __name__ == '__main__':
    # scan product_info table in update_ts order and update products within time period
    # only products with empty llm_analysis be updated
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    login_taobao()
    start_ts = int(time.time()) - UPDATE_TIME_PERIOD_IN_SECONDS
    shops = ShopInfo.select().where(ShopInfo.update_ts > start_ts).order_by(ShopInfo.update_ts)
    for shop in shops:
        if not re.match(SHOP_LINK_KNOWN_RE_EXP_LIST, shop.shop_link):
            crawl_shop_link_by_search_results(shop.shop_name, UPDATE_ID)
