# coding: utf-8
# !./bin/python
# 大模型分析任务，本程序长时间运行

from taobao import *

LOG_FILE_NAME = './logs/tb_llm_analyze_task.log'
LLM_ANALYZE_GAP_IN_SECONDS = 10
LLM_TASK_SCAN_NAP_IN_SECONDS = 60
LLM_TASK_BATCH_SIZE = 10
UPDATE_ID = 'tb_llm_analyze_task'
UPDATE_ROLE = 'tb_llm_analyze_task'


def batch_update_task_status(batch, status, update_id, update_role):
    for p, t in batch:
        update_task_status(t, status, update_id, update_role)


if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    while True:
        product_task_batch = []
        # scan llm_analyze_task and get all unfinished tasks
        start_ts = int(time.time()) - TB_LLM_ANALYZE_TASK_PERIOD_IN_SECONDS
        tasks = LLMAnalyzeTask.select().where(LLMAnalyzeTask.status != TASK_STATUS_DONE,
                                              LLMAnalyzeTask.update_ts > start_ts).order_by(
            LLMAnalyzeTask.update_ts)
        for task in tasks:
            task.try_count = task.try_count + 1
            update_task_status(task, TASK_STATUS_IN_PROGRESS, UPDATE_ID, UPDATE_ROLE)
            try:
                if len(product_task_batch) >= LLM_TASK_BATCH_SIZE:
                    update_product_llm_analysis_batch([p for p, t in product_task_batch], UPDATE_ID)
                    batch_update_task_status(product_task_batch, TASK_STATUS_DONE, UPDATE_ID, UPDATE_ROLE)
                    product_task_batch = []
                    time.sleep(LLM_ANALYZE_GAP_IN_SECONDS)
                product_task_batch.append((Product(id=task.product_id, title=task.product_title), task))
            except Exception:
                logger.error(
                    f'get unhandled exception while analyzing llm products {[p for p, t in product_task_batch]}')
                traceback.print_exc()
                batch_update_task_status(product_task_batch, TASK_STATUS_ERROR, UPDATE_ID, UPDATE_ROLE)
                product_task_batch = []
                continue
        # handle last batch
        if len(product_task_batch) > 0:
            try:
                update_product_llm_analysis_batch([p for p, t in product_task_batch], UPDATE_ID)
                batch_update_task_status(product_task_batch, TASK_STATUS_DONE, UPDATE_ID, UPDATE_ROLE)
                product_task_batch = []
                time.sleep(LLM_ANALYZE_GAP_IN_SECONDS)
            except Exception:
                logger.error(
                    f'get unhandled exception while analyzing llm products {[p for p, t in product_task_batch]}')
                traceback.print_exc()
                batch_update_task_status(product_task_batch, TASK_STATUS_ERROR, UPDATE_ID, UPDATE_ROLE)
                product_task_batch = []
        time.sleep(LLM_TASK_SCAN_NAP_IN_SECONDS)
