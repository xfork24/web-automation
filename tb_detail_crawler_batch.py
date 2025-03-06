# coding: utf-8
# #!./bin/python
# 获取commodity_info表中更新时间在一段时间内的商品记录，若它的img和offer详细信息缺失，则抓取并更新commodity_info表

from taobao import *

LOG_FILE_NAME = './logs/tb_detail_crawler_batch.log'
UPDATE_TIME_PERIOD_IN_SECONDS = 86400
UPDATE_ID = 'tb_detail_crawler_batch'
ForceUpdate = False

if __name__ == '__main__':
    # scan commodity_info table in update_ts desc order and update commodities within time period
    # only commodities with empty info will be updated
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    start_ts = int(time.time()) - UPDATE_TIME_PERIOD_IN_SECONDS
    commodities = CommodityInfo.select().where(CommodityInfo.update_ts > start_ts)
    logger.info(f'get {len(commodities)} commodities to be updated by applying update_ts > {start_ts}')
    login_taobao()
    for commodity in commodities:
        if commodity.title_imgs != '' and commodity.page_imgs != '' and commodity.details != '' and not ForceUpdate:
            logger.info(f'commodity [{commodity.id}] information already updated, just ignore')
            continue
        logger.info(f'update commodity [{commodity.id}], link = {commodity.link}')
        logger.info('navigate to commodity link')
        Driver.get(commodity.link)
        logger.info('wait detail page for seconds')
        time.sleep(DETAIL_PAGE_WAIT_IN_SECONDS)
        try:
            craw_taobao_detail_page_result(commodity.link, commodity.id, UPDATE_ID)
        except Exception:
            logger.error('get unhandled exception while crawling commodity, just print error and continue')
            traceback.print_exc()
            continue
