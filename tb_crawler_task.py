# coding: utf-8
# !./bin/python
# ALL IN ONE 抓取任务，因为淘宝的登录认证，本程序长时间运行

from taobao import *

LOG_FILE_NAME = './logs/tb_crawler_task.log'
UPDATE_ID = 'tb_crawler_task'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    login_taobao()
    while True:
        # scan search_crawl_task and get all unfinished tasks
        run_all_in_one_crawler_task(UPDATE_ID)
        time.sleep(ALL_IN_ONE_SCAN_NAP_IN_SECONDS)
