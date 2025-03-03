# coding: utf-8
# !./bin/python

import time
import datetime
import csv
import re
import traceback
from enum import Enum
from json import dumps
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeDriverService
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchWindowException, ElementClickInterceptedException
from taobao.config import *
from taobao.utils import *
from taobao.models import *

TAOBAO_LOGIN_PAGE = 'https://login.taobao.com/member/login.jhtml'
TAOBAO_SEARCH_PAGE = 'https://s.taobao.com/search'
TB_PERSONAL_HOMEPAGE_TITLE_NAME = '我的淘宝'
TB_HOMEPAGE_TITLE_NAME = '淘宝'
LOGIN_CHECK_INTERVAL_IN_SECONDS = 5
DRIVER_IMPLICIT_WAIT_IN_SECONDS = 10
SEARCH_WAIT_IN_SECONDS = 10
DETAIL_PAGE_WAIT_IN_SECONDS = 10
CLICK_INTERCEPTED_WAIT_IN_SECONDS = 1
TB_PAGE_DEFAULT_ZOOM_RATIO = 0.5
MAX_SKU_ITEMS_NUM = 5

SKU_CARD_RE_EXP = re.compile('^doubleCard--')
SKU_MAIN_PIC_AND_DESC_RE_EXP = re.compile('^mainPicAndDesc--')
SKU_SHOP_INFO_RE_EXP = re.compile('^shopInfo--')
SKU_ITEMS_RE_EXP = re.compile('^skuItem--')
INNER_SKU_ITEMS_RE_EXP = re.compile('^content--')
SKU_PRICE_RE_EXP = re.compile('^highlightPrice--')
SKU_PRICE_UNIT_RE_EXP = re.compile('symbol--')
SKU_PRICE_VAL_RE_EXP = re.compile('text--')
SKU_TITLE_IMGS_RE_EXP = re.compile('^thumbnailsWrap--')
SKU_MAIN_IMGS_RE_EXP = re.compile('^descV8-container')

COMMODITIES_IN_ONE_SEARCH = set()


class WebDriverType(Enum):
    ChromDriver = 1
    SafariDriver = 2


def init_webdriver(webdriver_type: WebDriverType):
    logger = get_logger()
    logger.info('start init %s webdriver ...' % webdriver_type)
    driver = None
    if webdriver_type == WebDriverType.ChromDriver:
        driver_service = ChromeDriverService('/Users/hengliu/Path/chromedriver')
        driver = webdriver.Chrome(service=driver_service)
    elif webdriver_type == WebDriverType.SafariDriver:
        options = webdriver.SafariOptions()
        driver = webdriver.Safari(options=options)
    logger.info('%s webdriver initialized' % webdriver_type)
    return driver


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


def zoom_content(ratio):
    zoom_script = 'document.body.style.zoom="%f"' % ratio
    Driver.execute_script(zoom_script)


def scroll_window(x, y):
    x = x if x is not None else 'document.body.scrollWidth'
    y = y if y is not None else 'document.body.scrollHeight'
    scroll_script = 'window.scrollTo(%s, %s)' % (str(x), str(y))
    Driver.execute_script(scroll_script)


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


def craw_taobao_search(qstring, num_of_pages):
    login_taobao()
    enter_query_string(qstring)
    crawl_taobao_search_results(qstring, num_of_pages)


def set_driver_implicit_wait(seconds):
    logger = get_logger()
    logger.info('set driver implicit wait to %d seconds' % seconds)
    Driver.implicitly_wait(seconds)


def enter_query_string(qstring):
    logger = get_logger()
    logger.info('navigate to taobao search page')
    Driver.get(TAOBAO_SEARCH_PAGE)
    qbox = Driver.find_element(By.ID, 'q')
    qbox.clear()
    qbox.send_keys(qstring)
    qbox.send_keys(Keys.RETURN)
    logger.info('searching %s' % qstring)
    global COMMODITIES_IN_ONE_SEARCH
    COMMODITIES_IN_ONE_SEARCH = set()


def crawl_taobao_search_results(qstring, num_of_pages):
    logger = get_logger()
    sku_info_list = []
    for i in range(1, num_of_pages + 1):
        try:
            # TBD: 在这里检查是否有滑动验证弹窗，并解决 (<div class='nocaptcha>, XPATH 'div/div/div' .text)
            logger.info('wait search results for seconds')
            time.sleep(SEARCH_WAIT_IN_SECONDS)
            search_result_wrapper = Driver.find_element(By.ID, 'content_items_wrapper')
            search_results = search_result_wrapper.find_elements(By.XPATH, 'div/a')
            logger.info('find %d search results' % len(search_results))
            for search_result in search_results:
                parse_taobao_search_result(search_result, sku_info_list)
            btn_pages = Driver.find_elements(By.CLASS_NAME, 'next-pagination-pages')
            assert (len(btn_pages) >= 1)  # 至少下面会有一个导航栏
            btn_list = btn_pages[-1].find_elements(By.XPATH, 'button')
            assert (len(btn_list) == 3)  # 下面导航栏里直属三个按钮：上一页，下一页，确定
            while True:
                try:
                    logger.info('get search results for page %d by press next page' % (i + 1))
                    btn_list[1].click()
                    break
                except ElementClickInterceptedException:
                    logger.error(
                        'got ElementClickInterceptedException, wait several seconds and try again, may need human intervention')
                    traceback.print_exc()
                    time.sleep(CLICK_INTERCEPTED_WAIT_IN_SECONDS)
        except NoSuchWindowException:
            logger.error('window is closed, now program will quit, searched results will be saved')
            traceback.print_exc()
            break
        except AssertionError:
            logger.error('assertion failed in search result page, just stop crawling')
            traceback.print_exc()
            break
        except Exception:
            logger.error('get unexcepted exception while parsing search results, just stop crawling')
            traceback.print_exc()
            break
    output_file = '%s/%s_%s_%dpages.csv' % (
        OUTPUT_DIR, qstring, datetime.datetime.now().strftime('%Y%m%d%H%M%S'), num_of_pages)
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = [ID, SKU_ID, SKU_TITLE, SKU_LINK, SKU_IMG_LINK,
                      SHOP_NAME, SHOP_LINK,
                      SKU_PRICE_UNIT, SKU_DISPLAY_PRICE, SKU_DISPLAY_SALE]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for item in sku_info_list:
            writer.writerow(item)


def parse_taobao_search_result(search_result, sku_info_list):
    logger = get_logger()
    try:
        logger.info('parsing search result: %s' % search_result.accessible_name)
        item_id = search_result.get_attribute('id')
        link = search_result.get_attribute('href')
        commodity_items = search_result.find_elements(By.XPATH, 'div/div')
        assert (len(commodity_items) == 3)
        sku_summary = None
        shop_summary = None
        for item in commodity_items:
            cls_name = item.get_attribute('class')
            if cls_name is None:
                continue
            if re.match(SKU_MAIN_PIC_AND_DESC_RE_EXP, cls_name):
                sku_summary = item
            if re.match(SKU_SHOP_INFO_RE_EXP, cls_name):
                shop_summary = item
        assert (sku_summary is not None and shop_summary is not None)
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
        display_sale = price_spans[1].text
        price_divs_inner = price_divs_wrapper[0].find_elements(By.XPATH, 'div')
        assert (len(price_divs_inner) == 2)
        display_price = '%s%s' % (price_divs_inner[0].text, price_divs_inner[1].text)
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
            SKU_DISPLAY_SALE: parse_sales(display_sale),
            SKU_PRICE_UNIT: parse_price_unit(price_unit),
            SKU_DISPLAY_PRICE: parse_price(display_price)
        }
        if sku_info[ID] not in COMMODITIES_IN_ONE_SEARCH:
            sku_info_list.append(sku_info)
        save_taobao_search_result(sku_info)
        COMMODITIES_IN_ONE_SEARCH.add(sku_info[ID])
    except AssertionError:
        logger.error('assertion failed while parsing %s' % search_result.accessible_name)
        logger.error('it may be caused by unloaded resources, just ignore it')
        traceback.print_exc()
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
        new_ci.details = ''
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
        new_cs.display_price = sku_info[SKU_DISPLAY_PRICE]
        new_cs.display_sale = sku_info[SKU_DISPLAY_SALE]
        new_cs.estimated_total_sale = sku_info[SKU_DISPLAY_PRICE] * sku_info[SKU_DISPLAY_SALE]
        new_cs.create_ts = ts
        new_cs.update_ts = ts
        new_cs.save(force_insert=True)


def craw_taobao_detail_page(commodity_link, commodity_id=None):
    logger = get_logger()
    login_taobao()
    logger.info('navigate to commodity link')
    Driver.get(commodity_link)
    logger.info('wait detail page for seconds')
    time.sleep(DETAIL_PAGE_WAIT_IN_SECONDS)
    logger.info('set detail page zoom ratio to %f' % TB_PAGE_DEFAULT_ZOOM_RATIO)
    zoom_content(TB_PAGE_DEFAULT_ZOOM_RATIO)
    craw_taobao_detail_page_result(commodity_id)


def craw_taobao_detail_page_result(commodity_id):
    # find all sku items, which is the basic aspect of an offer
    logger = get_logger()
    divs = Driver.find_elements(By.XPATH, '//div')
    sku_items_divs = []
    sku_price_div = None
    title_image_div = None
    main_image_div = None
    for div in divs:
        cls_name = div.get_attribute('class')
        if cls_name is None:
            continue
        if re.match(SKU_ITEMS_RE_EXP, cls_name):
            sku_items_divs.append(div)
        elif re.match(SKU_PRICE_RE_EXP, cls_name):
            sku_price_div = div
        elif re.match(SKU_TITLE_IMGS_RE_EXP, cls_name):
            title_image_div = div
        elif re.match(SKU_MAIN_IMGS_RE_EXP, cls_name):
            main_image_div = div
    assert (len(sku_items_divs) < MAX_SKU_ITEMS_NUM)
    assert (sku_price_div is not None)
    assert (main_image_div is not None)
    # parse all sku items
    value_items_divs = []
    sku_items = []
    for sku_items_div in sku_items_divs:
        content_div = None
        inner_divs = sku_items_div.find_elements(By.XPATH, 'div')
        for inner_div in inner_divs:
            cls_name = inner_div.get_attribute('class')
            if cls_name is None:
                continue
            if re.match(INNER_SKU_ITEMS_RE_EXP, cls_name):
                content_div = inner_div
                break
        sku_item_list = []
        value_item_divs = content_div.find_elements(By.XPATH, 'div')
        value_items_divs.append(value_item_divs)
        for value_item_div in value_item_divs:
            sku_item = craw_taobao_value_item_result(value_item_div)
            assert (sku_item is not None)
            sku_item_list.append(sku_item)
        sku_items.append(sku_item_list)
    # parse all prices
    offers = craw_taobao_sku_prices(value_items_divs, sku_price_div)
    commodity_details = {
        "sku_items": sku_items,
        "valid_offers": offers
    }
    logger.info('get commodity [%s] details: %s' % (commodity_id, commodity_details))
    # parse title images
    title_imgs = title_image_div.find_elements(By.XPATH, 'ul/li/img')
    title_images = [title_img.get_attribute('src') for title_img in title_imgs]
    logger.info('get title image list: %s' % title_images)
    # parse main images
    main_imgs = main_image_div.find_elements(By.XPATH, 'div/img')
    main_images = [main_img.get_attribute('src') for main_img in main_imgs]
    logger.info('get main image list: %s' % main_images)
    # update commodity info in DB
    if commodity_id is not None:
        update_commodity_info(commodity_id, title_images, main_images, commodity_details)


def update_commodity_info(commodity_id, title_imgs, main_imgs, details):
    logger = get_logger()
    ts = int(time.time())
    try:
        exist_ci = CommodityInfo.get(CommodityInfo.id == commodity_id)
        exist_ci.title_imgs = dumps(title_imgs)
        exist_ci.page_imgs = main_imgs
        exist_ci.details = details
        exist_ci.update_ts = ts
        exist_ci.save()
    except DoesNotExist:
        logger.info('commodity [%s] not exist, ignore commodity detail update' % commodity_id)


def craw_taobao_sku_prices(value_items_divs, sku_price_div):
    combos = get_value_item_combos(value_items_divs)
    offers = []
    for combo in combos:
        offer = []
        valid = True
        for value_item in combo:
            cls_name = value_item.get_attribute('class')
            if cls_name is not None and cls_name.find('isDisabled') != -1:
                valid = False
                break
            span = value_item.find_element(By.XPATH, 'span')
            offer.append(span.text)
            value_item.click()
        if not valid:
            continue
        price_spans = sku_price_div.find_elements(By.XPATH, 'span')
        assert (len(price_spans) >= 2)
        price_unit_span = None
        price_val_span = None
        for price_span in price_spans:
            cls_name = price_span.get_attribute('class')
            if cls_name is None:
                continue
            elif re.match(SKU_PRICE_UNIT_RE_EXP, cls_name):
                price_unit_span = price_span
            elif re.match(SKU_PRICE_VAL_RE_EXP, cls_name):
                price_val_span = price_span
        assert (price_unit_span is not None and price_val_span is not None)
        offer.append(parse_price_unit(price_unit_span.text))
        offer.append(parse_price(price_val_span.text))
        offers.append(offer)
    return offers


def get_value_item_combos(value_items_divs):
    combos = []
    combo = []
    inner_get_value_item_combos(value_items_divs, 0, combo, combos)
    return combos


def inner_get_value_item_combos(value_items_divs, cur, combo, combos):
    if len(combo) == len(value_items_divs):
        combos.append(combo.copy())
        return
    for value_item in value_items_divs[cur]:
        combo.append(value_item)
        inner_get_value_item_combos(value_items_divs, cur + 1, combo, combos)
        combo.pop()


def craw_taobao_value_item_result(value_item):
    logger = get_logger()
    sku_item = {}
    try:
        span = value_item.find_element(By.XPATH, 'span')
        sku_item['name'] = span.text
    except Exception:
        logger.error('get exception while parsing value_item span, %s' % value_item.accessible_name)
        traceback.print_exc()
        return None
    try:
        img = value_item.find_element(By.XPATH, 'img')
        sku_item['img'] = img.get_attribute('src')
    except Exception:
        logger.error('some sku_item do not have img, just ignore')
    return sku_item


Driver = init_webdriver(WebDriverType.ChromDriver)
