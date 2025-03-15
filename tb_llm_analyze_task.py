# coding: utf-8
# !./bin/python
# 大模型分析任务，本程序长时间运行

from taobao import *

LOG_FILE_NAME = './logs/tb_llm_analyze_task.log'
UPDATE_ID = 'tb_llm_analyze_task'


if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    while True:
        # scan llm_analyze_task and get all unfinished tasks
        run_llm_analyze_tasks(UPDATE_ID)
        time.sleep(LLM_TASK_SCAN_NAP_IN_SECONDS)
