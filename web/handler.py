# coding: utf-8
# !./bin/python
# restful API for management console

from bottle import route, request
from core.models import *

DB_QUERY_DEFAULT_LIMIT = 10000
ERROR_CODE_SERVER_ERROR = -1
ERROR_CODE_NOT_FOUND = -11


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


@route('/api/v1/product/<product_id>', method='GET')
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
@route('/api/v1/products', method='GET')
def query_products():
    logger = get_logger()
    try:
        select_exps = []
        sort = ProductInfo.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.query.items():
            if k == 'shop_name':
                # OR use direct property access (request.query.shop_name) to decode automatically
                # See: https://stackoverflow.com/questions/27432211/python-bottle-requests-and-unicode
                select_exps.append(ProductInfo.shop_name == v.encode("ISO-8859-1").decode("utf-8"))
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
        query = ProductInfo.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@route('/api/v1/shop/<shop_name>', method='GET')
def get_shop_by_name(shop_name):
    logger = get_logger()
    try:
        p = ShopInfo.get(ShopInfo.shop_name == shop_name)
        return build_success_response({'data': p.to_dict()})
    except DoesNotExist:
        msg = f'shop_name={shop_name} not found'
        logger.info(f'invalid shop_name={shop_name}, not found')
        return build_not_found_response(msg)
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


# supported query params:
# shop_name = XXX
# update_ts = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = update_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@route('/api/v1/shops', method='GET')
def query_shops():
    logger = get_logger()
    try:
        select_exps = []
        sort = ShopInfo.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.query.items():
            if k == 'update_ts':
                select_exps += parse_param_compare(ShopInfo.update_ts, v)
            elif k == 'update_id':
                select_exps.append(ShopInfo.update_id == v)
            elif k == 'sort':
                sort_columns = {
                    'update_ts': ShopInfo.update_ts,
                    'update_id': ShopInfo.update_id
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
        query = ShopInfo.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@route('/api/v1/product_sale/<product_id>/<create_ts>', method='GET')
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


# supported query params:
# product_id = XXX
# shop_name = XXX
# update_ts = {"lt": 100, "gt": 30}
# display_sale = {"lt": 100, "gt": 30}
# estimated_revenue = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = create_ts or display_sale or estimated_revenue or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@route('/api/v1/product_sales', method='GET')
def query_product_sales():
    logger = get_logger()
    try:
        select_exps = []
        sort = ProductSale.create_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.query.items():
            if k == 'product_id':
                select_exps.append(ProductSale.product_id == v)
            elif k == 'shop_name':
                # OR use direct property access (request.query.shop_name) to decode automatically
                # See: https://stackoverflow.com/questions/27432211/python-bottle-requests-and-unicode
                select_exps.append(ProductSale.shop_name == v.encode("ISO-8859-1").decode("utf-8"))
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
        query = ProductSale.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@route('/api/v1/hot_product/<product_id>/<create_ts>', method='GET')
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


# supported query params:
# product_id = XXX
# shop_name = XXX
# create_ts = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = create_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@route('/api/v1/hot_product', method='GET')
def query_hot_products():
    logger = get_logger()
    try:
        select_exps = []
        sort = HotProduct.create_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.query.items():
            if k == 'product_id':
                select_exps.append(HotProduct.product_id == v)
            elif k == 'shop_name':
                # OR use direct property access (request.query.shop_name) to decode automatically
                # See: https://stackoverflow.com/questions/27432211/python-bottle-requests-and-unicode
                select_exps.append(HotProduct.shop_name == v.encode("ISO-8859-1").decode("utf-8"))
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
        query = HotProduct.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@route('/api/v1/operation_history/<history_id>', method='GET')
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
@route('/api/v1/operation_histories', method='GET')
def query_operation_histories():
    logger = get_logger()
    try:
        select_exps = []
        sort = OperationHistory.create_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.query.items():
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
        query = OperationHistory.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@route('/api/v1/detail_task/<task_id>', method='GET')
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


# supported query params:
# product_id = XXX
# status = XXX
# update_ts = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = update_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@route('/api/v1/detail_tasks', method='GET')
def get_detail_crawl_tasks():
    logger = get_logger()
    try:
        select_exps = []
        sort = DetailCrawlTask.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.query.items():
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
        query = DetailCrawlTask.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@route('/api/v1/shop_task/<task_id>', method='GET')
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


# supported query params:
# shop_name = XXX
# status = XXX
# update_ts = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = update_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@route('/api/v1/shop_tasks', method='GET')
def get_shop_crawl_tasks():
    logger = get_logger()
    try:
        select_exps = []
        sort = ShopCrawlTask.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.query.items():
            if k == 'shop_name':
                # OR use direct property access (request.query.shop_name) to decode automatically
                # See: https://stackoverflow.com/questions/27432211/python-bottle-requests-and-unicode
                select_exps.append(ShopCrawlTask.shop_name == v.encode("ISO-8859-1").decode("utf-8"))
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
        query = ShopCrawlTask.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@route('/api/v1/search_task/<task_id>', method='GET')
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


# supported query params:
# search_key = XXX
# status = XXX
# update_ts = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = update_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@route('/api/v1/search_tasks', method='GET')
def get_search_crawl_tasks():
    logger = get_logger()
    try:
        select_exps = []
        sort = SearchCrawlTask.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.query.items():
            if k == 'search_key':
                # OR use direct property access (request.query.shop_name) to decode automatically
                # See: https://stackoverflow.com/questions/27432211/python-bottle-requests-and-unicode
                select_exps.append(SearchCrawlTask.search_key == v.encode("ISO-8859-1").decode("utf-8"))
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
        query = SearchCrawlTask.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@route('/api/v1/llm_task/<task_id>', method='GET')
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


# supported query params:
# product_id = XXX
# status = XXX
# update_ts = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = update_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@route('/api/v1/llm_tasks', method='GET')
def get_llm_analyze_tasks():
    logger = get_logger()
    try:
        select_exps = []
        sort = LLMAnalyzeTask.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.query.items():
            if k == 'product_id':
                # OR use direct property access (request.query.shop_name) to decode automatically
                # See: https://stackoverflow.com/questions/27432211/python-bottle-requests-and-unicode
                select_exps.append(LLMAnalyzeTask.product_id == v.encode("ISO-8859-1").decode("utf-8"))
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
        query = LLMAnalyzeTask.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)


@route('/api/v1/shop_search_task/<task_id>', method='GET')
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


# supported query params:
# shop_name = XXX
# status = XXX
# update_ts = {"lt": 100, "gt": 30}
# update_id = XXX
# sort = update_ts or update_id
# desc = true or false
# limit = int(XXX)
# offset = int(XXX)
@route('/api/v1/shop_search_tasks', method='GET')
def get_shop_search_crawl_tasks():
    logger = get_logger()
    try:
        select_exps = []
        sort = ShopSearchCrawlTask.update_ts
        desc = False
        limit = DB_QUERY_DEFAULT_LIMIT
        offset = 0
        for k, v in request.query.items():
            if k == 'shop_name':
                # OR use direct property access (request.query.shop_name) to decode automatically
                # See: https://stackoverflow.com/questions/27432211/python-bottle-requests-and-unicode
                select_exps.append(ShopSearchCrawlTask.shop_name == v.encode("ISO-8859-1").decode("utf-8"))
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
        query = ShopSearchCrawlTask.select().where(*select_exps).order_by(sort).limit(limit).offset(offset)
        data = [q.to_dict() for q in query]
        return build_success_response({'data': data})
    except Exception as e:
        msg = f'get unhandled exception {e}'
        logger.error(msg)
        return build_server_error_response(msg)
