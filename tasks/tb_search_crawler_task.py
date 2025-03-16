# coding: utf-8
# !./bin/python
# search页面抓取任务，因为淘宝的登录认证，本程序长时间运行

from core import *

LOG_FILE_NAME = './logs/tb_search_crawler_task.log'
UPDATE_ID = 'tb_search_crawler_task'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    login_taobao()
    while True:
        # scan search_crawl_task and get all unfinished tasks
        task_ts = run_search_crawler_task(UPDATE_ID)
        analyze_and_generate_fix_tasks(task_ts, UPDATE_ID)
        time.sleep(SEARCH_SCAN_NAP_IN_SECONDS)
