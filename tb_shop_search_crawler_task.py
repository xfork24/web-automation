# coding: utf-8
# !./bin/python
# 淘宝店铺搜索任务，本程序长时间运行

from taobao import *

LOG_FILE_NAME = './logs/tb_shop_search_crawler_task.log'
SHOP_SEARCH_CRAWL_GAP_IN_SECONDS = 10
SHOP_SEARCH_CRAWL_NAP_IN_SECONDS = 60
UPDATE_ID = 'tb_shop_search_crawler_task'
UPDATE_ROLE = 'tb_shop_search_crawler_task'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    login_taobao()
    while True:
        # scan shop_search_crawl_task and get all unfinished tasks
        start_ts = int(time.time()) - TB_SHOP_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS
        tasks = ShopSearchCrawlTask.select().where(ShopSearchCrawlTask.status != TASK_STATUS_DONE,
                                                   ShopSearchCrawlTask.status != TASK_STATUS_ARCHIVED,
                                                   ShopSearchCrawlTask.update_ts > start_ts).order_by(
            ShopSearchCrawlTask.update_ts)
        for task in tasks:
            task.try_count = task.try_count + 1
            update_task_status(task, TASK_STATUS_IN_PROGRESS, UPDATE_ID, UPDATE_ROLE)
            try:
                crawl_shop_link_by_search_results(task.shop_name, UPDATE_ID)
            except Exception:
                logger.error(f'get unhandled exception while crawling shop search [{task.shop_name}]')
                traceback.print_exc()
                update_task_status(task, TASK_STATUS_ERROR, UPDATE_ID, UPDATE_ROLE)
                continue
            update_task_status(task, TASK_STATUS_DONE, UPDATE_ID, UPDATE_ROLE)
            time.sleep(SHOP_SEARCH_CRAWL_GAP_IN_SECONDS)
        time.sleep(SHOP_SEARCH_CRAWL_NAP_IN_SECONDS)
