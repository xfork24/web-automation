# coding: utf-8
# !./bin/python
# detail页面抓取任务，因为淘宝的登录认证，本程序长时间运行

from taobao import *

LOG_FILE_NAME = './logs/tb_detail_crawler_task.log'
UPDATE_TIME_PERIOD_IN_SECONDS = 86400
DETAIL_CRAWL_GAP_IN_SECONDS = 10
DETAIL_SCAN_NAP_IN_SECONDS = 60
UPDATE_ID = 'tb_detail_crawler_task'


def update_task_status(crawl_task, status):
    crawl_task.status = status
    crawl_task.save()


if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    login_taobao()
    while True:
        # scan detail_crawl_task and get all unfinished tasks
        start_ts = int(time.time()) - UPDATE_TIME_PERIOD_IN_SECONDS
        tasks = DetailCrawlTask.select().where(DetailCrawlTask.status != TASK_STATUS_DONE,
                                               DetailCrawlTask.update_ts > start_ts).order_by(
            DetailCrawlTask.update_ts)
        for task in tasks:
            try:
                task.try_count = task.try_count + 1
                update_task_status(task, TASK_STATUS_IN_PROGRESS)
                logger.info(f'navigate to product [{task.product_id}] link: {task.product_link}')
                Driver.get(task.product_link)
                logger.info('wait detail page for seconds')
                time.sleep(DETAIL_PAGE_WAIT_IN_SECONDS)
                craw_taobao_detail_page_result(task.product_link, task.product_id, UPDATE_ID)
                update_task_status(task, TASK_STATUS_DONE)
            except Exception:
                logger.error(f'get unhandled exception while crawling product [{task.product_id}]')
                traceback.print_exc()
                update_task_status(task, TASK_STATUS_ERROR)
                continue
            time.sleep(DETAIL_CRAWL_GAP_IN_SECONDS)
        time.sleep(DETAIL_SCAN_NAP_IN_SECONDS)
