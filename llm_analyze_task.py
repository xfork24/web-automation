# coding: utf-8
# !./bin/python
# 大模型分析任务，本程序长时间运行

from core import *

LOG_FILE_NAME = './logs/llm_analyze_task.log'
UPDATE_ID = 'llm_analyze_task'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    while True:
        # scan llm_analyze_task and get all unfinished tasks
        try:
            run_llm_analyze_tasks(UPDATE_ID)
        except Exception as e:
            logger.error(f'get unhandled exception while execute run_all_in_one_crawler_task, {e}')
            traceback.print_exc()
        time.sleep(LLM_TASK_SCAN_NAP_IN_SECONDS)
