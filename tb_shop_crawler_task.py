# coding: utf-8
# !./bin/python
# shop页面抓取任务，因为淘宝的登录认证，本程序长时间运行

from taobao import *

LOG_FILE_NAME = './logs/tb_shop_crawler_task.log'
SHOP_CRAWL_GAP_IN_SECONDS = 10
SHOP_SCAN_NAP_IN_SECONDS = 60
UPDATE_ID = 'tb_shop_crawler_task'
UPDATE_ROLE = 'tb_shop_crawler_task'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    login_taobao()
    while True:
        # scan search_crawl_task and get all unfinished tasks
        start_ts = int(time.time()) - TB_SHOP_CRAWL_TASK_PERIOD_IN_SECONDS
        tasks = ShopCrawlTask.select().where(ShopCrawlTask.status != TASK_STATUS_DONE,
                                             ShopCrawlTask.status != TASK_STATUS_ARCHIVED,
                                             ShopCrawlTask.update_ts > start_ts).order_by(
            ShopCrawlTask.update_ts)
        for task in tasks:
            task.try_count = task.try_count + 1
            update_task_status(task, TASK_STATUS_IN_PROGRESS, UPDATE_ID, UPDATE_ROLE)
            try:
                logger.info(f'handling shop crawl task [{task.id}] with shop_name [{task.shop_name}]')
                shop = ShopInfo.get(ShopInfo.shop_name == task.shop_name)
                target_product_ids = json_loads(task.target_product_ids)
                craw_taobao_shop_page_results(shop.shop_link, UPDATE_ID, target_product_ids)
            except DoesNotExist:
                logger.error(f'shop_info record with shop_name [{task.shop_name}] does not exist, just ignore')
                continue
            except Exception:
                logger.error(
                    f'get unhandled exception while crawling shop [{task.shop_name}] with link {task.product_link} pages')
                traceback.print_exc()
                update_task_status(task, TASK_STATUS_ERROR, UPDATE_ID, UPDATE_ROLE)
                continue
            update_task_status(task, TASK_STATUS_DONE, UPDATE_ID, UPDATE_ROLE)
            time.sleep(SHOP_CRAWL_GAP_IN_SECONDS)
        time.sleep(SHOP_SCAN_NAP_IN_SECONDS)
