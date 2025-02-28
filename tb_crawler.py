# coding: utf-8
# !./bin/python
import enum
import sys
import time
import csv
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

import logging

LOGGING_FORMAT = '%(asctime)s %(message)s'
TAOBAO_MAIN_PAGE = 'https://www.taobao.com'
TAOBAO_SEARCH_PAGE = 'https://s.taobao.com/search'
TAOBAO_LOGIN_PAGE = 'https://login.taobao.com/member/login.jhtml'
LOGIN_PAGE_DISPLAY_CHECK_INTERVAL_IN_SECONDS = 1
NUM_OF_PAGES_TO_PARSE = 10
LOGIN_CHECK_INTERVAL_IN_SECONDS = 10
SEARCH_WAIT_IN_SECONDS = 10
Driver: webdriver.Chrome = None
LOG_FILE_NAME = 'tb_crawler.log'
DOM_TB_HOME_SEARCH_BOX_ID = 'q'
DOM_TB_SEARCH_RESULT_WRAPPER_ID = 'content_items_wrapper'
DOM_LOGIN_FORM_ID = 'login'
TB_PERSONAL_HOMEPAGE_TITLE_NAME = '我的淘宝'
TB_HOMEPAGE_TITLE_NAME = '淘宝'
QUERY_STRING = '美剧'
SAVE_TO_FILE_PATH = '%sTops.csv' % QUERY_STRING
SKU_LINK = 'link'
SKU_IMG_LINK = 'img_link'
SKU_TITLE = 'title'
SKU_SALES = 'sales'
SKU_PRICE_UNIT = 'price_unit'
SKU_PRICE = 'price'
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
            Driver.find_element(By.ID, DOM_LOGIN_FORM_ID)
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


def craw_taobao(qstring):
    init_webdriver(WebDriverType.ChromDriver)
    login_taobao()
    enter_query_string(qstring)
    parse_taobao_search_results()


def enter_query_string(qstring):
    logger = get_logger()
    logger.info('navigate to taobao search page')
    Driver.get(TAOBAO_SEARCH_PAGE)
    qbox = Driver.find_element(By.ID, DOM_TB_HOME_SEARCH_BOX_ID)
    qbox.clear()
    qbox.send_keys(qstring)
    qbox.send_keys(Keys.RETURN)
    logger.info('searching %s' % qstring)
    logger.info('wait search results for %d seconds' % SEARCH_WAIT_IN_SECONDS)
    time.sleep(SEARCH_WAIT_IN_SECONDS)


def parse_taobao_search_results():
    logger = get_logger()
    sku_info_list = []
    for i in range(NUM_OF_PAGES_TO_PARSE):
        try:
            search_result_wrapper = Driver.find_element(By.ID, DOM_TB_SEARCH_RESULT_WRAPPER_ID)
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
        except Exception as e:
            logger.error('get exception, ', str(e))
            continue
    with open(SAVE_TO_FILE_PATH, 'w', newline='') as csvfile:
        fieldnames = [SKU_TITLE, SKU_LINK, SKU_IMG_LINK, SKU_PRICE_UNIT, SKU_PRICE, SKU_SALES]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for item in sku_info_list:
            writer.writerow(item)


def parse_sales(sales):
    sales_num = sales[:-3]
    if sales_num[-1] == '+':
        sales_num = sales_num[:-1]
    if sales_num[-1] == '万':
        sales_num = sales_num[:-1] + '0000'
    return int(sales_num)


def parse_taobao_search_result(search_result, sku_info_list):
    logger = get_logger()
    try:
        logger.info('parsing search result: %s' % search_result.accessible_name)
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
        sku_info_list.append({
            SKU_LINK: link,
            SKU_IMG_LINK: img_link,
            SKU_TITLE: title,
            SKU_SALES: parse_sales(sales),
            SKU_PRICE_UNIT: price_unit,
            SKU_PRICE: price
        })
    except Exception as e:
        logger.error('get exception: ', e)


if __name__ == '__main__':
    init_logger()
    craw_taobao(QUERY_STRING)
