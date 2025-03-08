# coding: utf-8
# !./bin/python
# shop页面抓取任务，因为淘宝的登录认证，本程序长时间运行

from taobao import *

LOG_FILE_NAME = './logs/tb_shop_crawler_task.log'
UPDATE_TIME_PERIOD_IN_SECONDS = 86400
SHOP_CRAWL_GAP_IN_SECONDS = 10
SHOP_SCAN_NAP_IN_SECONDS = 60
UPDATE_ID = 'tb_shop_crawler_task'


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
        tasks = ShopCrawlTask.select().where(ShopCrawlTask.status != TASK_STATUS_DONE,
                                             ShopCrawlTask.update_ts > start_ts).order_by(
            ShopCrawlTask.update_ts)
        for task in tasks:
            try:
                task.try_count = task.try_count + 1
                update_task_status(task, TASK_STATUS_IN_PROGRESS)
                logger.info(f'navigate to shop [{task.shop_name}] with link {task.link} and wait for seconds')
                Driver.get(task.link)
                time.sleep(SHOP_PAGE_WAIT_IN_SECONDS)
                craw_taobao_shop_page_results(task.link, UPDATE_ID)
                update_task_status(task, TASK_STATUS_DONE)
            except Exception:
                logger.error(
                    f'get unhandled exception while crawling shop [{task.shop_name}] with link {task.link} pages')
                traceback.print_exc()
                update_task_status(task, TASK_STATUS_ERROR)
                continue
            time.sleep(SHOP_CRAWL_GAP_IN_SECONDS)
        time.sleep(SHOP_SCAN_NAP_IN_SECONDS)
