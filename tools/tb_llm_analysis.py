# coding: utf-8
# !./bin/python
# 抓取最近一段时间更新的product_info记录，若llm_analysis内容为空，或强制更新，则调用llm更新分析信息

from core import *

LOG_FILE_NAME = './logs/tb_fix_llm_analysis.log'
UPDATE_TIME_PERIOD_IN_SECONDS = 86400
LLM_BATCH_WAIT_IN_SECONDS = 10
LLM_QUERY_BATCH_SIZE = 10
UPDATE_ID = 'tb_llm_analysis'
ForceUpdate = False


def main():
    # scan product_info table in update_ts order and update products within time period
    # only products with empty llm_analysis be updated
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    start_ts = int(time.time()) - UPDATE_TIME_PERIOD_IN_SECONDS
    products = ProductInfo.select().where(ProductInfo.update_ts > start_ts).order_by(ProductInfo.update_ts)
    logger.info(f'get {len(products)} products to be updated by applying update_ts > {start_ts}')
    product_batch = []
    for product in products:
        additional_properties = json_loads(product.additional_properties)
        if LLM_ANALYSIS_KEY not in additional_properties.keys() and not ForceUpdate:
            logger.info(f'product [{product.product_id}] llm analysis already updated, just ignore')
            continue
        if len(product_batch) == LLM_QUERY_BATCH_SIZE:
            update_product_llm_analysis_batch(product_batch, UPDATE_ID)
            product_batch = []
            logger.info('wait LLM tokens ready for seconds')
            time.sleep(LLM_BATCH_WAIT_IN_SECONDS)
        product_batch.append(Product(id=product.product_id, title=product.product_title))
    # the last batch
    if len(product_batch) > 0:
        update_product_llm_analysis_batch(product_batch, UPDATE_ID)
    cleanup()


if __name__ == '__main__':
    main()
