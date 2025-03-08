# coding: utf-8
# !./bin/python

from taobao.models import *
from uuid import uuid4

TB_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS = 604800
TB_SHOP_CRAWL_TASK_PERIOD_IN_SECONDS = 604800
TB_DETAIL_CRAWL_TASK_PERIOD_IN_SECONDS = 604800
TB_SHOP_AGGREGATE_TOPN = 10


# 对于预定义搜索词，如果一段时间内没有存在的任务，则添加搜索任务
# 同样的search_key忽略num_of_pages的不同，认为任务存在，无视任务的状态
def analyze_and_add_search_crawl_tasks(search_key, num_of_pages, update_id):
    logger = get_logger()
    start_ts = int(time.time()) - TB_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS
    query = SearchCrawlTask.select().where(SearchCrawlTask.search_key == search_key,
                                           SearchCrawlTask.update_ts > start_ts).order_by(
        SearchCrawlTask.update_ts).limit(1)
    if query.count() > 0:
        logger.info(f'search crawl task [{query[0].id}] already exist, just ignore')
        return
    add_search_crawl_task(search_key, num_of_pages, TASK_STATUS_NEW, update_id,
                          analyze_and_add_search_crawl_tasks.__name__)


# 获取topn销量的店铺信息
def aggregate_shop_sales(top_n=TB_SHOP_AGGREGATE_TOPN):
    pass


# 获取一段时间内的商品最新销量和销售数据，按店铺聚合，若满足一定条件，且没有已存在的任务，则添加搜索任务
def analyze_and_add_shop_crawl_tasks():
    pass


# 获取一段时间内的商品最新销量和销售数据，若满足一定条件，且没有已存在的任务，则添加搜索任务
def analyze_and_add_detail_crawl_tasks():
    pass


def analyze_and_add_hot_products():
    pass
