# coding: utf-8
# !./bin/python
# search页面抓取任务，因为淘宝的登录认证，本程序长时间运行

from taobao import *

LOG_FILE_NAME = './logs/tb_search_crawler_task.log'
SEARCH_CRAWL_GAP_IN_SECONDS = 10
SEARCH_SCAN_NAP_IN_SECONDS = 60
SALE_ORDER = False
UPDATE_ID = 'tb_search_crawler_task'
UPDATE_ROLE = 'tb_search_crawler_task'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    login_taobao()
    while True:
        # scan search_crawl_task and get all unfinished tasks
        now_ts = int(time.time())
        start_ts = now_ts - TB_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS
        tasks = SearchCrawlTask.select().where(SearchCrawlTask.status != TASK_STATUS_DONE,
                                               SearchCrawlTask.update_ts > start_ts).order_by(
            SearchCrawlTask.update_ts)
        for task in tasks:
            task.try_count = task.try_count + 1
            update_task_status(task, TASK_STATUS_IN_PROGRESS, UPDATE_ID, UPDATE_ROLE)
            try:
                target_product_ids = json_loads(task.target_product_ids)
                crawl_taobao_search_results(task.search_key, task.num_of_pages, SALE_ORDER, UPDATE_ID,
                                            target_product_ids)
            except Exception:
                logger.error(
                    f'get unhandled exception while crawling search key [{task.search_key}] for {task.num_of_pages} pages')
                traceback.print_exc()
                update_task_status(task, TASK_STATUS_ERROR, UPDATE_ID, UPDATE_ROLE)
                continue
            update_task_status(task, TASK_STATUS_DONE, UPDATE_ID, UPDATE_ROLE)
            time.sleep(SEARCH_CRAWL_GAP_IN_SECONDS)
        analyze_and_generate_fix_tasks(now_ts, UPDATE_ID)
        time.sleep(SEARCH_SCAN_NAP_IN_SECONDS)
