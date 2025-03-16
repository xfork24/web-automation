# coding: utf-8
# !./bin/python
# 淘宝店铺搜索任务，本程序长时间运行

from core import *

LOG_FILE_NAME = './logs/tb_shop_search_crawler_task.log'
UPDATE_ID = 'tb_shop_search_crawler_task'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    login_taobao()
    while True:
        # scan shop_search_crawl_task and get all unfinished tasks
        run_shop_search_crawler_task(UPDATE_ID)
        time.sleep(SHOP_SEARCH_CRAWL_NAP_IN_SECONDS)
