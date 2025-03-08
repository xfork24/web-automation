# coding: utf-8
# !./bin/python

from taobao.models import *

TB_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS = 604800
TB_SHOP_CRAWL_TASK_PERIOD_IN_SECONDS = 604800
TB_DETAIL_CRAWL_TASK_PERIOD_IN_SECONDS = 604800
TB_SHOP_AGGREGATE_TOPN = 10
TB_SHOP_REVENUE_THRESHOLD = 10000
TB_SKU_AGGREGATE_TOPN = 50
TB_SKU_REVENUE_THRESHOLD = 1000


# 对于预定义搜索词，如果一段时间内没有存在的任务，则添加搜索任务
# 同样的search_key忽略num_of_pages的不同，认为任务存在，无视任务的状态
def analyze_and_add_search_crawl_tasks(search_key, num_of_pages, update_id):
    logger = get_logger()
    start_ts = int(time.time()) - TB_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS
    query = SearchCrawlTask.select().where(SearchCrawlTask.search_key == search_key,
                                           SearchCrawlTask.update_ts > start_ts).order_by(
        SearchCrawlTask.update_ts).limit(1)
    if query.count() > 0:
        logger.info(f'search crawl task [{query[0].id}] already exist for search_key [{search_key}], just ignore')
        return
    add_search_crawl_task(search_key, num_of_pages, TASK_STATUS_NEW, update_id,
                          analyze_and_add_search_crawl_tasks.__name__)


# 获取一段时间内的商品最新销量和销售数据，按店铺聚合，若满足一定条件，且没有已存在的任务，则添加搜索任务
def analyze_and_add_shop_crawl_tasks(update_id, top_n=TB_SHOP_AGGREGATE_TOPN,
                                     revenue_threshold=TB_SHOP_REVENUE_THRESHOLD):
    logger = get_logger()
    start_ts = int(time.time()) - TB_SHOP_CRAWL_TASK_PERIOD_IN_SECONDS
    cf_query = CommodityInfo.select(CommodityInfo.shop_name,
                                    fn.AVG(CommodityInfo.display_price).alias('avg_price'),
                                    fn.SUM(CommodityInfo.display_sale).alias('total_sale'),
                                    fn.SUM(CommodityInfo.estimated_revenue).alias('total_revenue')).group_by(
        CommodityInfo.shop_name).order_by(fn.SUM(CommodityInfo.estimated_revenue).desc())
    idx = 0
    for q in cf_query:
        if idx > top_n and q.total_revenue < revenue_threshold * 100:
            break
        idx += 1
        query = ShopCrawlTask.select().where(ShopCrawlTask.shop_name == q.shop_name,
                                             ShopCrawlTask.update_ts > start_ts).order_by(
            ShopCrawlTask.update_ts).limit(1)
        if query.count() > 0:
            logger.info(f'shop crawl task [{query[0].id}] already exist for shop_name [{q.shop_name}], just ignore')
            continue
        try:
            exist_si = ShopInfo.get(ShopInfo.name == q.shop_name)
            add_shop_crawl_task(exist_si.name, exist_si.link, TASK_STATUS_NEW, update_id,
                                analyze_and_add_shop_crawl_tasks.__name__)
        except DoesNotExist:
            logger.error(f'ShopInfo item with shop_name=[{q.shop_name}] do not exist, just ignore')
            continue


# 获取一段时间内的商品最新销量和销售数据，若满足一定条件，且没有已存在的任务，则添加搜索任务
def analyze_and_add_detail_crawl_tasks(update_id, top_n=TB_SKU_AGGREGATE_TOPN,
                                       revenue_threshold=TB_SKU_REVENUE_THRESHOLD):
    logger = get_logger()
    start_ts = int(time.time()) - TB_DETAIL_CRAWL_TASK_PERIOD_IN_SECONDS
    cf_query = CommodityInfo.select().order_by(CommodityInfo.estimated_revenue.desc())
    idx = 0
    for cf in cf_query:
        if idx > top_n and cf.estimated_revenue < revenue_threshold * 100:
            # 我们暂时不分析商品销量历史数据，因为这逻辑上相当于年度均线，且淘宝给出的信息很含糊
            break
        idx += 1
        query = DetailCrawlTask.select().where(DetailCrawlTask.commodity_id == cf.id,
                                               DetailCrawlTask.update_ts > start_ts).order_by(
            DetailCrawlTask.update_ts).limit(1)
        if query.count() > 0:
            logger.info(f'detail crawl task [{query[0].id}] already exist for commodity_id [{cf.id}], just ignore')
            continue
        add_detail_crawl_task(cf.id, cf.link, TASK_STATUS_NEW, update_id,
                              analyze_and_add_detail_crawl_tasks.__name__)


# 这里假设商品相关信息已经抓取并更新到commodity_info表中了，否则不继续进行
def analyze_and_add_hot_products():
    pass
