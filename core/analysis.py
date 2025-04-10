# coding: utf-8
# !./bin/python

from core.llm import *
from core.crawler import *

# 区分自动修复任务与手动添加任务，前者只要DEDUP期间有则不添加（无论状态），后者只要无非终止状态的就添加（无论时间）
# 各任务的执行检查周期，所有任务都是检查所有（10年），通过自动归档机制自动处理
TASK_CHECK_PERIOD_IN_SECONDS = 315360000

# 在考虑归档检查的前提下，任务仍然有可能会重复触发，但实际无需每次都跑，
# 比如店铺抓取，同样的店铺几天内抓过（不管是否成功，不成功会重试），则不再重复抓
# 再比如我们现在的抓取策略并不清楚在搜索页和店铺页是否抓到目标商品，且商品信息是否得到修复
# 自动任务的添加去重周期：7天
TASK_DEDUP_IN_SECONDS = 604800

# hot product 生成去重检查，日更（1天减去5分钟）
HOT_PRODUCT_DEDUP_IN_SECONDS = 86100

# 各任务的等待配置
SEARCH_CRAWL_IN_SALE_ORDER = False
SHOP_CRAWL_IN_SALE_ORDER = True
TASK_RETRY_COUNT_BEFORE_ARCHIVED = 10
TASK_RETRY_WAIT_IN_SECONDS = 3600
TASK_EXECUTE_GAP_IN_SECONDS = 10
TASK_SCAN_WAIT_IN_SECONDS = 60
LLM_TASK_BATCH_SIZE = 10

# 几个统计任务的统计标准
TB_SHOP_REVENUE_TOPN = 10
TB_SHOP_REVENUE_THRESHOLD = 50000
TB_SKU_REVENUE_TOPN = 50
TB_SKU_REVENUE_THRESHOLD = 10000


# 对于预定义搜索词，如果一段时间内没有存在的任务，则添加搜索任务
# 同样的search_key忽略num_of_pages的不同，认为任务存在，无视任务的状态
def analyze_and_add_search_crawl_tasks(search_key, num_of_pages, update_id):
    logger = get_logger()
    query = SearchCrawlTask.select().where(SearchCrawlTask.search_key == search_key,
                                           SearchCrawlTask.status != TASK_STATUS_DONE,
                                           SearchCrawlTask.status != TASK_STATUS_ARCHIVED).order_by(
        SearchCrawlTask.update_ts.desc()).limit(1)
    if query.count() > 0:
        logger.info(
            f'search crawl task id={query[0].id} already exist for search_key={search_key}, just ignore')
        return
    add_search_crawl_task(search_key, num_of_pages, None, None, update_id,
                          analyze_and_add_search_crawl_tasks.__name__)


# 获取一段时间内的商品最新销量和销售数据，按店铺聚合，若满足一定条件，且没有已存在的任务，则添加搜索任务
def analyze_and_add_shop_crawl_tasks(update_id, top_n=TB_SHOP_REVENUE_TOPN,
                                     revenue_threshold=TB_SHOP_REVENUE_THRESHOLD):
    logger = get_logger()
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
                                             ShopCrawlTask.status != TASK_STATUS_DONE,
                                             ShopCrawlTask.status != TASK_STATUS_ARCHIVED).order_by(
            ShopCrawlTask.update_ts.desc()).limit(1)
        if query.count() > 0:
            logger.info(
                f'shop crawl task id={query[0].id} already exist for shop_name={pi.shop_name}, just ignore')
            continue
        try:
            exist_si = ShopInfo.get(ShopInfo.shop_name == pi.shop_name)
            add_shop_crawl_task(exist_si.shop_name, None, None, update_id,
                                analyze_and_add_shop_crawl_tasks.__name__)
        except DoesNotExist:
            logger.error(f'ShopInfo item with shop_name={pi.shop_name} do not exist, just ignore')
            continue


# 获取一段时间内的商品最新销量和销售数据，若满足一定条件，且没有已存在的任务，则添加搜索任务
def analyze_and_add_detail_crawl_tasks(update_id, top_n=TB_SKU_REVENUE_TOPN,
                                       revenue_threshold=TB_SKU_REVENUE_THRESHOLD):
    logger = get_logger()
    ts = int(time.time())
    pi_query = ProductInfo.select().order_by(ProductInfo.estimated_revenue.desc())
    idx = 0
    for pi in pi_query:
        if idx > top_n and pi.estimated_revenue < revenue_threshold * 100:
            # 我们暂时不分析商品销量历史数据，因为这逻辑上相当于年度均线，且淘宝给出的信息很含糊
            break
        idx += 1
        query = DetailCrawlTask.select().where(DetailCrawlTask.product_id == pi.product_id,
                                               DetailCrawlTask.update_ts > ts - TASK_DEDUP_IN_SECONDS).order_by(
            DetailCrawlTask.update_ts)
        if query.count() > 0:
            logger.info(
                f'detail crawl task id={query[0].id} already exist for product_id={pi.product_id}, just ignore')
        else:
            add_detail_crawl_task(pi.product_id, pi.product_link, None, update_id,
                                  analyze_and_add_detail_crawl_tasks.__name__)


# 这里假设商品相关信息已经抓取并更新到product_info表中了，否则不继续进行
def analyze_and_add_hot_products(update_id, top_n=TB_SKU_REVENUE_TOPN,
                                 revenue_threshold=TB_SKU_REVENUE_THRESHOLD):
    logger = get_logger()
    ts = int(time.time())
    pi_query = ProductInfo.select().order_by(ProductInfo.estimated_revenue.desc())
    idx = 0
    for pi in pi_query:
        # 我们暂时不分析商品销量历史数据，因为这逻辑上相当于年度均线，且淘宝给出的信息很含糊
        if idx > top_n and pi.estimated_revenue < revenue_threshold * 100:
            break
        # 我们暂时也不处理未经LLM分析，或LLM认为的非虚拟商品，虽然这不一定准确
        additional_properties = json_loads(pi.additional_properties)
        if LLM_ANALYSIS_KEY not in additional_properties:
            continue
        if not additional_properties[LLM_ANALYSIS_KEY]['digital']:
            continue
        idx += 1
        query = HotProduct.select().where(HotProduct.product_id == pi.product_id,
                                          HotProduct.create_ts > ts - HOT_PRODUCT_DEDUP_IN_SECONDS).order_by(
            HotProduct.create_ts).limit(1)
        if query.count() > 0:
            logger.info(
                f'hot product product_id={pi.product_id} already added, just ignore')
            continue
        add_hot_product(pi.product_id, pi.shop_name, None, update_id,
                        analyze_and_add_hot_products.__name__)


# 返回是否继续执行这个task
def handle_error_task(task, update_id):
    ts = int(time.time())
    if task.try_count >= TASK_RETRY_COUNT_BEFORE_ARCHIVED:
        # set task status to TASK_STATUS_ARCHIVED if try count >= TASK_RETRY_BEFORE_ARCHIVED
        update_task_info(task, update_id, TASK_STATUS_ARCHIVED)
        return False
    if task.status == TASK_STATUS_ERROR and task.update_ts > ts - TASK_RETRY_WAIT_IN_SECONDS:
        # wait at least ALL_IN_ONE_TASK_ERROR_WAIT_IN_SECONDS seconds for next try
        return False
    return True


class CrawlTaskRunner:
    def __init__(self):
        self.logger = get_logger()
        self.crawler = Crawler()

    def login(self):
        self.crawler.login_taobao()

    def run_taobao_crawler_tasks(self, update_id):
        self.run_search_crawler_task(update_id)
        self.generate_crawl_fix_tasks(update_id)
        self.run_shop_search_crawler_task(update_id)
        self.run_shop_crawler_tasks(update_id)
        self.run_detail_crawler_tasks(update_id)

    def run_search_crawler_task(self, update_id):
        now_ts = int(time.time())
        start_ts = now_ts - TASK_CHECK_PERIOD_IN_SECONDS
        self.logger.info(f'run search crawler tasks with now_ts={now_ts}, start_ts={start_ts}')
        tasks = SearchCrawlTask.select().where(SearchCrawlTask.status != TASK_STATUS_DONE,
                                               SearchCrawlTask.status != TASK_STATUS_ARCHIVED,
                                               SearchCrawlTask.update_ts > start_ts).order_by(
            SearchCrawlTask.update_ts)
        for task in tasks:
            if not handle_error_task(task, update_id):
                continue
            task.try_count = task.try_count + 1
            update_task_info(task, update_id, TASK_STATUS_RUNNING)
            try:
                self.logger.info(
                    f'handling search crawl task id={task.id} with search_key={task.search_key}, num_of_pages={task.num_of_pages}, target_product_ids={task.target_product_ids}')
                target_product_ids = json_loads(task.target_product_ids)
                self.crawler.crawl_taobao_search_results(task.search_key, task.num_of_pages, SEARCH_CRAWL_IN_SALE_ORDER,
                                                         task.id,
                                                         target_product_ids)
            except Exception:
                self.logger.error(
                    f'get unhandled exception while handling task id={task.id} with search_key={task.search_key}, num_of_pages={task.num_of_pages}, target_product_ids={task.target_product_ids}')
                traceback.print_exc()
                update_task_info(task, update_id, TASK_STATUS_ERROR,
                                 err_code=TASK_FAILED_UNEXPECTED_ERROR,
                                 call_stack=traceback.format_exc())
                continue
            update_task_info(task, update_id, TASK_STATUS_DONE)
            time.sleep(TASK_EXECUTE_GAP_IN_SECONDS)
        return now_ts

    # 有如下可能的无效shop_info的情况：
    # 1. shop_link非标准格式，这不一定是无效链接，但我们尝试再通过搜索获取一遍
    # 有如下可能的无效product_info的情况：
    # 1. display_sale和estimated_revenue为-1，表示我们目前没获取到这些信息
    # 2. 缺失大模型分析结果，默认所有商品信息都没有这个信息
    # 通过生成对应task的方式来获取这些信息
    def generate_crawl_fix_tasks(self, update_id,
                                 fix_shop_title=True,
                                 fix_product_sale=True,
                                 fix_product_sale_by_search=False,
                                 fix_product_sale_by_shop=True,
                                 fix_llm_analysis=True):
        logger = get_logger()
        update_role = self.generate_crawl_fix_tasks.__name__
        ts = int(time.time())
        # 处理可能的店铺问题
        if fix_shop_title:
            logger.info('handling shop issues with invalid link ...')
            si_query = ShopInfo.select().where(ShopInfo.update_ts > ts - TASK_CHECK_PERIOD_IN_SECONDS).order_by(
                ShopInfo.update_ts)
            for si in si_query:
                shop_link_match = False
                for reg_exp in SHOP_LINK_KNOWN_RE_EXP_LIST:
                    if re.match(reg_exp, si.shop_link):
                        shop_link_match = True
                        break
                if not shop_link_match:
                    logger.info(f'handle shop link issue for shop_name={si.shop_name} with shop_link={si.shop_link}')
                    tasks = ShopSearchCrawlTask.select().where(ShopSearchCrawlTask.shop_name == si.shop_name,
                                                               ShopSearchCrawlTask.update_ts > ts - TASK_DEDUP_IN_SECONDS).order_by(
                        ShopSearchCrawlTask.update_ts.desc())
                    if tasks.count() == 0:
                        add_shop_search_crawl_task(si.shop_name, None, update_id, update_role)
        logger.info('handling product issues with display_sale==-1 or estimated_revenue==-1 ...')
        pi_query = ProductInfo.select().where(ProductInfo.update_ts > ts - TASK_CHECK_PERIOD_IN_SECONDS).order_by(
            ProductInfo.update_ts)
        for pi in pi_query:
            # 处理无销售数量问题，同时添加搜索任务和店铺任务
            if pi.display_sale == -1 or pi.estimated_revenue == -1:
                # 添加搜索任务
                if fix_product_sale and fix_product_sale_by_search:
                    logger.info(f'handle display_sale issue by search for product_id={pi.product_id}')
                    # 不考虑已标记为TASK_STATUS_ARCHIVED状态的店铺的商品，它们会被更新，但不会被抓取
                    tasks = SearchCrawlTask.select().where(SearchCrawlTask.search_key == pi.product_title,
                                                           SearchCrawlTask.update_ts > ts - TASK_DEDUP_IN_SECONDS).order_by(
                        SearchCrawlTask.update_ts.desc())
                    if len(tasks) > 0:
                        target_product_ids = json_loads(tasks[0].target_product_ids)
                        if len(target_product_ids) > 0:
                            if pi.product_id not in target_product_ids:
                                target_product_ids.append(pi.product_id)
                                update_task_info(tasks[0], update_id, target_product_ids=target_product_ids)
                    else:
                        add_search_crawl_task(pi.product_title, 1, [pi.product_id], None, update_id, update_role)
                # 同时也添加店铺搜索任务
                if fix_product_sale and fix_product_sale_by_shop:
                    logger.info(f'handle display_sale issue by shop for product_id={pi.product_id}')
                    # 不考虑已标记为TASK_STATUS_ARCHIVED状态的店铺的商品，它们会被更新，但不会被抓取
                    tasks = ShopCrawlTask.select().where(ShopCrawlTask.shop_name == pi.shop_name,
                                                         ShopCrawlTask.update_ts > ts - TASK_DEDUP_IN_SECONDS).order_by(
                        ShopCrawlTask.update_ts.desc())
                    if len(tasks) > 0:
                        target_product_ids = json_loads(tasks[0].target_product_ids)
                        if len(target_product_ids) > 0:
                            if pi.product_id not in target_product_ids:
                                target_product_ids.append(pi.product_id)
                                update_task_info(tasks[0], update_id, target_product_ids=target_product_ids)
                    else:
                        add_shop_crawl_task(pi.shop_name, [pi.product_id], None, update_id, update_role)
            # 处理llm_analysis缺失问题，我们不用batch的方式，便于检查任务是否存在，在执行任务时进行batch
            if fix_llm_analysis:
                if LLM_ANALYSIS_KEY not in json_loads(pi.additional_properties):
                    tasks = LLMAnalyzeTask.select().where(LLMAnalyzeTask.product_id == pi.product_id,
                                                          LLMAnalyzeTask.update_ts > ts - TASK_DEDUP_IN_SECONDS).order_by(
                        LLMAnalyzeTask.update_ts.desc())
                    logger.info(f'handle LLM analysis for product_id={pi.product_id}, product_title={pi.product_title}')
                    if tasks.count() == 0:
                        add_llm_analyze_task(pi.product_id, pi.product_title, None, update_id, update_role)

    def run_shop_search_crawler_task(self, update_id):
        start_ts = int(time.time()) - TASK_CHECK_PERIOD_IN_SECONDS
        self.logger.info(f'run shop search crawler tasks with start_ts={start_ts}')
        tasks = ShopSearchCrawlTask.select().where(ShopSearchCrawlTask.status != TASK_STATUS_DONE,
                                                   ShopSearchCrawlTask.status != TASK_STATUS_ARCHIVED,
                                                   ShopSearchCrawlTask.update_ts > start_ts).order_by(
            ShopSearchCrawlTask.update_ts)
        for task in tasks:
            if not handle_error_task(task, update_id):
                continue
            task.try_count = task.try_count + 1
            update_task_info(task, update_id, TASK_STATUS_RUNNING)
            try:
                self.logger.info(f'handling shop search crawler task id={task.id} with shop_name={task.shop_name}')
                self.crawler.crawl_taobao_shop_link_by_search(task.shop_name, task.id)
            except ShopNotFoundInSearch:
                self.logger.error(f'shop_name={task.shop_name} not found in shop search, task_id={task.id}')
                update_task_info(task, update_id, TASK_STATUS_ERROR,
                                 err_code=TASK_FAILED_SHOP_NOT_FOUND_IN_SEARCH)
                continue
            except Exception:
                self.logger.error(
                    f'get unhandled exception while handling task id={task.id} with shop_name={task.shop_name}, just continue')
                traceback.print_exc()
                update_task_info(task, update_id, TASK_STATUS_ERROR,
                                 err_code=TASK_FAILED_UNEXPECTED_ERROR,
                                 call_stack=traceback.format_exc())
                continue
            update_task_info(task, update_id, TASK_STATUS_DONE)
            time.sleep(TASK_EXECUTE_GAP_IN_SECONDS)
        return

    def run_shop_crawler_tasks(self, update_id):
        start_ts = int(time.time()) - TASK_CHECK_PERIOD_IN_SECONDS
        self.logger.info(f'run shop crawler tasks with start_ts={start_ts}')
        tasks = ShopCrawlTask.select().where(ShopCrawlTask.status != TASK_STATUS_DONE,
                                             ShopCrawlTask.status != TASK_STATUS_ARCHIVED,
                                             ShopCrawlTask.update_ts > start_ts).order_by(
            ShopCrawlTask.update_ts)
        for task in tasks:
            if not handle_error_task(task, update_id):
                continue
            task.try_count = task.try_count + 1
            update_task_info(task, update_id, TASK_STATUS_RUNNING)
            try:
                self.logger.info(
                    f'handling shop crawl task id={task.id} with shop_name={task.shop_name}, target_product_ids={task.target_product_ids}')
                shop = ShopInfo.get(ShopInfo.shop_name == task.shop_name)
                target_product_ids = json_loads(task.target_product_ids)
                self.crawler.craw_taobao_shop_page(shop.shop_link, SHOP_CRAWL_IN_SALE_ORDER, task.id,
                                                   target_product_ids)
            except DoesNotExist:
                self.logger.error(f'shop_info record with shop_name={task.shop_name} does not exist, just continue')
                update_task_info(task, update_id, TASK_STATUS_ERROR,
                                 err_code=TASK_FAILED_SHOP_NOT_EXIST)
                continue
            except ShopLinkNotFound:
                self.logger.error(f'shop link not found with shop_name={task.shop_name}, just continue')
                update_task_info(task, update_id, TASK_STATUS_ERROR,
                                 err_code=TASK_FAILED_SHOP_LINK_NOT_FOUND)
                continue
            except NotStandardShop:
                self.logger.error(f'shop is not a taobao standard shop, shop_name={task.shop_name}, just continue')
                update_task_info(task, update_id, TASK_STATUS_ERROR,
                                 err_code=TASK_FAILED_SHOP_NOT_STANDARD)
                continue
            except ShopLinkNotAccessible:
                self.logger.error(f'shop link can not be accessed now, shop_name={task.shop_name}, just continue')
                update_task_info(task, update_id, TASK_STATUS_ERROR,
                                 err_code=TASK_FAILED_SHOP_LINK_NOT_ACCESSIBLE)
                continue
            except Exception:
                self.logger.error(
                    f'get unhandled exception while handling task id={task.id} with shop_name={task.shop_name}, just continue')
                traceback.print_exc()
                update_task_info(task, update_id, TASK_STATUS_ERROR,
                                 err_code=TASK_FAILED_UNEXPECTED_ERROR,
                                 call_stack=traceback.format_exc())
                continue
            update_task_info(task, update_id, TASK_STATUS_DONE)
            time.sleep(TASK_EXECUTE_GAP_IN_SECONDS)
        return

    def run_detail_crawler_tasks(self, update_id):
        start_ts = int(time.time()) - TASK_CHECK_PERIOD_IN_SECONDS
        self.logger.info(f'run detail crawler tasks with start_ts={start_ts}')
        tasks = DetailCrawlTask.select().where(DetailCrawlTask.status != TASK_STATUS_DONE,
                                               DetailCrawlTask.status != TASK_STATUS_ARCHIVED,
                                               DetailCrawlTask.update_ts > start_ts).order_by(
            DetailCrawlTask.update_ts)
        for task in tasks:
            if not handle_error_task(task, update_id):
                continue
            task.try_count = task.try_count + 1
            update_task_info(task, update_id, TASK_STATUS_RUNNING)
            try:
                self.logger.info(
                    f'handling search crawl task id={task.id} with product_id={task.product_id}, product_link={task.product_link}')
                self.crawler.craw_taobao_detail_page(task.product_id, task.product_link, task.id)
                self.crawler.download_product_resources(task.product_id, task.id)
            except Exception:
                self.logger.error(
                    f'get unhandled exception while crawling task id={task.id} with product_id={task.product_id}, product_link={task.product_link}, just continue')
                traceback.print_exc()
                update_task_info(task, update_id, TASK_STATUS_ERROR,
                                 err_code=TASK_FAILED_UNEXPECTED_ERROR,
                                 call_stack=traceback.format_exc())
                continue
            update_task_info(task, update_id, TASK_STATUS_DONE)
            time.sleep(TASK_EXECUTE_GAP_IN_SECONDS)
        return


class ProductManageTaskRunner:
    def __init__(self):
        self.logger = get_logger()
        self.crawler = Crawler()

    def login(self):
        self.crawler.login_taobao()
        self.crawler.login_rednote()

    def run_shadow_product_tasks(self, update_id):
        self.analyze_and_add_shadow_products(update_id)
        self.generate_shadow_fix_tasks(update_id)
        self.run_product_manage_tasks(update_id)

    def analyze_and_add_shadow_products(self, update_id):
        # 按一定标准自动生成shadow_products
        pass

    # 分析并自动添加shadow products, 同时生成detail_crawl_task和llm_analyze_task
    # 然后检查并更新所有状态为NEW的shadow_product
    def generate_shadow_fix_tasks(self, update_id):
        ts = int(time.time())
        # check and update shadow product status
        shadow_products = ShadowProductInfo.select().where(ShadowProductInfo.status == SHADOW_PRODUCT_STATUS_NEW,
                                                           ShadowProductInfo.update_ts > ts - TASK_CHECK_PERIOD_IN_SECONDS)
        for sp in shadow_products:
            try:
                p = ProductInfo.get(ProductInfo.product_id == sp.product_id)
                additional_properties = json_loads(p.additional_properties)
                if RESOURCE_ROOT_KEY not in additional_properties:
                    tasks = DetailCrawlTask.select().where(DetailCrawlTask.product_id == p.product_id,
                                                           DetailCrawlTask.update_ts > ts - TASK_DEDUP_IN_SECONDS).order_by(
                        DetailCrawlTask.update_ts.desc())
                    if len(tasks) == 0:
                        self.logger.info(f'add detail crawl task to fix shadow product, product_id={p.product_id}')
                        add_detail_crawl_task(p.product_id, p.product_link, {}, update_id,
                                              self.generate_shadow_fix_tasks.__name__)
                if LLM_ANALYSIS_KEY not in additional_properties:
                    tasks = LLMAnalyzeTask.select().where(LLMAnalyzeTask.product_id == p.product_id,
                                                          LLMAnalyzeTask.update_ts > ts - TASK_DEDUP_IN_SECONDS).order_by(
                        LLMAnalyzeTask.update_ts.desc())
                    if len(tasks) == 0:
                        self.logger.info(f'add llm analyze task to fix shadow product, product_id={p.product_id}')
                        add_llm_analyze_task(p.product_id, p.product_title, {}, update_id,
                                             self.generate_shadow_fix_tasks.__name__)
                if sp.status == SHADOW_PRODUCT_STATUS_NEW:
                    tasks = ProductManageTask.select().where(ProductManageTask.product_id == p.product_id,
                                                             ProductManageTask.update_ts > ts - TASK_DEDUP_IN_SECONDS).order_by(
                        ProductManageTask.update_ts.desc())
                    if len(tasks) == 0:
                        self.logger.info(f'add product_manage_task to sync shadow product, product_id={sp.product_id}')
                        add_product_manage_task(sp.product_id, sp.shop_name, PRODUCT_MANAGE_PLATFORM_NONE,
                                                PRODUCT_MANAGE_OPERATION_READY, {}, update_id,
                                                self.generate_shadow_fix_tasks.__name__)
            except DoesNotExist:
                self.logger.error(
                    f'product_id={sp.product_id} does not exist while updating shadow product, just continue')
                continue
            except Exception:
                self.logger.error(f'get unexpected exception while updating shadow products, just continue')
                traceback.print_exc()
                continue

    def run_product_manage_tasks(self, update_id):
        logger = get_logger()
        start_ts = int(time.time()) - TASK_CHECK_PERIOD_IN_SECONDS
        logger.info(f'run product manage tasks with start_ts={start_ts}')
        tasks = ProductManageTask.select().where(ProductManageTask.status != TASK_STATUS_DONE,
                                                 ProductManageTask.status != TASK_STATUS_ARCHIVED,
                                                 ProductManageTask.update_ts > start_ts).order_by(
            ProductManageTask.update_ts)
        for task in tasks:
            # 这个任务不处理 handle_error_task
            task.try_count = task.try_count + 1
            update_task_info(task, update_id, TASK_STATUS_RUNNING)
            try:
                logger.info(
                    f'handling product manage task id={task.id} with product_id={task.product_id}, shop_name={task.shop_name}, operation={task.operation}')
                success = False
                if task.operation == PRODUCT_MANAGE_OPERATION_READY:
                    success = self.crawler.product_manage_ready(task.product_id, task.shop_name, task.platform, task.id)
                elif task.operation == PRODUCT_MANAGE_OPERATION_ONSHELF:
                    success = self.crawler.product_manage_on_shelf(task.product_id, task.shop_name, task.platform,
                                                                   task.id)
                elif task.operation == PRODUCT_MANAGE_OPERATION_ONLINE:
                    success = self.crawler.product_manage_online(task.product_id, task.shop_name, task.platform,
                                                                 task.id)
                elif task.operation == PRODUCT_MANAGE_OPERATION_OFFLINE:
                    success = self.crawler.product_manage_offline(task.product_id, task.shop_name, task.platform,
                                                                  task.id)
                elif task.operation == PRODUCT_MANAGE_OPERATION_OFFSHELF:
                    success = self.crawler.product_manage_off_shelf(task.product_id, task.shop_name, task.platform,
                                                                    task.id)
            except Exception:
                logger.error(
                    f'get unhandled exception while handling product manage task id={task.id} with product_id={task.product_id}, shop_name={task.shop_name}, operation={task.operation}, just continue')
                traceback.print_exc()
                update_task_info(task, update_id, TASK_STATUS_ERROR,
                                 err_code=TASK_FAILED_UNEXPECTED_ERROR,
                                 call_stack=traceback.format_exc())
                continue
            update_task_info(task, update_id, TASK_STATUS_DONE if success else TASK_STATUS_NEW)
            time.sleep(TASK_EXECUTE_GAP_IN_SECONDS)
        return


class LLMTaskRunner:
    def __init__(self):
        self.logger = get_logger()
        self.llm_client = LLMClient()

    def run_llm_analyze_tasks(self, update_id):
        start_ts = int(time.time()) - TASK_CHECK_PERIOD_IN_SECONDS
        self.logger.info(f'run llm analyze task with start_ts={start_ts}')
        product_task_batch = []
        tasks = LLMAnalyzeTask.select().where(LLMAnalyzeTask.status != TASK_STATUS_DONE,
                                              LLMAnalyzeTask.status != TASK_STATUS_ARCHIVED,
                                              LLMAnalyzeTask.update_ts > start_ts).order_by(
            LLMAnalyzeTask.update_ts)
        for task in tasks:
            # We don't do any handle_error_task(task, update_id) here
            task.try_count = task.try_count + 1
            update_task_info(task, update_id, TASK_STATUS_RUNNING)
            try:
                if len(product_task_batch) >= LLM_TASK_BATCH_SIZE:
                    id_set = self.llm_client.update_product_llm_analysis_batch([p for p, t in product_task_batch])
                    for p, t in product_task_batch:
                        if p.id in id_set:
                            update_task_info(t, update_id, TASK_STATUS_DONE)
                        else:
                            update_task_info(t, update_id, TASK_STATUS_ERROR)
                    product_task_batch = []
                    time.sleep(TASK_EXECUTE_GAP_IN_SECONDS)
                product_task_batch.append(
                    (Product(id=task.product_id, task_id=task.id, title=task.product_title), task))
            except Exception:
                self.logger.error(
                    f'get unhandled exception while analyzing llm products {[p for p, t in product_task_batch]}, just continue')
                traceback.print_exc()
                [update_task_info(t, update_id, TASK_STATUS_ERROR,
                                  err_code=TASK_FAILED_UNEXPECTED_ERROR,
                                  call_stack=traceback.format_exc()) for _, t in
                 product_task_batch]
                continue
        # handle last batch
        if len(product_task_batch) > 0:
            try:
                id_set = self.llm_client.update_product_llm_analysis_batch([p for p, t in product_task_batch])
                for p, t in product_task_batch:
                    if p.id in id_set:
                        update_task_info(t, update_id, TASK_STATUS_DONE)
                    else:
                        update_task_info(t, update_id, TASK_STATUS_ERROR)
                product_task_batch = []
                time.sleep(TASK_EXECUTE_GAP_IN_SECONDS)
            except Exception:
                self.logger.error(
                    f'get unhandled exception while analyzing llm products {[p for p, t in product_task_batch]}, just continue')
                traceback.print_exc()
                [update_task_info(t, update_id, TASK_STATUS_ERROR,
                                  err_code=TASK_FAILED_UNEXPECTED_ERROR,
                                  call_stack=traceback.format_exc()) for _, t in
                 product_task_batch]
        return
