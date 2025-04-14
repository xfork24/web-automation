# coding: utf-8
# !./bin/python
# shop页面抓取任务，因为淘宝的登录认证，本程序长时间运行

from core import *

LOG_FILE_NAME = './logs/tb_shop_crawler_task.log'
UPDATE_ID = 'tb_shop_crawler_task'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    ctr = CrawlTaskRunner(headless=False)
    ctr.login()
    while True:
        # scan search_crawl_task and get all unfinished tasks
        ctr.run_shop_crawler_tasks(UPDATE_ID, force=True)
        time.sleep(TASK_SCAN_WAIT_IN_SECONDS)
