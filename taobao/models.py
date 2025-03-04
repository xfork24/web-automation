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


class CommodityInfo(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    sku_id = CharField(max_length=32, index=True)
    title = CharField(max_length=128)
    link = CharField(max_length=512)
    shop_name = CharField(max_length=128, index=True)
    title_imgs = CharField(max_length=4096)
    page_imgs = CharField(max_length=4096)
    details = CharField(max_length=4096)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'commodity_info'


class ShopInfo(BaseModel):
    name = CharField(max_length=128, primary_key=True)
    link = CharField(max_length=512)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'shop_info'


class CommoditySales(BaseModel):
    id = CharField(max_length=32)
    ts = IntegerField()
    shop_name = CharField(max_length=128, index=True)
    price_unit = CharField(max_length=3)
    display_price = IntegerField()
    display_sale = IntegerField(index=True)
    estimated_total_sale = IntegerField(index=True)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'commodity_sales'
        primary_key = CompositeKey('id', 'ts')


class DetailCrawlTasks(BaseModel):
    id = IntegerField(primary_key=True)
    commodity_id = CharField(max_length=32, index=True)
    link = CharField(max_length=512)
    status = SmallIntegerField(index=True)
    create_ts = IntegerField()
    update_ts = IntegerField(index=True)
    update_role = CharField(max_length=64)

    class Meta:
        table_name = 'detail_crawl_tasks'
