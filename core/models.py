# coding: utf-8
# !./bin/python

import re
import time
from uuid import uuid4
from peewee import *
from core.utils import *
from core.config import (
    DB_NAME,
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_PORT,
    DB_CHARSET)
from core.utils import get_logger
from json import JSONDecodeError
from playhouse.shortcuts import model_to_dict

SHOP_COVER_DEFAULT_LINK = 'https://img.alicdn.com/imgextra/i1/O1CN01pz5irY1bhDKceJor2_!!6000000003496-2-tps-144-144.png_320x320q75.jpg_.webp'
LLM_ANALYSIS_KEY = 'llm_analysis'
ERRORS_KEY = 'errors'

DB_OPS_CREATE_NEW = 1
DB_OPS_UPDATE_EXIST = 2
DB_OPS_DELETE_RECORD = 3

TASK_STATUS_NEW = 1
TASK_STATUS_RUNNING = 2
TASK_STATUS_DONE = 3
TASK_STATUS_ERROR = 4
TASK_STATUS_ARCHIVED = 5

TASK_FAILED_UNEXPECTED_ERROR = 1
TASK_FAILED_SHOP_NOT_STANDARD = 2
TASK_FAILED_SHOP_SKU_EXCEEDS_LIMIT = 3
TASK_FAILED_SHOP_NOT_EXIST = 4
TASK_FAILED_SHOP_LINK_NOT_ACCESSIBLE = 5
TASK_FAILED_SHOP_NOT_FOUND_IN_SEARCH = 6
TASK_FAILED_SHOP_LINK_NOT_FOUND = 7

SHOP_LINK_KNOWN_RE_EXP_LIST = [re.compile('^https://store.taobao.com/shop/view_shop.htm'),
                               re.compile('^https://shop\\w+.taobao.com/')]

DB = MySQLDatabase(DB_NAME,
                   host=DB_HOST,
                   port=DB_PORT,
                   user=DB_USER,
                   password=DB_PASSWORD,
                   charset=DB_CHARSET)
DB.connect(reuse_if_open=True)


def close_db():
    logger = get_logger()
    logger.info('close DB instance ...')
    DB.close()


class BaseModel(Model):
    class Meta:
        database = DB

    def to_json(self, recurse=False):
        jsonv = dict()
        x = model_to_dict(self, recurse)
        for k, v in x.items():
            try:
                if not isinstance(v, str):
                    continue
                if re.match(re.compile('^[\[\{][\\s\\S]*[\]\}]$'), v):
                    jsonv[k] = json_loads(v)
            except JSONDecodeError:
                continue
        x.update(jsonv)
        return x

    def table_name(self):
        return self._meta.table_name


class ShopInfo(BaseModel):
    shop_name = CharField(max_length=128, primary_key=True)
    shop_link = CharField(max_length=512)
    shop_cover = CharField(max_length=512)
    additional_properties = TextField()
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'shop_info'


class ProductInfo(BaseModel):
    product_id = CharField(max_length=32, primary_key=True)
    sku_id = CharField(max_length=32, index=True)
    product_title = CharField(max_length=128)
    product_link = CharField(max_length=512)
    product_cover = CharField(max_length=512)
    shop_name = ForeignKeyField(ShopInfo, backref='productinfos', column_name='shop_name', lazy_load=False)
    shop_link = CharField(max_length=512)
    price_unit = CharField(max_length=3)
    display_price = IntegerField()
    display_sale = IntegerField(index=True)
    estimated_revenue = IntegerField(index=True)
    title_imgs = TextField()
    page_imgs = TextField()
    offer_details = TextField()
    additional_properties = TextField()
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'product_info'


class ProductSale(BaseModel):
    product_id = ForeignKeyField(ProductInfo, backref='productsales', column_name='product_id', lazy_load=False)
    shop_name = ForeignKeyField(ShopInfo, backref='productsales', column_name='shop_name', lazy_load=False)
    price_unit = CharField(max_length=3)
    display_price = IntegerField()
    display_sale = IntegerField(index=True)
    estimated_revenue = IntegerField(index=True)
    additional_properties = TextField()
    create_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'product_sale'
        primary_key = CompositeKey('product_id', 'create_ts')


class HotProduct(BaseModel):
    product_id = ForeignKeyField(ProductInfo, backref='hotproducts', column_name='product_id', lazy_load=False)
    shop_name = ForeignKeyField(ShopInfo, backref='hotproducts', column_name='shop_name', lazy_load=False)
    additional_properties = TextField()
    create_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'hot_product'
        primary_key = CompositeKey('product_id', 'create_ts')


class OperationHistory(BaseModel):
    id = IntegerField()
    pk = CharField(max_length=128)
    table_name = CharField(max_length=32)
    additional_properties = TextField()
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)
    operation_ts = IntegerField()
    operation = IntegerField()
    create_ts = IntegerField(index=True)

    class Meta:
        table_name = 'operation_history'
        indexes = (
            (('pk', 'table_name'), False),
            (('update_id', 'operation_ts'), False),
        )


class DetailCrawlTask(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    product_id = ForeignKeyField(ProductInfo, backref='detailcrawltasks', column_name='product_id', lazy_load=False)
    product_link = CharField(max_length=512)
    status = SmallIntegerField(index=True)
    try_count = IntegerField()
    additional_properties = TextField()
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'detail_crawl_task'


class ShopCrawlTask(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    shop_name = ForeignKeyField(ShopInfo, backref='shopcrawltasks', column_name='shop_name', lazy_load=False)
    target_product_ids = CharField(max_length=1024)
    status = SmallIntegerField(index=True)
    try_count = IntegerField()
    additional_properties = TextField()
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'shop_crawl_task'


class SearchCrawlTask(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    search_key = CharField(max_length=128, index=True)
    num_of_pages = IntegerField()
    target_product_ids = CharField(max_length=1024)
    status = SmallIntegerField(index=True)
    try_count = IntegerField()
    additional_properties = TextField()
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'search_crawl_task'


class LLMAnalyzeTask(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    product_id = ForeignKeyField(ProductInfo, backref='llmanalyzetasks', column_name='product_id', lazy_load=False)
    product_title = CharField(max_length=128)
    status = SmallIntegerField(index=True)
    try_count = IntegerField()
    additional_properties = TextField()
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'llm_analyze_task'


class ShopSearchCrawlTask(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    shop_name = ForeignKeyField(ShopInfo, backref='shopsearchcrawltasks', column_name='shop_name', lazy_load=False)
    status = SmallIntegerField(index=True)
    try_count = IntegerField()
    additional_properties = TextField()
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'shop_search_crawl_task'


def update_product_info(product_id, update_id, update_role,
                        sku_id='', product_title='', product_link='', product_cover='',
                        shop_name='', shop_link='',
                        price_unit='', display_price=-1, display_sale=-1,
                        title_imgs=None, page_imgs=None, offer_details=None, additional_properties=None):
    # update product_info table
    logger = get_logger()
    ts = int(time.time())
    try:
        # if record already exists, update only if value is valid
        exist_pi = ProductInfo.get(ProductInfo.product_id == product_id)
        original_json = exist_pi.to_json()
        if sku_id != '':
            exist_pi.sku_id = sku_id
        if product_title != '':
            exist_pi.product_title = product_title
        if product_link != '':
            exist_pi.product_link = product_link
        if product_cover != '':
            exist_pi.product_cover = product_cover
        if shop_name != '':
            exist_pi.shop_name = shop_name
        shop_link_match = False
        for reg_exp in SHOP_LINK_KNOWN_RE_EXP_LIST:
            if re.match(reg_exp, shop_link):
                shop_link_match = True
                break
        if shop_link_match:
            exist_pi.shop_link = shop_link
        else:
            logger.info(f'find shop_name={shop_name} with unknown link={shop_link}, exist record not updated')
        if price_unit != '':
            exist_pi.price_unit = price_unit
        if display_price != -1:
            exist_pi.display_price = display_price
        if display_sale != -1:
            exist_pi.display_sale = display_sale
        if exist_pi.display_price >= 0 and exist_pi.display_sale >= 0:
            exist_pi.estimated_revenue = exist_pi.display_price * exist_pi.display_sale
        else:
            exist_pi.estimated_revenue = -1
        if title_imgs is not None:
            exist_pi.title_imgs = json_dumps(title_imgs)
        if page_imgs is not None:
            exist_pi.page_imgs = json_dumps(page_imgs)
        if offer_details is not None:
            exist_pi.offer_details = json_dumps(offer_details)
        if additional_properties is not None:
            exist_pi.additional_properties = json_dumps(additional_properties)
        exist_pi.update_ts = ts
        exist_pi.update_id = update_id
        exist_pi.update_role = update_role
        exist_pi.save()
        updated_json = exist_pi.to_json()
        logger.info(f'exist product info record updated: {exist_pi.to_json()}')
        add_operation_history(product_id, exist_pi.table_name(),
                              {'diff': json_diff(original_json, updated_json)},
                              update_id, update_role, ts,
                              DB_OPS_UPDATE_EXIST)
    except DoesNotExist:
        new_pi = ProductInfo()
        new_pi.product_id = product_id
        new_pi.sku_id = sku_id
        new_pi.product_title = product_title
        new_pi.product_link = product_link
        new_pi.product_cover = product_cover
        new_pi.shop_name = shop_name
        new_pi.shop_link = shop_link
        new_pi.price_unit = price_unit
        new_pi.display_price = display_price
        new_pi.display_sale = display_sale
        if new_pi.display_price >= 0 and new_pi.display_sale >= 0:
            new_pi.estimated_revenue = new_pi.display_price * new_pi.display_sale
        else:
            new_pi.estimated_revenue = -1
        if title_imgs is not None:
            new_pi.title_imgs = json_dumps(title_imgs)
        else:
            new_pi.title_imgs = json_dumps({})
        if page_imgs is not None:
            new_pi.page_imgs = json_dumps(page_imgs)
        else:
            new_pi.page_imgs = json_dumps({})
        if offer_details is not None:
            new_pi.offer_details = json_dumps(offer_details)
        else:
            new_pi.offer_details = json_dumps({})
        if additional_properties is not None:
            new_pi.additional_properties = json_dumps(additional_properties)
        else:
            new_pi.additional_properties = json_dumps({})
        new_pi.create_ts = ts
        new_pi.update_ts = ts
        new_pi.update_id = update_id
        new_pi.update_role = update_role
        new_pi.save(force_insert=True)
        logger.info(f'new product info record inserted: {new_pi.to_json()}')
        add_operation_history(product_id, new_pi.table_name(),
                              {'diff': json_diff({}, new_pi.to_json())},
                              update_id, update_role, ts, DB_OPS_CREATE_NEW)


def update_shop_info(shop_name, update_id, update_role, shop_link='', shop_cover='', additional_properties=None):
    # update shop_info table
    logger = get_logger()
    ts = int(time.time())
    try:
        # update only when value is valid
        exist_si = ShopInfo.get(ShopInfo.shop_name == shop_name)
        original_json = exist_si.to_json()
        shop_link_match = False
        for reg_exp in SHOP_LINK_KNOWN_RE_EXP_LIST:
            if re.match(reg_exp, shop_link):
                shop_link_match = True
                break
        if shop_link_match:
            exist_si.shop_link = shop_link
        else:
            logger.info(f'find shop_name={shop_name} with unknown link={shop_link}, exist record not updated')
        if shop_cover != '':
            exist_si.shop_cover = shop_cover
        if additional_properties is not None:
            exist_si.additional_properties = json_dumps(additional_properties)
        exist_si.update_ts = ts
        exist_si.update_id = update_id
        exist_si.update_role = update_role
        exist_si.save()
        updated_json = exist_si.to_json()
        logger.info(f'exist shop info record updated: {exist_si.to_json()}')
        add_operation_history(shop_name, exist_si.table_name(),
                              {'diff': json_diff(original_json, updated_json)},
                              update_id, update_role, ts, DB_OPS_UPDATE_EXIST)
    except DoesNotExist:
        new_si = ShopInfo()
        new_si.shop_name = shop_name
        new_si.shop_link = shop_link
        new_si.shop_cover = SHOP_COVER_DEFAULT_LINK if shop_cover == '' else shop_cover
        if additional_properties is not None:
            new_si.additional_properties = json_dumps(additional_properties)
        else:
            new_si.additional_properties = json_dumps({})
        new_si.create_ts = ts
        new_si.update_ts = ts
        new_si.update_id = update_id
        new_si.update_role = update_role
        new_si.save(force_insert=True)
        logger.info(f'new shop info record inserted: {new_si.to_json()}')
        add_operation_history(shop_name, new_si.table_name(),
                              {'diff': json_diff({}, new_si.to_json())},
                              update_id, update_role, ts, DB_OPS_CREATE_NEW)


def add_product_sale(product_id, shop_name,
                     price_unit, display_price, display_sale,
                     additional_properties, update_id, update_role):
    logger = get_logger()
    ts = int(time.time())
    estimated_revenue = display_price * display_sale
    estimated_revenue = -1 if estimated_revenue < 0 else estimated_revenue
    # 有些情况下（比如shop中）同样的商品可以出现多次，所以这里我们仍然要检查一下是否有键重复
    try:
        ProductSale.get(ProductSale.product_id == product_id, ProductSale.create_ts == ts)
        logger.error(f'product sale record already exist, id = {product_id} and update_ts = {ts}, just ignore')
    except DoesNotExist:
        new_ps = ProductSale()
        new_ps.product_id = product_id
        new_ps.shop_name = shop_name
        new_ps.price_unit = price_unit
        new_ps.display_price = display_price
        new_ps.display_sale = display_sale
        new_ps.estimated_revenue = estimated_revenue
        if additional_properties is not None:
            new_ps.additional_properties = json_dumps(additional_properties)
        else:
            new_ps.additional_properties = json_dumps({})
        new_ps.create_ts = ts
        new_ps.update_id = update_id
        new_ps.update_role = update_role
        new_ps.save(force_insert=True)
        updated_json = new_ps.to_json()
        logger.info(f'new product sale record inserted: {new_ps.to_json()}')
        add_operation_history(f'{product_id},{ts}', new_ps.table_name(),
                              {'diff': json_diff({}, updated_json)},
                              update_id, update_role, ts, DB_OPS_CREATE_NEW)


def add_operation_history(pk, table_name, additional_properties, update_id, update_role, operation_ts, operation):
    logger = get_logger()
    new_oh = OperationHistory()
    new_oh.pk = pk
    new_oh.table_name = table_name
    if additional_properties is not None:
        new_oh.additional_properties = json_dumps(additional_properties)
    else:
        new_oh.additional_properties = json_dumps({})
    new_oh.update_id = update_id
    new_oh.update_role = update_role
    new_oh.operation_ts = operation_ts
    new_oh.operation = operation
    new_oh.create_ts = int(time.time())
    new_oh.save(force_insert=True)
    logger.info(f'new operation history record inserted: {new_oh.to_json()}')
    return new_oh.id


def add_detail_crawl_task(product_id, link, additional_properties, update_id, update_role):
    logger = get_logger()
    ts = int(time.time())
    pk = uuid4().hex
    new_dct = DetailCrawlTask()
    new_dct.id = pk
    new_dct.product_id = product_id
    new_dct.product_link = link
    new_dct.status = TASK_STATUS_NEW
    new_dct.try_count = 0
    if additional_properties is not None:
        new_dct.additional_properties = json_dumps(additional_properties)
    else:
        new_dct.additional_properties = json_dumps({})
    new_dct.create_ts = ts
    new_dct.update_ts = ts
    new_dct.update_id = update_id
    new_dct.update_role = update_role
    new_dct.save(force_insert=True)
    logger.info(f'new detail crawl task record inserted: {new_dct.to_json()}')
    add_operation_history(pk, new_dct.table_name(),
                          {'diff': json_diff({}, new_dct.to_json())},
                          update_id, update_role, ts, DB_OPS_CREATE_NEW)
    return pk


def add_shop_crawl_task(shop_name, target_product_ids, additional_properties, update_id, update_role):
    logger = get_logger()
    ts = int(time.time())
    pk = uuid4().hex
    new_sct = ShopCrawlTask()
    new_sct.id = pk
    new_sct.shop_name = shop_name
    new_sct.target_product_ids = json_dumps(target_product_ids) if target_product_ids is not None else json_dumps([])
    new_sct.status = TASK_STATUS_NEW
    new_sct.try_count = 0
    if additional_properties is not None:
        new_sct.additional_properties = json_dumps(additional_properties)
    else:
        new_sct.additional_properties = json_dumps({})
    new_sct.create_ts = ts
    new_sct.update_ts = ts
    new_sct.update_id = update_id
    new_sct.update_role = update_role
    new_sct.save(force_insert=True)
    logger.info(f'new shop crawl task record inserted: {new_sct.to_json()}')
    add_operation_history(pk, new_sct.table_name(),
                          {'diff': json_diff({}, new_sct.to_json())},
                          update_id, update_role, ts, DB_OPS_CREATE_NEW)
    return pk


def add_search_crawl_task(search_key, num_of_pages, target_product_ids, additional_properties, update_id, update_role):
    logger = get_logger()
    ts = int(time.time())
    pk = uuid4().hex
    new_sct = SearchCrawlTask()
    new_sct.id = pk
    new_sct.search_key = search_key
    new_sct.num_of_pages = num_of_pages
    if target_product_ids is not None:
        new_sct.target_product_ids = json_dumps(target_product_ids)
    else:
        new_sct.target_product_ids = json_dumps([])
    new_sct.status = TASK_STATUS_NEW
    new_sct.try_count = 0
    if additional_properties is not None:
        new_sct.additional_properties = json_dumps(additional_properties)
    else:
        new_sct.additional_properties = json_dumps({})
    new_sct.create_ts = ts
    new_sct.update_ts = ts
    new_sct.update_id = update_id
    new_sct.update_role = update_role
    new_sct.save(force_insert=True)
    logger.info(f'new search crawl task record inserted: {new_sct.to_json()}')
    add_operation_history(pk, new_sct.table_name(),
                          {'diff': json_diff({}, new_sct.to_json())},
                          update_id, update_role, ts, DB_OPS_CREATE_NEW)
    return pk


def add_llm_analyze_task(product_id, product_title, additional_properties, update_id, update_role):
    logger = get_logger()
    ts = int(time.time())
    pk = uuid4().hex
    new_lat = LLMAnalyzeTask()
    new_lat.id = pk
    new_lat.product_id = product_id
    new_lat.product_title = product_title
    new_lat.status = TASK_STATUS_NEW
    new_lat.try_count = 0
    if additional_properties is not None:
        new_lat.additional_properties = json_dumps(additional_properties)
    else:
        new_lat.additional_properties = json_dumps({})
    new_lat.create_ts = ts
    new_lat.update_ts = ts
    new_lat.update_id = update_id
    new_lat.update_role = update_role
    new_lat.save(force_insert=True)
    logger.info(f'new llm analyze task record inserted: {new_lat.to_json()}')
    add_operation_history(pk, new_lat.table_name(),
                          {'diff': json_diff({}, new_lat.to_json())},
                          update_id, update_role, ts, DB_OPS_CREATE_NEW)
    return pk


def add_shop_search_crawl_task(shop_name, additional_properties, update_id, update_role):
    logger = get_logger()
    ts = int(time.time())
    pk = uuid4().hex
    new_sct = ShopSearchCrawlTask()
    new_sct.id = pk
    new_sct.shop_name = shop_name
    new_sct.status = TASK_STATUS_NEW
    new_sct.try_count = 0
    if additional_properties is not None:
        new_sct.additional_properties = json_dumps(additional_properties)
    else:
        new_sct.additional_properties = json_dumps({})
    new_sct.create_ts = ts
    new_sct.update_ts = ts
    new_sct.update_id = update_id
    new_sct.update_role = update_role
    new_sct.save(force_insert=True)
    logger.info(f'new shop search crawl task record inserted: {new_sct.to_json()}')
    add_operation_history(pk, new_sct.table_name(),
                          {'diff': json_diff({}, new_sct.to_json())},
                          update_id, update_role, ts, DB_OPS_CREATE_NEW)
    return pk


def add_hot_product(product_id, shop_name, additional_properties, update_id, update_role):
    logger = get_logger()
    ts = int(time.time())
    new_hp = HotProduct()
    new_hp.product_id = product_id
    new_hp.shop_name = shop_name
    if additional_properties is not None:
        new_hp.additional_properties = json_dumps(additional_properties)
    else:
        new_hp.additional_properties = json_dumps({})
    new_hp.create_ts = ts
    new_hp.update_id = update_id
    new_hp.update_role = update_role
    new_hp.save(force_insert=True)
    logger.info(f'new hot product record inserted: {new_hp.to_json()}')
    add_operation_history(f'{product_id},{ts}', new_hp.table_name(),
                          {'diff': json_diff({}, new_hp.to_json())},
                          update_id, update_role, ts, DB_OPS_CREATE_NEW)


def update_task_info(task, update_id, status=None,
                     target_product_ids=None, num_of_pages=None,
                     err_code=None, call_stack=None):
    logger = get_logger()
    original_json = task.to_json()
    ts = int(time.time())
    if err_code is not None:
        additional_properties = json_loads(task.additional_properties)
        if ERRORS_KEY not in additional_properties:
            additional_properties[ERRORS_KEY] = []
        errors = additional_properties[ERRORS_KEY]
        error_entity = {'update_ts': ts, 'err_code': err_code}
        if call_stack is not None:
            error_entity['call_stack'] = call_stack
        errors.append(error_entity)
        additional_properties[ERRORS_KEY] = errors
        task.additional_properties = json_dumps(additional_properties)
    if target_product_ids is not None:
        task.target_product_ids = json_dumps(target_product_ids)
    if num_of_pages is not None:
        task.num_of_pages = num_of_pages
    task.status = status if status is not None else task.status
    task.update_id = update_id
    task.update_role = update_task_info.__name__
    task.update_ts = ts
    task.save()
    updated_json = task.to_json()
    logger.info(f'update task id={task.id} status to {status}')
    add_operation_history(task.id, task.table_name(),
                          {'diff': json_diff(original_json, updated_json)},
                          update_id, update_task_info.__name__, ts, DB_OPS_UPDATE_EXIST)


def delete_product(product_id, update_id):
    logger = get_logger()
    ts = int(time.time())
    try:
        # 关联删除所有hot_product
        hot_products = HotProduct.select().where(HotProduct.product_id == product_id)
        for hot_product in hot_products:
            delete_hot_product(hot_product.product_id, hot_product.create_ts, update_id)
        # 关联删除所有product_sale
        product_sales = ProductSale.select().where(ProductSale.product_id == product_id)
        for product_sale in product_sales:
            delete_product_sale(product_sale.product_id, product_sale.create_ts, update_id)
        # 关联删除所有detail_crawl_task
        detail_crawl_tasks = DetailCrawlTask.select().where(DetailCrawlTask.product_id == product_id)
        for detail_crawl_task in detail_crawl_tasks:
            delete_detail_crawl_task(detail_crawl_task.id, update_id)
        # 关联删除所有llm_analyze_task
        llm_analyze_tasks = LLMAnalyzeTask.select().where(LLMAnalyzeTask.product_id == product_id)
        for llm_analyze_task in llm_analyze_tasks:
            delete_llm_analyze_task(llm_analyze_task.id, update_id)
        # 删除product_info
        exist_pi = ProductInfo.get(ProductInfo.product_id == product_id)
        original_json = exist_pi.to_json()
        x = ProductInfo.delete().where(ProductInfo.product_id == product_id).execute()
        add_operation_history(product_id, exist_pi.table_name(),
                              {'diff': json_diff(original_json, {})},
                              update_id, delete_product.__name__, ts, DB_OPS_DELETE_RECORD)
        return x
    except DoesNotExist:
        logger.info(f'product with product_id={product_id} does not exist')
        return 0
    except IntegrityError:
        logger.info(f'integrity check failed and product_id={product_id} can not be deleted')
        return 0


def delete_shop(shop_name, update_id):
    logger = get_logger()
    ts = int(time.time())
    try:
        # 关联删除所有product_info
        product_infos = ProductInfo.select().where(ProductInfo.shop_name == shop_name)
        for product_info in product_infos:
            delete_product(product_info.product_id, update_id)
        # 关联删除所有shop_crawl_task
        shop_crawl_tasks = ShopCrawlTask.select().where(ShopCrawlTask.shop_name == shop_name)
        for shop_crawl_task in shop_crawl_tasks:
            delete_shop_crawl_task(shop_crawl_task.id, update_id)
        # 关联删除所有shop_search_crawl_task
        shop_search_crawl_tasks = ShopSearchCrawlTask.select().where(ShopSearchCrawlTask.shop_name == shop_name)
        for shop_search_crawl_task in shop_search_crawl_tasks:
            delete_shop_search_crawl_task(shop_search_crawl_task.id, update_id)
        # 删除shop_info
        exist_si = ShopInfo.get(ShopInfo.shop_name == shop_name)
        original_json = exist_si.to_json()
        x = ShopInfo.delete().where(ShopInfo.shop_name == shop_name).execute()
        add_operation_history(shop_name, exist_si.table_name(),
                              {'diff': json_diff(original_json, {})},
                              update_id, delete_shop.__name__, ts, DB_OPS_DELETE_RECORD)
        return x
    except DoesNotExist:
        logger.info(f'shop with shop_name={shop_name} does not exist')
        return 0
    except IntegrityError:
        logger.info(f'integrity check failed and shop_name={shop_name} can not be deleted')
        return 0


def delete_product_sale(product_id, create_ts, update_id):
    logger = get_logger()
    ts = int(time.time())
    try:
        exist_ps = ProductSale.get(ProductSale.product_id == product_id,
                                   ProductSale.create_ts == create_ts)
        original_json = exist_ps.to_json()
        x = ProductSale.delete().where(ProductSale.product_id == product_id,
                                       ProductSale.create_ts == create_ts).execute()
        add_operation_history(f'{product_id},{create_ts}', exist_ps.table_name(),
                              {'diff': json_diff(original_json, {})},
                              update_id, delete_product_sale.__name__, ts, DB_OPS_DELETE_RECORD)
        return x
    except DoesNotExist:
        logger.info(f'product sale with product_id={product_id}, create_ts={create_ts} does not exist')
        return 0
    except IntegrityError:
        logger.info(f'integrity check failed and product_id={product_id}, create_ts={create_ts} can not be deleted')
        return 0


def delete_hot_product(product_id, create_ts, update_id):
    logger = get_logger()
    ts = int(time.time())
    try:
        exist_hp = HotProduct.get(HotProduct.product_id == product_id,
                                  HotProduct.create_ts == create_ts)
        original_json = exist_hp.to_json()
        x = HotProduct.delete().where(HotProduct.product_id == product_id,
                                      HotProduct.create_ts == create_ts).execute()
        add_operation_history(f'{product_id},{create_ts}', exist_hp.table_name(),
                              {'diff': json_diff(original_json, {})},
                              update_id, delete_hot_product.__name__, ts, DB_OPS_DELETE_RECORD)
        return x
    except DoesNotExist:
        logger.info(f'hot product with product_id={product_id}, create_ts={create_ts} does not exist')
        return 0
    except IntegrityError:
        logger.info(f'integrity check failed and product_id={product_id}, create_ts={create_ts} can not be deleted')
        return 0


def delete_detail_crawl_task(task_id, update_id):
    logger = get_logger()
    ts = int(time.time())
    try:
        exist_dct = DetailCrawlTask.get(DetailCrawlTask.id == task_id)
        original_json = exist_dct.to_json()
        x = DetailCrawlTask.delete().where(DetailCrawlTask.id == task_id).execute()
        add_operation_history(task_id, exist_dct.table_name(),
                              {'diff': json_diff(original_json, {})},
                              update_id, delete_detail_crawl_task.__name__, ts, DB_OPS_DELETE_RECORD)
        return x
    except DoesNotExist:
        logger.info(f'shop with task_id={task_id} does not exist')
        return 0
    except IntegrityError:
        logger.info(f'integrity check failed and task_id={task_id} can not be deleted')
        return 0


def delete_shop_crawl_task(task_id, update_id):
    logger = get_logger()
    ts = int(time.time())
    try:
        exist_sct = ShopCrawlTask.get(ShopCrawlTask.id == task_id)
        original_json = exist_sct.to_json()
        x = ShopCrawlTask.delete().where(ShopCrawlTask.id == task_id).execute()
        add_operation_history(task_id, exist_sct.table_name(),
                              {'diff': json_diff(original_json, {})},
                              update_id, delete_shop_crawl_task.__name__, ts, DB_OPS_DELETE_RECORD)
        return x
    except DoesNotExist:
        logger.info(f'shop with task_id={task_id} does not exist')
        return 0
    except IntegrityError:
        logger.info(f'integrity check failed and task_id={task_id} can not be deleted')
        return 0


def delete_search_crawl_task(task_id, update_id):
    logger = get_logger()
    ts = int(time.time())
    try:
        exist_sct = SearchCrawlTask.get(SearchCrawlTask.id == task_id)
        original_json = exist_sct.to_json()
        x = SearchCrawlTask.delete().where(SearchCrawlTask.id == task_id).execute()
        add_operation_history(task_id, exist_sct.table_name(),
                              {'diff': json_diff(original_json, {})},
                              update_id, delete_search_crawl_task.__name__, ts, DB_OPS_DELETE_RECORD)
        return x
    except DoesNotExist:
        logger.info(f'shop with task_id={task_id} does not exist')
        return 0
    except IntegrityError:
        logger.info(f'integrity check failed and task_id={task_id} can not be deleted')
        return 0


def delete_llm_analyze_task(task_id, update_id):
    logger = get_logger()
    ts = int(time.time())
    try:
        exist_lat = LLMAnalyzeTask.get(LLMAnalyzeTask.id == task_id)
        original_json = exist_lat.to_json()
        x = LLMAnalyzeTask.delete().where(LLMAnalyzeTask.id == task_id).execute()
        add_operation_history(task_id, exist_lat.table_name(),
                              {'diff': json_diff(original_json, {})},
                              update_id, delete_llm_analyze_task.__name__, ts, DB_OPS_DELETE_RECORD)
        return x
    except DoesNotExist:
        logger.info(f'shop with task_id={task_id} does not exist')
        return 0
    except IntegrityError:
        logger.info(f'integrity check failed and task_id={task_id} can not be deleted')
        return 0


def delete_shop_search_crawl_task(task_id, update_id):
    logger = get_logger()
    ts = int(time.time())
    try:
        exist_sct = ShopSearchCrawlTask.get(ShopSearchCrawlTask.id == task_id)
        original_json = exist_sct.to_json()
        x = ShopSearchCrawlTask.delete().where(ShopSearchCrawlTask.id == task_id).execute()
        add_operation_history(task_id, exist_sct.table_name(),
                              {'diff': json_diff(original_json, {})},
                              update_id, delete_shop_search_crawl_task.__name__, ts, DB_OPS_DELETE_RECORD)
        return x
    except DoesNotExist:
        logger.info(f'shop with task_id={task_id} does not exist')
        return 0
    except IntegrityError:
        logger.info(f'integrity check failed and task_id={task_id} can not be deleted')
        return 0
