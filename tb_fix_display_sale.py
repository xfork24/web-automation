# coding: utf-8
# !./bin/python
# 有些商品淘宝在搜索页面并没有展示销量，我们通过店铺内的商品信息来fix这些商品的销量和收入

from taobao import *

LOG_FILE_NAME = './logs/tb_fix_display_sale.log'
UPDATE_TIME_PERIOD_IN_SECONDS = 86400
UPDATE_ID = 'tb_fix_display_sale'

if __name__ == '__main__':
    # scan commodity_info table to find illegal items with display_sale == -1 within time period
    # fix them by crawling shop page with target commodity id
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    start_ts = int(time.time()) - UPDATE_TIME_PERIOD_IN_SECONDS
    query = CommodityInfo.select().where(CommodityInfo.display_sale == -1,
                                         CommodityInfo.update_ts > start_ts).order_by(CommodityInfo.update_ts)
    illegal_commodities = {}
    for ci in query:
        if ci.shop_name not in illegal_commodities.keys():
            illegal_commodities[ci.shop_name] = []
        illegal_commodities[ci.shop_name].append(ci.id)
    login_taobao()
    for k, v in illegal_commodities.items():
        try:
            exist_si = ShopInfo.get(ShopInfo.name == k)
            logger.info('navigate to shop link and wait for seconds')
            Driver.get(exist_si.link)
            time.sleep(SHOP_PAGE_WAIT_IN_SECONDS)
            craw_taobao_shop_page_results(exist_si.link, UPDATE_ID, v)
        except DoesNotExist:
            logger.error(f'ShopInfo item with shop_name=[{k}] do not exist, just ignore')
            continue
        except Exception:
            logger.error('get unhandled exception, shop page may be changed, just continue')
            traceback.print_exc()
            continue
