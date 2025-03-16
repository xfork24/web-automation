# coding: utf-8
# !./bin/python
# detail页面抓取任务，因为淘宝的登录认证，本程序长时间运行

from core import *

LOG_FILE_NAME = './logs/tb_detail_crawler_task.log'
UPDATE_ID = 'tb_detail_crawler_task'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    login_taobao()
    while True:
        # scan detail_crawl_task and get all unfinished tasks
        run_detail_crawler_tasks(UPDATE_ID)
        time.sleep(DETAIL_SCAN_NAP_IN_SECONDS)
