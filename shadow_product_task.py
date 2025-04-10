# coding: utf-8
# !./bin/python
# ALL IN ONE 抓取任务，因为淘宝的登录认证，本程序长时间运行

from core import *
import signal

LOG_FILE_NAME = './logs/shadow_product_task.log'
UPDATE_ID = 'shadow_product_task'


def signal_handler(sig, frame):
    logger = get_logger()
    logger.info(f'signal={sig} captured with frame={frame}, will clean up resources and quit.')
    close_db()
    sys.exit(0)


if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    signal.signal(signal.SIGINT, signal_handler)
    pmt = ProductManageTaskRunner()
    pmt.login()
    while True:
        # scan search_crawl_task and get all unfinished tasks
        try:
            pmt.run_shadow_product_tasks(UPDATE_ID)
        except Exception as e:
            logger.error(f'get unhandled exception while execute run_shadow_product_tasks, {e}')
            traceback.print_exc()
        time.sleep(TASK_SCAN_WAIT_IN_SECONDS)
