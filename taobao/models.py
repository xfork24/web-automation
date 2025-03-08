# coding: utf-8
# !./bin/python

import time
from uuid import uuid4
from peewee import *
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


class CommodityInfo(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    sku_id = CharField(max_length=32, index=True)
    title = CharField(max_length=128)
    link = CharField(max_length=512)
    shop_name = CharField(max_length=128, index=True)
    price_unit = CharField(max_length=3)
    display_price = IntegerField()
    display_sale = IntegerField(index=True)
    estimated_revenue = IntegerField(index=True)
    title_imgs = CharField(max_length=4096)
    page_imgs = CharField(max_length=4096)
    details = CharField(max_length=4096)
    llm_analysis = CharField(max_length=1024)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'commodity_info'


class ShopInfo(BaseModel):
    name = CharField(max_length=128, primary_key=True)
    link = CharField(max_length=512)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'shop_info'


class CommoditySale(BaseModel):
    id = CharField(max_length=32)
    shop_name = CharField(max_length=128, index=True)
    price_unit = CharField(max_length=3)
    display_price = IntegerField()
    display_sale = IntegerField(index=True)
    estimated_revenue = IntegerField(index=True)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'commodity_sale'
        primary_key = CompositeKey('id', 'update_ts')


class OperationHistory(BaseModel):
    id = CharField(max_length=32)
    pk = CharField(max_length=128)
    table_name = CharField(max_length=32)
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
    commodity_id = CharField(max_length=32, index=True)
    link = CharField(max_length=512)
    status = SmallIntegerField(index=True)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'detail_crawl_task'


class ShopCrawlTask(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    shop_name = CharField(max_length=128, index=True)
    link = CharField(max_length=512)
    status = SmallIntegerField(index=True)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'shop_crawl_task'


class SearchCrawlTask(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    search_key = CharField(max_length=32, index=True)
    num_of_pages = IntegerField()
    status = SmallIntegerField(index=True)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_id = CharField(max_length=32, index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'search_crawl_task'


def update_commodity_info(commodity_id, sku_id, commodity_title, commodity_link, shop_name,
                          price_unit, display_price, display_sale,
                          title_imgs, main_imgs, details, llm_analysis, update_id, update_role):
    # update commodity_info table
    logger = get_logger()
    ts = int(time.time())
    estimated_revenue = display_price * display_sale
    estimated_revenue = -1 if estimated_revenue < 0 else estimated_revenue
    try:
        # if record already exists, update only if value is valid
        exist_ci = CommodityInfo.get(CommodityInfo.id == commodity_id)
        exist_ci.sku_id = sku_id if sku_id != '' else exist_ci.sku_id
        exist_ci.title = commodity_title if commodity_id != '' else exist_ci.title
        exist_ci.link = commodity_link if commodity_link != '' else exist_ci.link
        exist_ci.shop_name = shop_name if shop_name != '' else exist_ci.shop_name
        exist_ci.price_unit = price_unit if price_unit != '' else exist_ci.price_unit
        exist_ci.display_price = display_price if display_price != -1 else exist_ci.display_price
        exist_ci.display_sale = display_sale if display_sale != -1 else exist_ci.display_sale
        exist_ci.estimated_revenue = estimated_revenue if estimated_revenue != -1 else exist_ci.estimated_revenue
        exist_ci.title_imgs = title_imgs if title_imgs != '' else exist_ci.title_imgs
        exist_ci.page_imgs = main_imgs if main_imgs != '' else exist_ci.page_imgs
        exist_ci.details = details if details != '' else exist_ci.details
        exist_ci.llm_analysis = llm_analysis if llm_analysis != '' else exist_ci.llm_analysis
        exist_ci.update_ts = ts
        exist_ci.update_id = update_id
        exist_ci.update_role = update_role
        exist_ci.save()
        logger.info(f'exist commodity info record updated: {exist_ci.to_dict()}')
        add_operation_history(commodity_id, exist_ci.table_name(), update_id, update_role, ts,
                              DB_OPS_UPDATE_EXIST)
    except DoesNotExist:
        new_ci = CommodityInfo()
        new_ci.id = commodity_id
        new_ci.sku_id = sku_id
        new_ci.title = commodity_title
        new_ci.link = commodity_link
        new_ci.shop_name = shop_name
        new_ci.price_unit = price_unit
        new_ci.display_price = display_price
        new_ci.display_sale = display_sale
        new_ci.estimated_revenue = estimated_revenue
        new_ci.title_imgs = title_imgs
        new_ci.page_imgs = main_imgs
        new_ci.details = details
        new_ci.llm_analysis = llm_analysis
        new_ci.create_ts = ts
        new_ci.update_ts = ts
        new_ci.update_id = update_id
        new_ci.update_role = update_role
        new_ci.save(force_insert=True)
        logger.info(f'new commodity info record inserted: {new_ci.to_dict()}')
        add_operation_history(commodity_id, new_ci.table_name(), update_id, update_role, ts,
                              DB_OPS_CREATE_NEW)


def update_shop_info(shop_name, shop_link, update_id, update_role):
    # update shop_info table
    logger = get_logger()
    ts = int(time.time())
    try:
        # update only when value is valid
        exist_si = ShopInfo.get(ShopInfo.name == shop_name)
        exist_si.link = shop_link if shop_link != '' else exist_si.link
        exist_si.update_ts = ts
        exist_si.update_id = update_id
        exist_si.update_role = update_role
        exist_si.save()
        logger.info(f'exist shop info record updated: {exist_si.to_dict()}')
        add_operation_history(shop_name, exist_si.table_name(), update_id, update_role, ts, DB_OPS_UPDATE_EXIST)
    except DoesNotExist:
        new_si = ShopInfo()
        new_si.name = shop_name
        new_si.link = shop_link
        new_si.create_ts = ts
        new_si.update_ts = ts
        new_si.update_id = update_id
        new_si.update_role = update_role
        new_si.save(force_insert=True)
        logger.info(f'new shop info record inserted: {new_si.to_dict()}')
        add_operation_history(shop_name, new_si.table_name(), update_id, update_role, ts, DB_OPS_CREATE_NEW)


def add_commodity_sale(commodity_id, shop_name,
                       price_unit, display_price, display_sale,
                       update_id, update_role):
    logger = get_logger()
    ts = int(time.time())
    estimated_revenue = display_price * display_sale
    estimated_revenue = -1 if estimated_revenue < 0 else estimated_revenue
    # 有些情况下（比如shop中）同样的商品可以出现多次，所以这里我们仍然要检查一下是否有键重复
    try:
        CommoditySale.get(CommoditySale.id == commodity_id, CommoditySale.update_ts == ts)
        logger.error(f'commodity sale record already exist, id = {commodity_id} and update_ts = {ts}, just ignore')
    except DoesNotExist:
        new_cs = CommoditySale()
        new_cs.id = commodity_id
        new_cs.shop_name = shop_name
        new_cs.price_unit = price_unit
        new_cs.display_price = display_price
        new_cs.display_sale = display_sale
        new_cs.estimated_revenue = estimated_revenue
        new_cs.create_ts = ts
        new_cs.update_ts = ts
        new_cs.update_id = update_id
        new_cs.update_role = update_role
        new_cs.save(force_insert=True)
        logger.info(f'new commodity sale record inserted: {new_cs.to_dict()}')
        add_operation_history(f'{commodity_id},{ts}', new_cs.table_name(),
                              update_id, update_role, ts, DB_OPS_CREATE_NEW)


def add_operation_history(pk, table_name, update_id, update_role, operation_ts, operation):
    logger = get_logger()
    new_oh = OperationHistory()
    new_oh.pk = pk
    new_oh.table_name = table_name
    new_oh.update_id = update_id
    new_oh.update_role = update_role
    new_oh.operation_ts = operation_ts
    new_oh.operation = operation
    new_oh.create_ts = int(time.time())
    new_oh.save(force_insert=True)
    logger.info(f'new operation history record inserted: {new_oh.to_dict()}')


def add_detail_crawl_task(commodity_id, link, status, update_id, update_role):
    logger = get_logger()
    ts = int(time.time())
    pk = uuid4().hex
    new_dct = DetailCrawlTask()
    new_dct.id = pk
    new_dct.commodity_id = commodity_id
    new_dct.link = link
    new_dct.status = status
    new_dct.create_ts = ts
    new_dct.update_ts = ts
    new_dct.update_id = update_id
    new_dct.update_role = update_role
    new_dct.save(force_insert=True)
    logger.info(f'new detail crawl task record inserted: {new_dct.to_dict()}')
    add_operation_history(pk, new_dct.table_name(), update_id, update_role, ts, DB_OPS_CREATE_NEW)


def add_shop_crawl_task(shop_name, link, status, update_id, update_role):
    logger = get_logger()
    ts = int(time.time())
    pk = uuid4().hex
    new_sct = ShopCrawlTask()
    new_sct.id = pk
    new_sct.shop_name = shop_name
    new_sct.link = link
    new_sct.status = status
    new_sct.create_ts = ts
    new_sct.update_ts = ts
    new_sct.update_id = update_id
    new_sct.update_role = update_role
    new_sct.save(force_insert=True)
    logger.info(f'new shop crawl task record inserted: {new_sct.to_dict()}')
    add_operation_history(pk, new_sct.table_name(), update_id, update_role, ts, DB_OPS_CREATE_NEW)


def add_search_crawl_task(search_key, num_of_pages, status, update_id, update_role):
    logger = get_logger()
    ts = int(time.time())
    pk = uuid4().hex
    new_sct = SearchCrawlTask()
    new_sct.id = pk
    new_sct.search_key = search_key
    new_sct.num_of_pages = num_of_pages
    new_sct.status = status
    new_sct.create_ts = ts
    new_sct.update_ts = ts
    new_sct.update_id = update_id
    new_sct.update_role = update_role
    new_sct.save(force_insert=True)
    logger.info(f'new search crawl task record inserted: {new_sct.to_dict()}')
    add_operation_history(pk, new_sct.table_name(), update_id, update_role, ts, DB_OPS_CREATE_NEW)
