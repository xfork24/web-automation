# coding: utf-8
# !./bin/python

import sys
import time
import logging
import datetime
import csv
import traceback
from enum import Enum
from urllib.parse import urlparse, parse_qs
from tb_config import LOGGING_FORMAT
from tb_models import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

LOGIN_CHECK_INTERVAL_IN_SECONDS = 10
SEARCH_WAIT_IN_SECONDS = 10
Driver: webdriver.Chrome = None
TAOBAO_SEARCH_PAGE = 'https://s.taobao.com/search'
TAOBAO_LOGIN_PAGE = 'https://login.taobao.com/member/login.jhtml'
LOG_FILE_NAME = './logs/tb_search_crawler.log'
TB_PERSONAL_HOMEPAGE_TITLE_NAME = '我的淘宝'
TB_HOMEPAGE_TITLE_NAME = '淘宝'

ID = 'id'
SKU_ID = 'sku_id'
SKU_LINK = 'link'
SKU_IMG_LINK = 'img_link'
SKU_TITLE = 'title'
SKU_SALES = 'sales'
SKU_PRICE_UNIT = 'price_unit'
SKU_PRICE = 'price'
SHOP_NAME = 'shop_name'
SHOP_LINK = 'shop_link'

QUERY_STRING = '美剧'
NUM_OF_PAGES_TO_PARSE = 10
COMMODITIES_IN_ONE_SEARCH = set()
DEBUG = True


class WebDriverType(Enum):
    ChromDriver = 1
    SafariDriver = 2


def init_logger():
    if DEBUG:
        logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stdout, level=logging.INFO)
    else:
        logging.basicConfig(format=LOGGING_FORMAT, filename=LOG_FILE_NAME, level=logging.INFO)


def get_logger(module_name=__name__):
    logger = logging.getLogger(module_name)
    return logger


def init_webdriver(webdriver_type: WebDriverType):
    global Driver
    if Driver is None:
        logger = get_logger()
        logger.info('start init %s webdriver ...' % webdriver_type)
        if webdriver_type == WebDriverType.ChromDriver:
            driver_service = Service('/Users/hengliu/Path/chromedriver')
            Driver = webdriver.Chrome(service=driver_service)
        elif webdriver_type == WebDriverType.SafariDriver:
            options = webdriver.SafariOptions()
            Driver = webdriver.Safari(options=options)
        logger.info('%s webdriver initialized' % webdriver_type)
    return Driver


def login_taobao():
    logger = get_logger()
    logger.info('forward to taobao login page')
    Driver.get(TAOBAO_LOGIN_PAGE)
    while True:
        try:
            logger.info('check taobao login status...')
            Driver.find_element(By.ID, 'login')
            time.sleep(LOGIN_CHECK_INTERVAL_IN_SECONDS)
        except NoSuchElementException:
            logger.info('can not find login form, you should already logged in and in taobao/personal homepage')
            break
    logger.info('check if we are in taobao/personal homepage')
    while True:
        if Driver.title == TB_PERSONAL_HOMEPAGE_TITLE_NAME or Driver.title == TB_HOMEPAGE_TITLE_NAME:
            logger.info('we are already in taobao/personal homepage, now perform following crawling')
            break
        else:
            logger.info(
                'we are not in taobao/personal homepage, finish authentication and navigate to taobao/personal homepage...')
            time.sleep(LOGIN_CHECK_INTERVAL_IN_SECONDS)


def craw_taobao_search(qstring):
    init_webdriver(WebDriverType.ChromDriver)
    login_taobao()
    enter_query_string(qstring)
    crawl_taobao_search_results()


def enter_query_string(qstring):
    logger = get_logger()
    logger.info('navigate to taobao search page')
    Driver.get(TAOBAO_SEARCH_PAGE)
    qbox = Driver.find_element(By.ID, 'q')
    qbox.clear()
    qbox.send_keys(qstring)
    qbox.send_keys(Keys.RETURN)
    logger.info('searching %s' % qstring)
    logger.info('wait search results for %d seconds' % SEARCH_WAIT_IN_SECONDS)
    time.sleep(SEARCH_WAIT_IN_SECONDS)
    global COMMODITIES_IN_ONE_SEARCH
    COMMODITIES_IN_ONE_SEARCH = set()


def crawl_taobao_search_results():
    logger = get_logger()
    sku_info_list = []
    for i in range(NUM_OF_PAGES_TO_PARSE):
        try:
            search_result_wrapper = Driver.find_element(By.ID, 'content_items_wrapper')
            search_results = search_result_wrapper.find_elements(By.XPATH, './div/a')
            logger.info('find %d search results' % len(search_results))
            for search_result in search_results:
                parse_taobao_search_result(search_result, sku_info_list)
            btn_pages = Driver.find_elements(By.CLASS_NAME, 'next-pagination-pages')
            assert (len(btn_pages) == 2)  # 上下各一个页数导航栏
            btn_list = btn_pages[1].find_elements(By.XPATH, 'button')
            assert (len(btn_list) == 3)  # 下面导航栏里直属三个按钮：上一页，下一页，确定
            btn_list[1].click()
            logger.info('wait search results for page %d for %d seconds' % (i + 1, SEARCH_WAIT_IN_SECONDS))
            time.sleep(SEARCH_WAIT_IN_SECONDS)
        except Exception:
            logger.error('get exception while parsing search results')
            traceback.print_exc()
            continue
    output_file = '%s_%s_%dpages.csv' % (
        QUERY_STRING, datetime.datetime.now().strftime('%Y%m%d%H%M%S'), NUM_OF_PAGES_TO_PARSE)
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = [ID, SKU_ID, SKU_TITLE, SKU_LINK, SKU_IMG_LINK,
                      SHOP_NAME, SHOP_LINK,
                      SKU_PRICE_UNIT, SKU_PRICE, SKU_SALES]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for item in sku_info_list:
            writer.writerow(item)


def parse_id(item_id):
    return item_id[item_id.rfind('_') + 1:]


def parse_sku_id(link):
    result = urlparse(link)
    qs = parse_qs(result.query)
    if 'skuId' in qs and len(qs['skuId']) == 1:
        return qs['skuId'][0]
    else:
        return '0'


def parse_sales(sales):
    sales_num = sales[:-3]
    if sales_num[-1] == '+':
        sales_num = sales_num[:-1]
    if sales_num[-1] == '万':
        sales_num = sales_num[:-1] + '0000'
    return int(sales_num)


def parse_price_unit(unit):
    if unit == '¥':
        return 'CNY'
    return unit


def parse_price(price):
    return int(float(price) * 100)


def parse_taobao_search_result(search_result, sku_info_list):
    logger = get_logger()
    try:
        logger.info('parsing search result: %s' % search_result.accessible_name)
        item_id = search_result.get_attribute('id')
        link = search_result.get_attribute('href')
        commodity_summary = search_result.find_elements(By.XPATH, 'div/div')
        assert (len(commodity_summary) == 3)
        sku_summary, _, shop_summary = commodity_summary
        sku_items = sku_summary.find_elements(By.XPATH, 'div')
        assert (len(sku_items) >= 4)
        if len(sku_items) == 4:
            sku_img_wrapper, sku_title_wrapper, _, price_wrapper = sku_items
        else:
            _, sku_img_wrapper, sku_title_wrapper, _, price_wrapper = sku_items
        sku_img_inner = sku_img_wrapper.find_element(By.XPATH, 'img')
        img_link = sku_img_inner.get_attribute('src')
        sku_title_inner = sku_title_wrapper.find_element(By.XPATH, 'div/span')
        title = sku_title_inner.text
        price_spans = price_wrapper.find_elements(By.XPATH, 'div/span')
        assert (len(price_spans) == 2)
        price_divs_wrapper = price_wrapper.find_elements(By.XPATH, 'div/div')
        assert (len(price_divs_wrapper) >= 2)
        price_unit = price_spans[0].text
        sales = price_spans[1].text
        price_divs_inner = price_divs_wrapper[0].find_elements(By.XPATH, 'div')
        assert (len(price_divs_inner) == 2)
        price = '%s%s' % (price_divs_inner[0].text, price_divs_inner[1].text)
        shop_info = shop_summary.find_element(By.XPATH, 'div/a')
        shop_link = shop_info.get_attribute('href')
        shop_name_wrapper = shop_info.find_elements(By.XPATH, 'div/span')
        shop_name = shop_name_wrapper[-1].text
        sku_info = {
            ID: parse_id(item_id),
            SKU_ID: parse_sku_id(link),
            SKU_LINK: link,
            SKU_IMG_LINK: img_link,
            SKU_TITLE: title,
            SHOP_NAME: shop_name,
            SHOP_LINK: shop_link,
            SKU_SALES: parse_sales(sales),
            SKU_PRICE_UNIT: parse_price_unit(price_unit),
            SKU_PRICE: parse_price(price)
        }
        if sku_info[ID] not in COMMODITIES_IN_ONE_SEARCH:
            sku_info_list.append(sku_info)
        save_taobao_search_result(sku_info)
        COMMODITIES_IN_ONE_SEARCH.add(sku_info[ID])
    except Exception:
        logger.error('get exception while parsing %s' % search_result.accessible_name)
        traceback.print_exc()


def save_taobao_search_result(sku_info):
    # save shop info
    ts = int(time.time())
    try:
        exist_si = ShopInfo.get(ShopInfo.name == sku_info[SHOP_NAME])
        exist_si.link = sku_info[SHOP_LINK]
        exist_si.update_ts = ts
        exist_si.save()
    except DoesNotExist:
        new_si = ShopInfo()
        new_si.name = sku_info[SHOP_NAME]
        new_si.link = sku_info[SHOP_LINK]
        new_si.create_ts = ts
        new_si.update_ts = ts
        new_si.save(force_insert=True)
    # save commodity info
    try:
        exist_ci = CommodityInfo.get(CommodityInfo.id == sku_info[ID])
        exist_ci.sku_id = sku_info[SKU_ID]
        exist_ci.title = sku_info[SKU_TITLE]
        exist_ci.link = sku_info[SKU_LINK]
        exist_ci.shop_name = sku_info[SHOP_NAME]
        exist_ci.update_ts = ts
    except DoesNotExist:
        new_ci = CommodityInfo()
        new_ci.id = sku_info[ID]
        new_ci.sku_id = sku_info[SKU_ID]
        new_ci.title = sku_info[SKU_TITLE]
        new_ci.link = sku_info[SKU_LINK]
        new_ci.shop_name = sku_info[SHOP_NAME]
        new_ci.title_imgs = ''
        new_ci.page_imgs = ''
        new_ci.detail = ''
        new_ci.create_ts = ts
        new_ci.update_ts = ts
        new_ci.save(force_insert=True)
    # save commodity sales info,
    # remember there can be same commodity in different search pages,
    # we only add one sale record for same commodity in one search process.
    if sku_info[ID] not in COMMODITIES_IN_ONE_SEARCH:
        new_cs = CommoditySales()
        new_cs.id = sku_info[ID]
        new_cs.ts = ts
        new_cs.shop_name = sku_info[SHOP_NAME]
        new_cs.price_unit = sku_info[SKU_PRICE_UNIT]
        new_cs.price = sku_info[SKU_PRICE]
        new_cs.sale = sku_info[SKU_SALES]
        new_cs.total_sale = sku_info[SKU_PRICE] * sku_info[SKU_SALES]
        new_cs.create_ts = ts
        new_cs.update_ts = ts
        new_cs.save(force_insert=True)


if __name__ == '__main__':
    init_logger()
    craw_taobao_search(QUERY_STRING)
