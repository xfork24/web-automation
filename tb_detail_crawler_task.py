# coding: utf-8
# !./bin/python
# detail页面抓取任务，因为淘宝的登录认证，本程序长时间运行

from taobao import *

LOG_FILE_NAME = './logs/tb_detail_crawler_task.log'
DETAIL_CRAWL_GAP_IN_SECONDS = 10
DETAIL_SCAN_NAP_IN_SECONDS = 60
UPDATE_ID = 'tb_detail_crawler_task'
UPDATE_ROLE = 'tb_detail_crawler_task'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    login_taobao()
    while True:
        # scan detail_crawl_task and get all unfinished tasks
        start_ts = int(time.time()) - TB_DETAIL_CRAWL_TASK_PERIOD_IN_SECONDS
        tasks = DetailCrawlTask.select().where(DetailCrawlTask.status != TASK_STATUS_DONE,
                                               DetailCrawlTask.status != TASK_STATUS_ARCHIVED,
                                               DetailCrawlTask.update_ts > start_ts).order_by(
            DetailCrawlTask.update_ts)
        for task in tasks:
            task.try_count = task.try_count + 1
            update_task_status(task, TASK_STATUS_IN_PROGRESS, UPDATE_ID, UPDATE_ROLE)
            try:
                craw_taobao_detail_page_result(task.product_link, task.product_id, UPDATE_ID)
            except Exception:
                logger.error(f'get unhandled exception while crawling product [{task.product_id}]')
                traceback.print_exc()
                update_task_status(task, TASK_STATUS_ERROR, UPDATE_ID, UPDATE_ROLE)
                continue
            update_task_status(task, TASK_STATUS_DONE, UPDATE_ID, UPDATE_ROLE)
            time.sleep(DETAIL_CRAWL_GAP_IN_SECONDS)
        time.sleep(DETAIL_SCAN_NAP_IN_SECONDS)
