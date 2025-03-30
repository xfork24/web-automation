# coding: utf-8
# !./bin/python
# restful API for management console

from flask import Flask, request
from core.models import *
from core.analysis import (
    TB_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS,
    TB_SHOP_CRAWL_TASK_PERIOD_IN_SECONDS,
    TB_DETAIL_CRAWL_TASK_PERIOD_IN_SECONDS,
    TB_SHOP_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS,
    TB_LLM_ANALYZE_TASK_PERIOD_IN_SECONDS,
    TB_HOT_PRODUCT_PERIOD_IN_SECONDS
)

TASK_STATUS_QUERY_PERIOD = 604800
DB_QUERY_DEFAULT_LIMIT = 100
ERROR_CODE_SERVER_ERROR = -1
ERROR_CODE_NOT_FOUND = -11

api = Flask(__name__)


def build_success_response(resp):
    resp['code'] = 0
    resp['msg'] = 'success'
    return json_dumps(resp)


def build_server_error_response(msg):
    return json_dumps({
        'code': ERROR_CODE_SERVER_ERROR,
        'msg': msg
    })


def build_not_found_response(msg):
    return json_dumps({
        'code': ERROR_CODE_NOT_FOUND,
        'msg': msg
    })


def parse_param_compare(x, v):
    exps = []
    param = json_loads(v)
    exps.append(x > int(param['gt'])) if 'gt' in param else None
    exps.append(x >= int(param['gte'])) if 'gte' in param else None
    exps.append(x < int(param['lt'])) if 'lt' in param else None
    exps.append(x <= int(param['lte'])) if 'lte' in param else None
    return exps


def parse_task_status_query(query):
    result = {}
    for q in query:
        if q.status == TASK_STATUS_NEW:
            result['NEW'] = q.count
        elif q.status == TASK_STATUS_IN_PROGRESS:
            result['IN_PROGRESS'] = q.count
        elif q.status == TASK_STATUS_DONE:
            result['DONE'] = q.count
        elif q.status == TASK_STATUS_ERROR:
            result['ERROR'] = q.count
        elif q.status == TASK_STATUS_ARCHIVED:
            result['ARCHIVED'] = q.count
    if 'NEW' not in result.keys():
        result['NEW'] = 0
    if 'IN_PROGRESS' not in result.keys():
        result['IN_PROGRESS'] = 0
    if 'DONE' not in result.keys():
        result['DONE'] = 0
    if 'ERROR' not in result.keys():
        result['ERROR'] = 0
    if 'ARCHIVED' not in result.keys():
        result['ARCHIVED'] = 0
    return result


@api.get('/api/v1/product/<product_id>')
def get_product_by_id(product_id):
    logger = get_logger()
    try:
        p = ProductInfo.get(ProductInfo.product_id == product_id)
        return build_success_response({'data': p.to_dict()})
    except DoesNotExist:
        msg = f'product_id={product_id} not found'
        logger.info(f'invalid product_id={product_id}, not found')
        return build_not_found_response(msg)
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.delete('/api/v1/product/<product_id>')
def delete_product_by_id(product_id):
    logger = get_logger()
    try:
        x = ProductInfo.delete().where(ProductInfo.product_id == product_id).execute()
        return build_success_response({'product_id': product_id if x == 1 else ''})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


# supported query params:
# shop_name = XXX
# update_ts = {"lt": 100, "gt": 30}
# display_sale = {"lt": 100, "gt": 30}
# estimated_revenue = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = update_ts or display_sale or estimated_revenue or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@api.get('/api/v1/products')
def query_products():
    logger = get_logger()
    try:
        select_exps = []
        sort = ProductInfo.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.args.items():
            if k == 'shop_name':
                select_exps.append(ProductInfo.shop_name == v)
            elif k == 'update_ts':
                select_exps += parse_param_compare(ProductInfo.update_ts, v)
            elif k == 'display_sale':
                select_exps += parse_param_compare(ProductInfo.display_sale, v)
            elif k == 'estimated_revenue':
                select_exps += parse_param_compare(ProductInfo.estimated_revenue, v)
            elif k == 'update_id':
                select_exps.append(ProductInfo.update_id == v)
            elif k == 'sort':
                sort_columns = {
                    'update_ts': ProductInfo.update_ts,
                    'display_sale': ProductInfo.display_sale,
                    'estimated_revenue': ProductInfo.estimated_revenue,
                    'update_id': ProductInfo.update_id
                }
                if v in sort_columns:
                    sort = sort_columns[v]
            elif k == 'desc':
                desc = True
            elif k == 'limit':
                limit = int(v)
            elif k == 'offset':
                offset = int(v)
        sort = sort.desc() if desc else sort
        if len(select_exps) == 0:
            query = ProductInfo.select().order_by(sort).limit(limit).offset(offset)
        else:
            query = ProductInfo.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.get('/api/v1/shop/<shop_name>')
def get_shop_by_name(shop_name):
    logger = get_logger()
    try:
        p = ShopInfo.select(ShopInfo.shop_name,
                            ShopInfo.shop_link,
                            ShopInfo.additional_properties,
                            ShopInfo.create_ts,
                            ShopInfo.update_ts,
                            ShopInfo.update_id,
                            ShopInfo.update_role,
                            fn.AVG(ProductInfo.display_price).alias('avg_price'),
                            fn.SUM(ProductInfo.display_sale).alias('total_sale'),
                            fn.SUM(ProductInfo.estimated_revenue).alias('total_revenue')).join(ProductInfo,
                                                                                               JOIN.LEFT_OUTER).group_by(
            ShopInfo.shop_name).where(
            ShopInfo.shop_name == shop_name)
        if len(p) == 0:
            raise DoesNotExist()
        item = {
            'avg_price': int(p[0].avg_price) if p[0].avg_price is not None else -1,
            'total_sale': int(p[0].total_sale) if p[0].total_sale is not None else -1,
            'total_revenue': int(p[0].total_revenue) if p[0].total_revenue is not None else -1
        }
        item.update(p[0].to_dict())
        return build_success_response({'data': item})
    except DoesNotExist:
        msg = f'shop_name={shop_name} not found'
        logger.info(f'invalid shop_name={shop_name}, not found')
        return build_not_found_response(msg)
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.delete('/api/v1/shop/<shop_name>')
def delete_shop_by_name(shop_name):
    logger = get_logger()
    try:
        x = ShopInfo.delete().where(ShopInfo.shop_name == shop_name).execute()
        return build_success_response({'shop_name': shop_name if x == 1 else ''})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


# supported query params:
# shop_name = XXX
# update_ts = {"lt": 100, "gt": 30}
# avg_price = {"lt": 100, "gt": 30}
# total_sale = {"lt": 100, "gt": 30}
# total_revenue = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = update_ts or update_id or avg_price or total_sale or total_revenue
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@api.get('/api/v1/shops')
def query_shops():
    logger = get_logger()
    try:
        select_exps = []
        sort = ShopInfo.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.args.items():
            if k == 'update_ts':
                select_exps += parse_param_compare(ShopInfo.update_ts, v)
            elif k == 'update_id':
                select_exps.append(ShopInfo.update_id == v)
            elif k == 'sort':
                sort_columns = {
                    'update_ts': ShopInfo.update_ts,
                    'update_id': ShopInfo.update_id,
                    'avg_price': fn.AVG(ProductInfo.display_price),
                    'total_sale': fn.SUM(ProductInfo.display_sale),
                    'total_revenue': fn.SUM(ProductInfo.estimated_revenue)
                }
                if v in sort_columns:
                    sort = sort_columns[v]
            elif k == 'desc':
                desc = True
            elif k == 'limit':
                limit = int(v)
            elif k == 'offset':
                offset = int(v)
        sort = sort.desc() if desc else sort
        if len(select_exps) == 0:
            query = ShopInfo.select(ShopInfo.shop_name,
                                    ShopInfo.shop_link,
                                    ShopInfo.additional_properties,
                                    ShopInfo.create_ts,
                                    ShopInfo.update_ts,
                                    ShopInfo.update_id,
                                    ShopInfo.update_role,
                                    fn.AVG(ProductInfo.display_price).alias('avg_price'),
                                    fn.SUM(ProductInfo.display_sale).alias('total_sale'),
                                    fn.SUM(ProductInfo.estimated_revenue).alias('total_revenue')).join(ProductInfo,
                                                                                                       JOIN.LEFT_OUTER).group_by(
                ShopInfo.shop_name).order_by(sort).limit(limit).offset(offset)
        else:
            query = ShopInfo.select(ShopInfo.shop_name,
                                    ShopInfo.shop_link,
                                    ShopInfo.additional_properties,
                                    ShopInfo.create_ts,
                                    ShopInfo.update_ts,
                                    ShopInfo.update_id,
                                    ShopInfo.update_role,
                                    fn.AVG(ProductInfo.display_price).alias('avg_price'),
                                    fn.SUM(ProductInfo.display_sale).alias('total_sale'),
                                    fn.SUM(ProductInfo.estimated_revenue).alias('total_revenue')).join(ProductInfo,
                                                                                                       JOIN.LEFT_OUTER).group_by(
                ShopInfo.shop_name).where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = []
        for q in query:
            item = {
                'avg_price': int(q.avg_price) if q.avg_price is not None else -1,
                'total_sale': int(q.total_sale) if q.total_sale is not None else -1,
                'total_revenue': int(q.total_revenue) if q.total_revenue is not None else -1
            }
            item.update(q.to_dict())
            data.append(item)
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.get('/api/v1/product_sale/<product_id>/<create_ts>')
def get_product_sale_by_id_and_ts(product_id, create_ts):
    logger = get_logger()
    try:
        p = ProductSale.get(ProductSale.product_id == product_id, ProductSale.create_ts == int(create_ts))
        return build_success_response({'data': p.to_dict()})
    except DoesNotExist:
        msg = f'product_id={product_id} and create_ts={create_ts} not found'
        logger.info(f'invalid product_id={product_id} and create_ts={create_ts} not found')
        return build_not_found_response(msg)
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.delete('/api/v1/product_sale/<product_id>/<create_ts>')
def delete_product_sale_by_id_and_ts(product_id, create_ts):
    logger = get_logger()
    try:
        x = ProductSale.delete().where(ProductSale.product_id == product_id,
                                       ProductSale.create_ts == create_ts).execute()
        return build_success_response(
            {'product_id': product_id if x == 1 else '', 'create_ts': create_ts if x == 1 else ''})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


# supported query params:
# product_id = XXX
# shop_name = XXX
# create_ts = {"lt": 100, "gt": 30}
# display_sale = {"lt": 100, "gt": 30}
# estimated_revenue = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = create_ts or display_sale or estimated_revenue or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@api.get('/api/v1/product_sales')
def query_product_sales():
    logger = get_logger()
    try:
        select_exps = []
        sort = ProductSale.create_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.args.items():
            if k == 'product_id':
                select_exps.append(ProductSale.product_id == v)
            elif k == 'shop_name':
                select_exps.append(ProductSale.shop_name == v)
            elif k == 'create_ts':
                select_exps += parse_param_compare(ProductSale.create_ts, v)
            elif k == 'display_sale':
                select_exps += parse_param_compare(ProductSale.display_sale, v)
            elif k == 'estimated_revenue':
                select_exps += parse_param_compare(ProductSale.estimated_revenue, v)
            elif k == 'update_id':
                select_exps.append(ProductSale.update_id == v)
            elif k == 'sort':
                sort_columns = {
                    'create_ts': ProductSale.create_ts,
                    'display_sale': ProductSale.display_sale,
                    'estimated_revenue': ProductSale.estimated_revenue,
                    'update_id': ProductSale.update_id
                }
                if v in sort_columns:
                    sort = sort_columns[v]
            elif k == 'desc':
                desc = True
            elif k == 'limit':
                limit = int(v)
            elif k == 'offset':
                offset = int(v)
        sort = sort.desc() if desc else sort
        if len(select_exps) == 0:
            query = ProductSale.select().order_by(sort).limit(limit).offset(offset)
        else:
            query = ProductSale.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.get('/api/v1/hot_product/<product_id>/<create_ts>')
def get_hot_product_by_id_and_ts(product_id, create_ts):
    logger = get_logger()
    try:
        p = HotProduct.get(HotProduct.product_id == product_id, HotProduct.create_ts == int(create_ts))
        return build_success_response({'data': p.to_dict()})
    except DoesNotExist:
        msg = f'product_id={product_id} and create_ts={create_ts} not found'
        logger.info(f'invalid product_id={product_id} and create_ts={create_ts} not found')
        return build_not_found_response(msg)
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.put('/api/v1/hot_product')
def create_hot_product():
    logger = get_logger()
    try:
        payload = request.json
        add_hot_product(payload.get('product_id'),
                        payload.get('shop_name'),
                        {},
                        payload.get('update_id'),
                        create_hot_product.__name__)
        return build_success_response({})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.delete('/api/v1/hot_product/<product_id>/<create_ts>')
def delete_hot_product_by_id_and_ts(product_id, create_ts):
    logger = get_logger()
    try:
        x = HotProduct.delete().where(HotProduct.product_id == product_id,
                                      HotProduct.create_ts == create_ts).execute()
        return build_success_response(
            {'product_id': product_id if x == 1 else '', 'create_ts': create_ts if x == 1 else ''})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


# supported query params:
# product_id = XXX
# shop_name = XXX
# create_ts = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = create_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@api.get('/api/v1/hot_products')
def query_hot_products():
    logger = get_logger()
    try:
        select_exps = []
        sort = HotProduct.create_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.args.items():
            if k == 'product_id':
                select_exps.append(HotProduct.product_id == v)
            elif k == 'shop_name':
                select_exps.append(HotProduct.shop_name == v)
            elif k == 'create_ts':
                select_exps += parse_param_compare(HotProduct.create_ts, v)
            elif k == 'update_id':
                select_exps.append(HotProduct.update_id == v)
            elif k == 'sort':
                sort_columns = {
                    'create_ts': HotProduct.create_ts,
                    'update_id': HotProduct.update_id
                }
                if v in sort_columns:
                    sort = sort_columns[v]
            elif k == 'desc':
                desc = True
            elif k == 'limit':
                limit = int(v)
            elif k == 'offset':
                offset = int(v)
        sort = sort.desc() if desc else sort
        if len(select_exps) == 0:
            query = HotProduct.select().order_by(sort).limit(limit).offset(offset)
        else:
            query = HotProduct.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.get('/api/v1/operation_history/<history_id>')
def get_operation_history_by_id(history_id):
    logger = get_logger()
    try:
        p = OperationHistory.get(OperationHistory.id == history_id)
        return build_success_response({'data': p.to_dict()})
    except DoesNotExist:
        msg = f'id={history_id} not found'
        logger.info(f'invalid id={history_id}, not found')
        return build_not_found_response(msg)
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


# supported query params:
# pk = XXX
# table_name = XXX
# update_id = XXX
# operation_ts = {"lt": 100, "gt": 30}
# create_ts = {"lt": 100, "gt": 30}
# sort = create_ts or operation_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@api.get('/api/v1/operation_histories')
def query_operation_histories():
    logger = get_logger()
    try:
        select_exps = []
        sort = OperationHistory.create_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.args.items():
            if k == 'pk':
                select_exps.append(OperationHistory.pk == v)
            elif k == 'table_name':
                select_exps.append(OperationHistory.table_name == v)
            elif k == 'update_id':
                select_exps.append(OperationHistory.update_id == v)
            elif k == 'operation_ts':
                select_exps.append(OperationHistory.operation_ts == v)
            elif k == 'create_ts':
                select_exps += parse_param_compare(OperationHistory.create_ts, v)
            elif k == 'sort':
                sort_columns = {
                    'create_ts': OperationHistory.create_ts,
                    'operation_ts': OperationHistory.operation_ts,
                    'update_id': OperationHistory.update_id
                }
                if v in sort_columns:
                    sort = sort_columns[v]
            elif k == 'desc':
                desc = True
            elif k == 'limit':
                limit = int(v)
            elif k == 'offset':
                offset = int(v)
        sort = sort.desc() if desc else sort
        if len(select_exps) == 0:
            query = OperationHistory.select().order_by(sort).limit(limit).offset(offset)
        else:
            query = OperationHistory.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


# update_ts = {"lt": 100, "gt": 30}
@api.get('/api/v1/tasks')
def get_all_tasks():
    logger = get_logger()
    try:
        data = {}
        now = int(time.time())
        start_ts = now - TASK_STATUS_QUERY_PERIOD
        if 'update_ts' in request.args.keys():
            param = json_loads(request.args['update_ts'])
            start_ts = int(param['gt']) if 'gt' in param else start_ts
            start_ts = int(param['gte']) if 'gte' in param else start_ts
            now = int(param['lt']) if 'lt' in param else now
            now = int(param['lte']) if 'lte' in param else now
        # detail crawl task
        query = DetailCrawlTask.select(DetailCrawlTask.status, fn.COUNT(DetailCrawlTask.id).alias('count')).where(
            DetailCrawlTask.update_ts >= start_ts, DetailCrawlTask.update_ts < now).group_by(DetailCrawlTask.status)
        data['detail_crawl_task'] = parse_task_status_query(query)
        # search crawl task
        query = SearchCrawlTask.select(SearchCrawlTask.status, fn.COUNT(SearchCrawlTask.id).alias('count')).where(
            SearchCrawlTask.update_ts >= start_ts, SearchCrawlTask.update_ts < now).group_by(SearchCrawlTask.status)
        data['search_crawl_task'] = parse_task_status_query(query)
        # shop crawl task
        query = ShopCrawlTask.select(ShopCrawlTask.status, fn.COUNT(ShopCrawlTask.id).alias('count')).where(
            ShopCrawlTask.update_ts >= start_ts, ShopCrawlTask.update_ts < now).group_by(ShopCrawlTask.status)
        data['shop_crawl_task'] = parse_task_status_query(query)
        # shop search crawl task
        query = ShopSearchCrawlTask.select(
            ShopSearchCrawlTask.status, fn.COUNT(ShopSearchCrawlTask.id).alias('count')).where(
            ShopSearchCrawlTask.update_ts >= start_ts, ShopSearchCrawlTask.update_ts < now).group_by(
            ShopSearchCrawlTask.status)
        data['shop_search_crawl_task'] = parse_task_status_query(query)
        # llm analyze task
        query = LLMAnalyzeTask.select(
            LLMAnalyzeTask.status, fn.COUNT(LLMAnalyzeTask.id).alias('count')).where(
            LLMAnalyzeTask.update_ts >= start_ts, LLMAnalyzeTask.update_ts < now).group_by(LLMAnalyzeTask.status)
        data['llm_analyze_task'] = parse_task_status_query(query)
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.get('/api/v1/detail_task/<task_id>')
def get_detail_crawl_task_by_id(task_id):
    logger = get_logger()
    try:
        p = DetailCrawlTask.get(DetailCrawlTask.id == task_id)
        return build_success_response({'data': p.to_dict()})
    except DoesNotExist:
        msg = f'id={task_id} not found'
        logger.info(f'invalid id={task_id}, not found')
        return build_not_found_response(msg)
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.put('/api/v1/detail_task')
def create_detail_crawl_task():
    logger = get_logger()
    try:
        start_ts = int(time.time()) - TB_DETAIL_CRAWL_TASK_PERIOD_IN_SECONDS
        payload = request.json
        tasks = DetailCrawlTask.select().where(DetailCrawlTask.product_id == payload.get('product_id'),
                                               DetailCrawlTask.status != TASK_STATUS_DONE,
                                               DetailCrawlTask.status != TASK_STATUS_ARCHIVED,
                                               DetailCrawlTask.update_ts > start_ts)
        task_id = ''
        if len(tasks) == 0 or payload.get('force') == 'true':
            task_id = add_detail_crawl_task(payload.get('product_id'),
                                            payload.get('product_link'),
                                            {},
                                            payload.get('update_id'),
                                            create_detail_crawl_task.__name__)
        else:
            logger.info(
                f'same task already exist for product_id={payload.get("product_id")} and "force" is not set to "true", just ignore')
        return build_success_response({'task_id': task_id})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.delete('/api/v1/detail_task/<task_id>')
def delete_detail_crawl_task(task_id):
    logger = get_logger()
    try:
        x = DetailCrawlTask.delete().where(DetailCrawlTask.id == task_id).execute()
        return build_success_response({'task_id': task_id if x == 1 else ''})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


# supported query params:
# product_id = XXX
# status = XXX
# update_ts = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = update_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@api.get('/api/v1/detail_tasks')
def get_detail_crawl_tasks():
    logger = get_logger()
    try:
        select_exps = []
        sort = DetailCrawlTask.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.args.items():
            if k == 'product_id':
                select_exps.append(DetailCrawlTask.product_id == v)
            elif k == 'status':
                select_exps.append(DetailCrawlTask.status == int(v))
            elif k == 'update_ts':
                select_exps += parse_param_compare(DetailCrawlTask.update_ts, v)
            elif k == 'update_id':
                select_exps.append(DetailCrawlTask.update_id == v)
            elif k == 'sort':
                sort_columns = {
                    'update_ts': DetailCrawlTask.update_ts,
                    'update_id': DetailCrawlTask.update_id
                }
                if v in sort_columns:
                    sort = sort_columns[v]
            elif k == 'desc':
                desc = True
            elif k == 'limit':
                limit = int(v)
            elif k == 'offset':
                offset = int(v)
        sort = sort.desc() if desc else sort
        if len(select_exps) == 0:
            query = DetailCrawlTask.select().order_by(sort).limit(limit).offset(offset)
        else:
            query = DetailCrawlTask.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.get('/api/v1/shop_task/<task_id>')
def get_shop_crawl_task_by_id(task_id):
    logger = get_logger()
    try:
        p = ShopCrawlTask.get(ShopCrawlTask.id == task_id)
        return build_success_response({'data': p.to_dict()})
    except DoesNotExist:
        msg = f'id={task_id} not found'
        logger.info(f'invalid id={task_id}, not found')
        return build_not_found_response(msg)
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.put('/api/v1/shop_task')
def create_shop_crawl_task():
    logger = get_logger()
    try:
        start_ts = int(time.time()) - TB_SHOP_CRAWL_TASK_PERIOD_IN_SECONDS
        payload = request.json
        tasks = ShopCrawlTask.select().where(ShopCrawlTask.shop_name == payload.get('shop_name'),
                                             ShopCrawlTask.status != TASK_STATUS_DONE,
                                             ShopCrawlTask.status != TASK_STATUS_ARCHIVED,
                                             ShopCrawlTask.update_ts > start_ts)
        target_product_ids = payload.get('target_product_ids')
        if len(tasks) == 0 or payload.get('force') == 'true':
            task_id = add_shop_crawl_task(payload.get('shop_name'),
                                          target_product_ids,
                                          {},
                                          payload.get('update_id'),
                                          create_shop_crawl_task.__name__)
        else:
            logger.info(
                f'same task already exist for shop_name={payload.get("shop_name")} and "force" is not set to "true", just update one of existing tasks')
            task = tasks[0]
            task_id = task.id
            target_product_ids = list(set(target_product_ids).union(set(json_loads(task.target_product_ids))))
            update_task_info(task, payload.get('update_id'), target_product_ids=target_product_ids)
        return build_success_response({'task_id': task_id})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.delete('/api/v1/shop_task/<task_id>')
def delete_shop_crawl_task(task_id):
    logger = get_logger()
    try:
        x = ShopCrawlTask.delete().where(ShopCrawlTask.id == task_id).execute()
        return build_success_response({'task_id': task_id if x == 1 else ''})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


# supported query params:
# shop_name = XXX
# status = XXX
# update_ts = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = update_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@api.get('/api/v1/shop_tasks')
def get_shop_crawl_tasks():
    logger = get_logger()
    try:
        select_exps = []
        sort = ShopCrawlTask.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.args.items():
            if k == 'shop_name':
                select_exps.append(ShopCrawlTask.shop_name == v)
            elif k == 'status':
                select_exps.append(ShopCrawlTask.status == int(v))
            elif k == 'update_ts':
                select_exps += parse_param_compare(ShopCrawlTask.update_ts, v)
            elif k == 'update_id':
                select_exps.append(ShopCrawlTask.update_id == v)
            elif k == 'sort':
                sort_columns = {
                    'update_ts': ShopCrawlTask.update_ts,
                    'update_id': ShopCrawlTask.update_id
                }
                if v in sort_columns:
                    sort = sort_columns[v]
            elif k == 'desc':
                desc = True
            elif k == 'limit':
                limit = int(v)
            elif k == 'offset':
                offset = int(v)
        sort = sort.desc() if desc else sort
        if len(select_exps) == 0:
            query = ShopCrawlTask.select().order_by(sort).limit(limit).offset(offset)
        else:
            query = ShopCrawlTask.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.get('/api/v1/search_task/<task_id>')
def get_search_crawl_task_by_id(task_id):
    logger = get_logger()
    try:
        p = SearchCrawlTask.get(SearchCrawlTask.id == task_id)
        return build_success_response({'data': p.to_dict()})
    except DoesNotExist:
        msg = f'id={task_id} not found'
        logger.info(f'invalid id={task_id}, not found')
        return build_not_found_response(msg)
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.put('/api/v1/search_task')
def create_search_crawl_task():
    logger = get_logger()
    try:
        start_ts = int(time.time()) - TB_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS
        payload = request.json
        tasks = SearchCrawlTask.select().where(SearchCrawlTask.search_key == payload.get('search_key'),
                                               SearchCrawlTask.status != TASK_STATUS_DONE,
                                               SearchCrawlTask.status != TASK_STATUS_ARCHIVED,
                                               SearchCrawlTask.update_ts > start_ts)
        target_product_ids = payload.get('target_product_ids')
        if len(tasks) == 0 or payload.get('force') == 'true':
            task_id = add_search_crawl_task(payload.get('search_key'),
                                            payload.get('num_of_pages'),
                                            target_product_ids,
                                            {},
                                            payload.get('update_id'),
                                            create_search_crawl_task.__name__)
        else:
            logger.info(
                f'same task already exist for search_key={payload.get("search_key")} and "force" is not set to "true", just update one of existing tasks')
            task = tasks[0]
            task_id = task.id
            target_product_ids = list(set(target_product_ids).union(set(json_loads(task.target_product_ids))))
            update_task_info(task, payload.get('update_id'), target_product_ids=target_product_ids,
                             num_of_pages=payload.get('num_of_pages'))
        return build_success_response({'task_id': task_id})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.delete('/api/v1/search_task/<task_id>')
def delete_search_crawl_task(task_id):
    logger = get_logger()
    try:
        x = SearchCrawlTask.delete().where(SearchCrawlTask.id == task_id).execute()
        return build_success_response({'task_id': task_id if x == 1 else ''})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


# supported query params:
# search_key = XXX
# status = XXX
# update_ts = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = update_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@api.get('/api/v1/search_tasks')
def get_search_crawl_tasks():
    logger = get_logger()
    try:
        select_exps = []
        sort = SearchCrawlTask.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.args.items():
            if k == 'search_key':
                select_exps.append(SearchCrawlTask.search_key == v)
            elif k == 'status':
                select_exps.append(SearchCrawlTask.status == int(v))
            elif k == 'update_ts':
                select_exps += parse_param_compare(SearchCrawlTask.update_ts, v)
            elif k == 'update_id':
                select_exps.append(SearchCrawlTask.update_id == v)
            elif k == 'sort':
                sort_columns = {
                    'update_ts': SearchCrawlTask.update_ts,
                    'update_id': SearchCrawlTask.update_id
                }
                if v in sort_columns:
                    sort = sort_columns[v]
            elif k == 'desc':
                desc = True
            elif k == 'limit':
                limit = int(v)
            elif k == 'offset':
                offset = int(v)
        sort = sort.desc() if desc else sort
        if len(select_exps) == 0:
            query = SearchCrawlTask.select().order_by(sort).limit(limit).offset(offset)
        else:
            query = SearchCrawlTask.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.get('/api/v1/llm_task/<task_id>')
def get_llm_analyze_task_by_id(task_id):
    logger = get_logger()
    try:
        p = LLMAnalyzeTask.get(LLMAnalyzeTask.id == task_id)
        return build_success_response({'data': p.to_dict()})
    except DoesNotExist:
        msg = f'id={task_id} not found'
        logger.info(f'invalid id={task_id}, not found')
        return build_not_found_response(msg)
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.put('/api/v1/llm_task')
def create_llm_analyze_task():
    logger = get_logger()
    try:
        start_ts = int(time.time()) - TB_LLM_ANALYZE_TASK_PERIOD_IN_SECONDS
        payload = request.json
        tasks = LLMAnalyzeTask.select().where(LLMAnalyzeTask.product_id == payload.get('product_id'),
                                              LLMAnalyzeTask.status != TASK_STATUS_DONE,
                                              LLMAnalyzeTask.status != TASK_STATUS_ARCHIVED,
                                              LLMAnalyzeTask.update_ts > start_ts)
        task_id = ''
        if len(tasks) == 0 or payload.get('force') == 'true':
            task_id = add_llm_analyze_task(payload.get('product_id'),
                                           payload.get('product_title'),
                                           {},
                                           payload.get('update_id'),
                                           create_llm_analyze_task.__name__)
        else:
            logger.info(
                f'same task already exist for product_id={payload.get("product_id")} and "force" is not set to "true", just ignore')
        return build_success_response({'task_id': task_id})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.delete('/api/v1/llm_task/<task_id>')
def delete_llm_analyze_task(task_id):
    logger = get_logger()
    try:
        x = LLMAnalyzeTask.delete().where(LLMAnalyzeTask.id == task_id).execute()
        return build_success_response({'task_id': task_id if x == 1 else ''})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


# supported query params:
# product_id = XXX
# status = XXX
# update_ts = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = update_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@api.get('/api/v1/llm_tasks')
def get_llm_analyze_tasks():
    logger = get_logger()
    try:
        select_exps = []
        sort = LLMAnalyzeTask.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.args.items():
            if k == 'product_id':
                select_exps.append(LLMAnalyzeTask.product_id == v)
            elif k == 'status':
                select_exps.append(LLMAnalyzeTask.status == int(v))
            elif k == 'update_ts':
                select_exps += parse_param_compare(LLMAnalyzeTask.update_ts, v)
            elif k == 'update_id':
                select_exps.append(LLMAnalyzeTask.update_id == v)
            elif k == 'sort':
                sort_columns = {
                    'update_ts': LLMAnalyzeTask.update_ts,
                    'update_id': LLMAnalyzeTask.update_id
                }
                if v in sort_columns:
                    sort = sort_columns[v]
            elif k == 'desc':
                desc = True
            elif k == 'limit':
                limit = int(v)
            elif k == 'offset':
                offset = int(v)
        sort = sort.desc() if desc else sort
        if len(select_exps) == 0:
            query = LLMAnalyzeTask.select().order_by(sort).limit(limit).offset(offset)
        else:
            query = LLMAnalyzeTask.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.get('/api/v1/shop_search_task/<task_id>')
def get_shop_search_crawl_task_by_id(task_id):
    logger = get_logger()
    try:
        p = ShopSearchCrawlTask.get(ShopSearchCrawlTask.id == task_id)
        return build_success_response({'data': p.to_dict()})
    except DoesNotExist:
        msg = f'id={task_id} not found'
        logger.info(f'invalid id={task_id}, not found')
        return build_not_found_response(msg)
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.put('/api/v1/shop_search_task')
def create_shop_search_task():
    logger = get_logger()
    try:
        start_ts = int(time.time()) - TB_SHOP_SEARCH_CRAWL_TASK_PERIOD_IN_SECONDS
        payload = request.json
        tasks = ShopSearchCrawlTask.select().where(ShopSearchCrawlTask.shop_name == payload.get('shop_name'),
                                                   ShopSearchCrawlTask.status != TASK_STATUS_DONE,
                                                   ShopSearchCrawlTask.status != TASK_STATUS_ARCHIVED,
                                                   ShopSearchCrawlTask.update_ts > start_ts)
        task_id = ''
        if len(tasks) == 0 or payload.get('force') == 'true':
            task_id = add_shop_search_crawl_task(payload.get('shop_name'),
                                                 {},
                                                 payload.get('update_id'),
                                                 create_shop_search_task.__name__)
        else:
            logger.info(
                f'same task already exist for shop_name={payload.get("shop_name")} and "force" is not set to "true", just ignore')
        return build_success_response({'task_id': task_id})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@api.delete('/api/v1/shop_search_task/<task_id>')
def delete_shop_search_crawl_task(task_id):
    logger = get_logger()
    try:
        x = ShopSearchCrawlTask.delete().where(ShopSearchCrawlTask.id == task_id).execute()
        return build_success_response({'task_id': task_id if x == 1 else ''})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


# supported query params:
# shop_name = XXX
# status = XXX
# update_ts = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = update_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@api.get('/api/v1/shop_search_tasks')
def get_shop_search_crawl_tasks():
    logger = get_logger()
    try:
        select_exps = []
        sort = ShopSearchCrawlTask.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.args.items():
            if k == 'shop_name':
                select_exps.append(ShopSearchCrawlTask.shop_name == v)
            elif k == 'status':
                select_exps.append(ShopSearchCrawlTask.status == int(v))
            elif k == 'update_ts':
                select_exps += parse_param_compare(ShopSearchCrawlTask.update_ts, v)
            elif k == 'update_id':
                select_exps.append(ShopSearchCrawlTask.update_id == v)
            elif k == 'sort':
                sort_columns = {
                    'update_ts': ShopSearchCrawlTask.update_ts,
                    'update_id': ShopSearchCrawlTask.update_id
                }
                if v in sort_columns:
                    sort = sort_columns[v]
            elif k == 'desc':
                desc = True
            elif k == 'limit':
                limit = int(v)
            elif k == 'offset':
                offset = int(v)
        sort = sort.desc() if desc else sort
        if len(select_exps) == 0:
            query = ShopSearchCrawlTask.select().order_by(sort).limit(limit).offset(offset)
        else:
            query = ShopSearchCrawlTask.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)
