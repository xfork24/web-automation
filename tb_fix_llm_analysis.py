# coding: utf-8
# !./bin/python
# 抓取最近一段时间更新的product_info记录，若llm_analysis内容为空，或强制更新，则调用llm更新分析信息

from taobao import *

LOG_FILE_NAME = './logs/tb_fix_llm_analysis.log'
UPDATE_TIME_PERIOD_IN_SECONDS = 86400
LLM_BATCH_WAIT_IN_SECONDS = 10
LLM_QUERY_BATCH_SIZE = 10
UPDATE_ID = 'tb_fix_llm_analysis'
ForceUpdate = False


def update_product_llm_analysis_batch(products, update_id):
    response = parse_product_list_by_dsr1_70b(products)
    ts = int(time.time())
    for record in response.infos:
        llm_analysis = {
            'keyword': record.keyword,
            'category': record.category,
            'digital': record.digital,
        }
        logger.info(f'update product [{record.id}] with llm_analysis = {llm_analysis}')
        exist_ci = ProductInfo.get(ProductInfo.product_id == record.id)
        exist_ci.llm_analysis = llm_analysis
        exist_ci.update_id = update_id
        exist_ci.update_role = update_product_llm_analysis_batch.__name__
        exist_ci.update_ts = ts
        exist_ci.save()


if __name__ == '__main__':
    # scan product_info table in update_ts order and update products within time period
    # only products with empty llm_analysis be updated
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    start_ts = int(time.time()) - UPDATE_TIME_PERIOD_IN_SECONDS
    products = ProductInfo.select().where(ProductInfo.update_ts > start_ts).order_by(ProductInfo.update_ts)
    logger.info(f'get {len(products)} products to be updated by applying update_ts > {start_ts}')
    product_batch = []
    for product in products:
        if product.llm_analysis != '' and not ForceUpdate:
            logger.info(f'product [{product.product_id}] llm analysis already updated, just ignore')
            continue
        if len(product_batch) == LLM_QUERY_BATCH_SIZE:
            update_product_llm_analysis_batch(product_batch, UPDATE_ID)
            product_batch = []
            logger.info('wait LLM tokens ready for seconds')
            time.sleep(LLM_BATCH_WAIT_IN_SECONDS)
        product_batch.append(Product(id=product.product_id, title=product.title))
    # the last batch
    if len(product_batch) > 0:
        update_product_llm_analysis_batch(product_batch, UPDATE_ID)
