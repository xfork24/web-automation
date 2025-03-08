# coding: utf-8
# #!./bin/python
# 抓取某个单一商品（提供商品链接和可选ID）的Detail页面信息，更新commodity_info表里的对应商品的如下字段：title_imgs, page_imgs, details
# 若商品不存在，则创建新的commodity_info表记录，并写入商品信息

from taobao import *

LOG_FILE_NAME = './logs/tb_detail_crawler.log'
UPDATE_ID = 'tb_detail_crawler'
COMMODITY_IDS = ['885720370978', '885754626983', '887311224888']

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    login_taobao()
    for commodity_id in COMMODITY_IDS:
        try:
            commodity = CommodityInfo.get(CommodityInfo.id == commodity_id)
            logger.info(f'navigate to commodity [{commodity.id}] link: {commodity.link}')
            Driver.get(commodity.link)
            logger.info('wait detail page for seconds')
            time.sleep(DETAIL_PAGE_WAIT_IN_SECONDS)
            craw_taobao_detail_page_result(commodity.link, commodity.id, UPDATE_ID)
        except DoesNotExist:
            logger.error(f'can not find commodity [{commodity_id}] in database')
