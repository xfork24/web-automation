# coding: utf-8
# !./bin/python

from taobao.llm import *
from taobao.models import *

TB_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS = 604800
TB_SHOP_CRAWL_TASK_PERIOD_IN_SECONDS = 604800
TB_DETAIL_CRAWL_TASK_PERIOD_IN_SECONDS = 604800
TB_SHOP_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS = 604800
TB_LLM_ANALYZE_TASK_PERIOD_IN_SECONDS = 604800
TB_SHOP_REVENUE_TOPN = 10
TB_SHOP_REVENUE_THRESHOLD = 10000
TB_SKU_REVENUE_TOPN = 50
TB_SKU_REVENUE_THRESHOLD = 1000
LLM_QUERY_BATCH_SIZE = 10


# 对于预定义搜索词，如果一段时间内没有存在的任务，则添加搜索任务
# 同样的search_key忽略num_of_pages的不同，认为任务存在，无视任务的状态
def analyze_and_add_search_crawl_tasks(search_key, num_of_pages, update_id):
    logger = get_logger()
    start_ts = int(time.time()) - TB_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS
    query = SearchCrawlTask.select().where(SearchCrawlTask.search_key == search_key,
                                           SearchCrawlTask.update_ts > start_ts).order_by(
        SearchCrawlTask.update_ts).limit(1)
    if query.count() > 0:
        logger.info(
            f'search crawl task [{query[0].id}] already exist for search_key [{search_key}], just ignore')
        return
    add_search_crawl_task(search_key, num_of_pages, [], {}, update_id,
                          analyze_and_add_search_crawl_tasks.__name__)


# 获取一段时间内的商品最新销量和销售数据，按店铺聚合，若满足一定条件，且没有已存在的任务，则添加搜索任务
def analyze_and_add_shop_crawl_tasks(update_id, top_n=TB_SHOP_REVENUE_TOPN,
                                     revenue_threshold=TB_SHOP_REVENUE_THRESHOLD):
    logger = get_logger()
    start_ts = int(time.time()) - TB_SHOP_CRAWL_TASK_PERIOD_IN_SECONDS
    pi_query = ProductInfo.select(ProductInfo.shop_name,
                                  fn.AVG(ProductInfo.display_price).alias('avg_price'),
                                  fn.SUM(ProductInfo.display_sale).alias('total_sale'),
                                  fn.SUM(ProductInfo.estimated_revenue).alias('total_revenue')).group_by(
        ProductInfo.shop_name).order_by(fn.SUM(ProductInfo.estimated_revenue).desc())
    idx = 0
    for pi in pi_query:
        if idx > top_n and pi.total_revenue < revenue_threshold * 100:
            break
        idx += 1
        query = ShopCrawlTask.select().where(ShopCrawlTask.shop_name == pi.shop_name,
                                             ShopCrawlTask.update_ts > start_ts).order_by(
            ShopCrawlTask.update_ts).limit(1)
        if query.count() > 0:
            logger.info(
                f'shop crawl task [{query[0].id}] already exist for shop_name [{pi.shop_name}], just ignore')
            continue
        try:
            exist_si = ShopInfo.get(ShopInfo.shop_name == pi.shop_name)
            add_shop_crawl_task(exist_si.shop_name, [], {}, update_id,
                                analyze_and_add_shop_crawl_tasks.__name__)
        except DoesNotExist:
            logger.error(f'ShopInfo item with shop_name=[{pi.shop_name}] do not exist, just ignore')
            continue


# 获取一段时间内的商品最新销量和销售数据，若满足一定条件，且没有已存在的任务，则添加搜索任务
def analyze_and_add_detail_crawl_tasks(update_id, top_n=TB_SKU_REVENUE_TOPN,
                                       revenue_threshold=TB_SKU_REVENUE_THRESHOLD):
    logger = get_logger()
    start_ts = int(time.time()) - TB_DETAIL_CRAWL_TASK_PERIOD_IN_SECONDS
    pi_query = ProductInfo.select().order_by(ProductInfo.estimated_revenue.desc())
    idx = 0
    for pi in pi_query:
        if idx > top_n and pi.estimated_revenue < revenue_threshold * 100:
            # 我们暂时不分析商品销量历史数据，因为这逻辑上相当于年度均线，且淘宝给出的信息很含糊
            break
        idx += 1
        query = DetailCrawlTask.select().where(DetailCrawlTask.product_id == pi.product_id,
                                               DetailCrawlTask.update_ts > start_ts).order_by(
            DetailCrawlTask.update_ts).limit(1)
        if query.count() > 0:
            logger.info(
                f'detail crawl task [{query[0].id}] already exist for product_id [{pi.product_id}], just ignore')
            continue
        add_detail_crawl_task(pi.product_id, pi.product_link, {}, update_id,
                              analyze_and_add_detail_crawl_tasks.__name__)


# 有如下可能的无效shop_info的情况：
# 1. shop_link非标准格式，这不一定是无效链接，但我们尝试再通过搜索获取一遍
# 有如下可能的无效product_info的情况：
# 1. display_sale和estimated_revenue为-1，表示我们目前没获取到这些信息
# 2. 缺失大模型分析结果，默认所有商品信息都没有这个信息
# 通过生成对应task的方式来获取这些信息
def analyze_and_generate_fix_tasks(batch_ts, update_id):
    update_role = analyze_and_generate_fix_tasks.__name__
    ts = int(time.time())
    # 处理可能的店铺问题
    shop_search_start_ts = ts - TB_SHOP_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS
    si_query = ShopInfo.select().where(ShopInfo.update_ts > batch_ts).order_by(ShopInfo.update_ts)
    for si in si_query:
        if not re.match(SHOP_LINK_RE_EXP, si.shop_link):
            task = ShopSearchCrawlTask.select().where(ShopSearchCrawlTask.shop_name == si.shop_name,
                                                      ShopSearchCrawlTask.update_ts > shop_search_start_ts).order_by(
                ShopSearchCrawlTask.update_ts).limit(1)
            if task.count() == 0:
                add_shop_search_crawl_task(si.shop_name, {}, update_id, update_role)
    # 处理可能的商品问题
    search_start_ts = ts - TB_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS
    shop_start_ts = ts - TB_SHOP_CRAWL_TASK_PERIOD_IN_SECONDS
    pi_query = ProductInfo.select().where(ProductInfo.update_ts > batch_ts).order_by(
        ProductInfo.update_ts)
    product_batch = []
    for pi in pi_query:
        # 处理无销售数量问题，同时添加搜索任务和店铺任务
        if pi.display_sale == -1 or pi.estimated_revenue == -1:
            # 添加搜索任务
            tasks = SearchCrawlTask.select().where(SearchCrawlTask.search_key == pi.product_title,
                                                   SearchCrawlTask.update_ts > search_start_ts).order_by(
                SearchCrawlTask.update_ts)
            task_existed = False
            for task in tasks:
                target_product_ids = json_loads(task.target_product_ids)
                if len(target_product_ids) == 0:
                    task_existed = True
                    break
                else:
                    if pi.product_id in target_product_ids:
                        task_existed = True
                        break
            if not task_existed:
                add_search_crawl_task(pi.product_title, 1, [pi.product_id], {}, update_id, update_role)
            # 同时也添加店铺搜索任务
            tasks = ShopCrawlTask.select().where(ShopCrawlTask.shop_name == pi.shop_name,
                                                 ShopCrawlTask.update_ts > shop_start_ts).order_by(
                ShopCrawlTask.update_ts)
            task_existed = False
            for task in tasks:
                target_product_ids = json_loads(task.target_product_ids)
                if len(target_product_ids) == 0:
                    task_existed = True
                    break
                else:
                    if pi.product_id in target_product_ids:
                        task_existed = True
                        break
            if not task_existed:
                add_shop_crawl_task(pi.shop_name, [pi.product_id], {}, update_id, update_role)
        # 处理llm_analysis缺失问题
        if LLM_ANALYSIS_KEY not in json_loads(pi.additional_properties):
            product_batch.append(Product(id=pi.product_id, title=pi.product_title))
        if len(product_batch) == LLM_QUERY_BATCH_SIZE:
            add_llm_analyze_task(product_batch, {}, update_id, update_role)
            product_batch = []
    if len(product_batch) > 0:
        add_llm_analyze_task(product_batch, {}, update_id, update_role)


# 这里假设商品相关信息已经抓取并更新到product_info表中了，否则不继续进行
def analyze_and_add_hot_products():
    pass
