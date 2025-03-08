# coding: utf-8
# !./bin/python
# 后台抓取任务入口

from taobao import *

LOG_FILE_NAME = './logs/tb_crawler_task.log'
UPDATE_ID = 'tb_crawler_task'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
