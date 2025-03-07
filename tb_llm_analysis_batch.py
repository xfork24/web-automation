# coding: utf-8
# !./bin/python
# 抓取最近一段时间更新的commodity_info记录，若llm_analysis内容为空，或强制更新，则调用llm更新分析信息

from taobao import *

LOG_FILE_NAME = './logs/tb_llm_analysis.log'
UPDATE_TIME_PERIOD_IN_SECONDS = 86400
LLM_BATCH_WAIT_IN_SECONDS = 10
LLM_QUERY_BATCH_SIZE = 10
UPDATE_ID = 'tb_llm_analysis_batch'
ForceUpdate = False


def update_commodity_llm_analysis_batch(products, update_id):
    response = parse_product_list_by_dsr1_70b(products)
    ts = int(time.time())
    for record in response.infos:
        llm_analysis = {
            'keyword': record.keyword,
            'category': record.category,
            'digital': record.digital,
        }
        logger.info(f'update commodity [{record.id}] with llm_analysis = {llm_analysis}')
        exist_ci = CommodityInfo.get(CommodityInfo.id == record.id)
        exist_ci.llm_analysis = llm_analysis
        exist_ci.update_id = update_id
        exist_ci.update_role = update_commodity_llm_analysis_batch.__name__
        exist_ci.update_ts = ts
        exist_ci.save()


if __name__ == '__main__':
    # scan commodity_info table in update_ts order and update commodities within time period
    # only commodities with empty llm_analysis be updated
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    start_ts = int(time.time()) - UPDATE_TIME_PERIOD_IN_SECONDS
    commodities = CommodityInfo.select().where(CommodityInfo.update_ts > start_ts).order_by(CommodityInfo.update_ts)
    logger.info(f'get {len(commodities)} commodities to be updated by applying update_ts > {start_ts}')
    product_batch = []
    for commodity in commodities:
        if commodity.llm_analysis != '' and not ForceUpdate:
            logger.info(f'commodity [{commodity.id}] llm analysis already updated, just ignore')
            continue
        if len(product_batch) == LLM_QUERY_BATCH_SIZE:
            update_commodity_llm_analysis_batch(product_batch, UPDATE_ID)
            product_batch = []
            logger.info('wait LLM tokens ready for seconds')
            time.sleep(LLM_BATCH_WAIT_IN_SECONDS)
        product_batch.append(Product(id=commodity.id, title=commodity.title))
    # the last batch
    if len(product_batch) > 0:
        update_commodity_llm_analysis_batch(product_batch, UPDATE_ID)
