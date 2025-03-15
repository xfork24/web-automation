# coding: utf-8
# !./bin/python
# shop页面抓取任务，因为淘宝的登录认证，本程序长时间运行

from taobao import *

LOG_FILE_NAME = './logs/tb_shop_crawler_task.log'
UPDATE_ID = 'tb_shop_crawler_task'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    login_taobao()
    while True:
        # scan search_crawl_task and get all unfinished tasks
        run_shop_crawler_tasks()
        time.sleep(SHOP_SCAN_NAP_IN_SECONDS)
