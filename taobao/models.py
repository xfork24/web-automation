# coding: utf-8
# !./bin/python

from peewee import *
from taobao.config import (
    DB_NAME,
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_PORT,
    DB_CHARSET)
from playhouse.shortcuts import model_to_dict

DB_OPS_CREATE_NEW = 1
DB_OPS_UPDATE_EXIST = 2

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
    estimated_total_sale = IntegerField(index=True)
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
