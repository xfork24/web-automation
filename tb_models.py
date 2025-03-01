# coding: utf-8
# !./bin/python
import time

from peewee import *
from tb_config import (
    DB_NAME,
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_PORT,
    DB_CHARSET)

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


class CommodityInfo(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    sku_id = CharField(max_length=32, index=True)
    title = CharField(max_length=128)
    link = CharField(max_length=512)
    shop_name = CharField(max_length=128, index=True)
    title_imgs = CharField(max_length=4096)
    page_imgs = CharField(max_length=4096)
    detail = CharField(max_length=4096)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)

    class Meta:
        table_name = 'commodity_info'


class ShopInfo(BaseModel):
    name = CharField(max_length=128, primary_key=True)
    link = CharField(max_length=512)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)

    class Meta:
        table_name = 'shop_info'


class CommoditySales(BaseModel):
    id = CharField(max_length=32)
    ts = IntegerField()
    shop_name = CharField(max_length=128, index=True)
    price_unit = CharField(max_length=3)
    price = IntegerField()
    sale = IntegerField(index=True)
    total_sale = IntegerField(index=True)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)

    class Meta:
        table_name = 'commodity_sales'
        primary_key = CompositeKey('id', 'ts')


class CrawlTasks(BaseModel):
    id = IntegerField(primary_key=True)
    commodity_id = CharField(max_length=32, index=True)
    link = CharField(max_length=512)
    status = SmallIntegerField(index=True)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)

    class Meta:
        table_name = 'crawl_tasks'
