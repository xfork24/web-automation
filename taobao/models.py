# coding: utf-8
# !./bin/python

import re
import time
from uuid import uuid4
from peewee import *
from taobao.utils import json_dumps
from taobao.config import (
    DB_NAME,
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_PORT,
    DB_CHARSET)
from taobao.utils import get_logger
from playhouse.shortcuts import model_to_dict

DB_OPS_CREATE_NEW = 1
DB_OPS_UPDATE_EXIST = 2

TASK_STATUS_NEW = 1
TASK_STATUS_IN_PROGRESS = 2
TASK_STATUS_DONE = 3
TASK_STATUS_ERROR = 4

SHOP_LINK_RE_EXP_LIST = [re.compile('^https://store.taobao.com/shop/view_shop.htm'),
                         re.compile('^https://shop\\w+.taobao.com/')]

DB = MySQLDatabase(DB_NAME,
                   host=DB_HOST,
                   port=DB_PORT,
                   user=DB_USER,
                   password=DB_PASSWORD,
                   charset=DB_CHARSET)
DB.connect(reuse_if_open=True)


class BaseModel(Model):
    class Meta:
        database = DB

    def to_dict(self):
        return model_to_dict(self)

    def table_name(self):
        return self._meta.table_name


class ProductInfo(BaseModel):
    product_id = CharField(max_length=32, primary_key=True)
    sku_id = CharField(max_length=32, index=True)
    product_title = CharField(max_length=128)
    product_link = CharField(max_length=512)
    shop_name = CharField(max_length=128, index=True)
    price_unit = CharField(max_length=3)
    display_price = IntegerField()
    display_sale = IntegerField(index=True)
    estimated_revenue = IntegerField(index=True)
    title_imgs = CharField(max_length=4096)
    page_imgs = CharField(max_length=4096)
    details = CharField(max_length=4096)
    additional_properties = CharField(max_length=2048)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'product_info'


class ShopInfo(BaseModel):
    shop_name = CharField(max_length=128, primary_key=True)
    shop_link = CharField(max_length=512)
    additional_properties = CharField(max_length=2048)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'shop_info'


class ProductSale(BaseModel):
    product_id = CharField(max_length=32)
    shop_name = CharField(max_length=128, index=True)
    price_unit = CharField(max_length=3)
    display_price = IntegerField()
    display_sale = IntegerField(index=True)
    estimated_revenue = IntegerField(index=True)
    additional_properties = CharField(max_length=2048)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'product_sale'
        primary_key = CompositeKey('product_id', 'update_ts')


class HotProduct(BaseModel):
    product_id = CharField(max_length=32)
    shop_name = CharField(max_length=128)
    additional_properties = CharField(max_length=2048)
    create_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'hot_product'
        primary_key = CompositeKey('product_id', 'create_ts')


class OperationHistory(BaseModel):
    id = CharField(max_length=32)
    pk = CharField(max_length=128)
    table_name = CharField(max_length=32)
    additional_properties = CharField(max_length=2048)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)
    operation_ts = IntegerField()
    operation = IntegerField()
    create_ts = IntegerField(index=True)

    class Meta:
        table_name = 'operation_history'
        indexes = (
            (('pk', 'table_name'), False),
            (('update_role', 'operation_ts'), False),
        )


class DetailCrawlTask(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    product_id = CharField(max_length=32, index=True)
    product_link = CharField(max_length=512)
    status = SmallIntegerField(index=True)
    try_count = IntegerField()
    additional_properties = CharField(max_length=2048)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'detail_crawl_task'


class ShopCrawlTask(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    shop_name = CharField(max_length=128, index=True)
    target_product_ids = CharField(max_length=1024)
    status = SmallIntegerField(index=True)
    try_count = IntegerField()
    additional_properties = CharField(max_length=2048)
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
    additional_properties = CharField(max_length=2048)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'search_crawl_task'


class LLMAnalyzeTask(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    product_id = CharField(max_length=32, index=True)
    product_title = CharField(max_length=128)
    status = SmallIntegerField(index=True)
    try_count = IntegerField()
    additional_properties = CharField(max_length=2048)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'llm_analyze_task'


class ShopSearchCrawlTask(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    shop_name = CharField(max_length=128, index=True)
    status = SmallIntegerField(index=True)
    try_count = IntegerField()
    additional_properties = CharField(max_length=2048)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'shop_search_crawl_task'


def update_product_info(product_id, sku_id, product_title, product_link, shop_name,
                        price_unit, display_price, display_sale,
                        title_imgs, page_imgs, details, additional_properties, update_id, update_role):
    # update product_info table
    logger = get_logger()
    ts = int(time.time())
    estimated_revenue = display_price * display_sale
    estimated_revenue = -1 if estimated_revenue < 0 else estimated_revenue
    try:
        # if record already exists, update only if value is valid
        exist_pi = ProductInfo.get(ProductInfo.product_id == product_id)
        exist_pi.sku_id = sku_id if sku_id != '' else exist_pi.sku_id
        exist_pi.product_title = product_title if product_id != '' else exist_pi.product_title
        exist_pi.product_link = product_link if product_link != '' else exist_pi.product_link
        exist_pi.shop_name = shop_name if shop_name != '' else exist_pi.shop_name
        exist_pi.price_unit = price_unit if price_unit != '' else exist_pi.price_unit
        exist_pi.display_price = display_price if display_price != -1 else exist_pi.display_price
        exist_pi.display_sale = display_sale if display_sale != -1 else exist_pi.display_sale
        if estimated_revenue != -1:
            exist_pi.estimated_revenue = estimated_revenue
        if title_imgs is not None:
            exist_pi.title_imgs = json_dumps(title_imgs)
        if page_imgs is not None:
            exist_pi.page_imgs = json_dumps(page_imgs)
        if details is not None:
            exist_pi.details = json_dumps(details)
        if additional_properties is not None:
            exist_pi.additional_properties = json_dumps(additional_properties)
        exist_pi.update_ts = ts
        exist_pi.update_id = update_id
        exist_pi.update_role = update_role
        exist_pi.save()
        logger.info(f'exist product info record updated: {exist_pi.to_dict()}')
        add_operation_history(product_id, exist_pi.table_name(), None, update_id, update_role, ts, DB_OPS_UPDATE_EXIST)
    except DoesNotExist:
        new_pi = ProductInfo()
        new_pi.product_id = product_id
        new_pi.sku_id = sku_id
        new_pi.product_title = product_title
        new_pi.product_link = product_link
        new_pi.shop_name = shop_name
        new_pi.price_unit = price_unit
        new_pi.display_price = display_price
        new_pi.display_sale = display_sale
        new_pi.estimated_revenue = estimated_revenue
        if title_imgs is not None:
            new_pi.title_imgs = json_dumps(title_imgs)
        else:
            new_pi.title_imgs = json_dumps({})
        if page_imgs is not None:
            new_pi.page_imgs = json_dumps(page_imgs)
        else:
            new_pi.page_imgs = json_dumps({})
        if details is not None:
            new_pi.details = json_dumps(details)
        else:
            new_pi.details = json_dumps({})
        if additional_properties is not None:
            new_pi.additional_properties = json_dumps(additional_properties)
        else:
            new_pi.additional_properties = json_dumps({})
        new_pi.create_ts = ts
        new_pi.update_ts = ts
        new_pi.update_id = update_id
        new_pi.update_role = update_role
        new_pi.save(force_insert=True)
        logger.info(f'new product info record inserted: {new_pi.to_dict()}')
        add_operation_history(product_id, new_pi.table_name(), None, update_id, update_role, ts, DB_OPS_CREATE_NEW)


def update_shop_info(shop_name, shop_link, additional_properties, update_id, update_role):
    # update shop_info table
    logger = get_logger()
    ts = int(time.time())
    try:
        # update only when value is valid
        exist_si = ShopInfo.get(ShopInfo.shop_name == shop_name)
        exist_si.shop_link = shop_link if shop_link != '' else exist_si.shop_link
        if additional_properties is not None:
            exist_si.additional_properties = json_dumps(additional_properties)
        exist_si.update_ts = ts
        exist_si.update_id = update_id
        exist_si.update_role = update_role
        exist_si.save()
        logger.info(f'exist shop info record updated: {exist_si.to_dict()}')
        add_operation_history(shop_name, exist_si.table_name(), None, update_id, update_role, ts, DB_OPS_UPDATE_EXIST)
    except DoesNotExist:
        new_si = ShopInfo()
        new_si.shop_name = shop_name
        new_si.shop_link = shop_link
        if additional_properties is not None:
            new_si.additional_properties = json_dumps(additional_properties)
        else:
            new_si.additional_properties = json_dumps({})
        new_si.create_ts = ts
        new_si.update_ts = ts
        new_si.update_id = update_id
        new_si.update_role = update_role
        new_si.save(force_insert=True)
        logger.info(f'new shop info record inserted: {new_si.to_dict()}')
        add_operation_history(shop_name, new_si.table_name(), None, update_id, update_role, ts, DB_OPS_CREATE_NEW)


def add_product_sale(product_id, shop_name,
                     price_unit, display_price, display_sale,
                     additional_properties, update_id, update_role):
    logger = get_logger()
    ts = int(time.time())
    estimated_revenue = display_price * display_sale
    estimated_revenue = -1 if estimated_revenue < 0 else estimated_revenue
    # 有些情况下（比如shop中）同样的商品可以出现多次，所以这里我们仍然要检查一下是否有键重复
    try:
        ProductSale.get(ProductSale.product_id == product_id, ProductSale.update_ts == ts)
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
        new_ps.update_ts = ts
        new_ps.update_id = update_id
        new_ps.update_role = update_role
        new_ps.save(force_insert=True)
        logger.info(f'new product sale record inserted: {new_ps.to_dict()}')
        add_operation_history(f'{product_id},{ts}', new_ps.table_name(), None, update_id, update_role, ts,
                              DB_OPS_CREATE_NEW)


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
    logger.info(f'new operation history record inserted: {new_oh.to_dict()}')


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
    logger.info(f'new detail crawl task record inserted: {new_dct.to_dict()}')
    add_operation_history(pk, new_dct.table_name(), None, update_id, update_role, ts, DB_OPS_CREATE_NEW)


def add_shop_crawl_task(shop_name, target_product_ids, additional_properties, update_id, update_role):
    logger = get_logger()
    ts = int(time.time())
    pk = uuid4().hex
    new_sct = ShopCrawlTask()
    new_sct.id = pk
    new_sct.shop_name = shop_name
    new_sct.target_product_ids = json_dumps(target_product_ids) if target_product_ids is not None else json_dumps({})
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
    logger.info(f'new shop crawl task record inserted: {new_sct.to_dict()}')
    add_operation_history(pk, new_sct.table_name(), None, update_id, update_role, ts, DB_OPS_CREATE_NEW)


def add_search_crawl_task(search_key, num_of_pages, target_product_ids, additional_properties, update_id,
                          update_role):
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
        new_sct.target_product_ids = json_dumps({})
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
    logger.info(f'new search crawl task record inserted: {new_sct.to_dict()}')
    add_operation_history(pk, new_sct.table_name(), None, update_id, update_role, ts, DB_OPS_CREATE_NEW)


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
    logger.info(f'new llm analyze task record inserted: {new_lat.to_dict()}')
    add_operation_history(pk, new_lat.table_name(), None, update_id, update_role, ts, DB_OPS_CREATE_NEW)


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
    logger.info(f'new shop search crawl task record inserted: {new_sct.to_dict()}')
    add_operation_history(pk, new_sct.table_name(), None, update_id, update_role, ts, DB_OPS_CREATE_NEW)


def update_task_status(task, status, update_id, update_role):
    task.update_id = update_id
    task.update_role = update_role
    task.status = status
    task.save()
