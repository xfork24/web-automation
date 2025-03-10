# coding: utf-8
# !./bin/python
# 大模型分析任务，本程序长时间运行

from taobao import *

LOG_FILE_NAME = './logs/tb_llm_analyze_task.log'
LLM_ANALYZE_GAP_IN_SECONDS = 10
LLM_TASK_SCAN_NAP_IN_SECONDS = 60
UPDATE_ID = 'tb_llm_analyze_task'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    while True:
        # scan llm_analyze_task and get all unfinished tasks
        start_ts = int(time.time()) - TB_LLM_ANALYZE_TASK_PERIOD_IN_SECONDS
        tasks = LLMAnalyzeTask.select().where(LLMAnalyzeTask.status != TASK_STATUS_DONE,
                                              LLMAnalyzeTask.update_ts > start_ts).order_by(
            LLMAnalyzeTask.update_ts)
        for task in tasks:
            task.try_count = task.try_count + 1
            update_task_status(task, TASK_STATUS_IN_PROGRESS)
            try:
                products = [Product(id=p.id, title=p.title) for p in json_loads(task.products)]
                update_product_llm_analysis_batch(products, UPDATE_ID)
            except Exception:
                logger.error(f'get unhandled exception while analyzing llm products [{task.products}]')
                traceback.print_exc()
                update_task_status(task, TASK_STATUS_ERROR)
                continue
            update_task_status(task, TASK_STATUS_DONE)
            time.sleep(LLM_ANALYZE_GAP_IN_SECONDS)
        time.sleep(LLM_TASK_SCAN_NAP_IN_SECONDS)
