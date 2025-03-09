# coding: utf-8
# !./bin/python
# search页面抓取任务，因为淘宝的登录认证，本程序长时间运行

from taobao import *

LOG_FILE_NAME = './logs/tb_search_crawler_task.log'
UPDATE_TIME_PERIOD_IN_SECONDS = 86400
SEARCH_CRAWL_GAP_IN_SECONDS = 10
SEARCH_SCAN_NAP_IN_SECONDS = 60
SALE_ORDER = False
UPDATE_ID = 'tb_search_crawler_task'


def update_task_status(crawl_task, status):
    crawl_task.status = status
    crawl_task.save()


if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    login_taobao()
    while True:
        # scan search_crawl_task and get all unfinished tasks
        start_ts = int(time.time()) - UPDATE_TIME_PERIOD_IN_SECONDS
        tasks = SearchCrawlTask.select().where(SearchCrawlTask.status != TASK_STATUS_DONE,
                                               SearchCrawlTask.update_ts > start_ts).order_by(
            SearchCrawlTask.update_ts)
        for task in tasks:
            task.try_count = task.try_count + 1
            update_task_status(task, TASK_STATUS_IN_PROGRESS)
            try:
                crawl_taobao_search_results(task.search_key, task.num_of_pages, SALE_ORDER, UPDATE_ID)
            except Exception:
                logger.error(
                    f'get unhandled exception while crawling search key [{task.search_key}] for {task.num_of_pages} pages')
                traceback.print_exc()
                update_task_status(task, TASK_STATUS_ERROR)
                continue
            update_task_status(task, TASK_STATUS_DONE)
            time.sleep(SEARCH_CRAWL_GAP_IN_SECONDS)
        time.sleep(SEARCH_SCAN_NAP_IN_SECONDS)
