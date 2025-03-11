# coding: utf-8
# !./bin/python

import re
import traceback
import uuid
from enum import Enum
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeDriverService
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from taobao.config import *
from taobao.utils import *
from taobao.models import *

TB_LOGIN_PAGE = 'https://login.taobao.com/member/login.jhtml'
TB_SEARCH_PAGE = 'https://s.taobao.com/search'
TB_HOMEPAGE_TITLE_NAME = '淘宝'
TB_PERSONAL_HOMEPAGE_TITLE_NAME = '我的淘宝'
LOGIN_CHECK_WAIT_IN_SECONDS = 5
SEARCH_WAIT_IN_SECONDS = 5
DETAIL_PAGE_WAIT_IN_SECONDS = 5
SHOP_PAGE_WAIT_IN_SECONDS = 5
SHOP_PAGE_SKU_LOAD_WAIT_IN_SECONDS = 5
DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS = 1
TB_PAGE_DEFAULT_ZOOM_RATIO = 0.5
MAX_SKU_ITEMS_NUM = 5

TB_GO_LOGIN_RE_EXP = re.compile('^GoLoginInfo--\\w+')
SEARCH_SHOP_TAB_RE_EXP = re.compile('^baseStyle--\\w+')
SKU_MAIN_PIC_AND_DESC_RE_EXP = re.compile('^mainPicAndDesc--\\w+')
SKU_SEARCH_UNIT_RE_EXP = re.compile('^unit--\\w+')
SKU_SEARCH_SALE_RE_EXP = re.compile('^realSales--\\w+')
SKU_SHOP_INFO_RE_EXP = re.compile('^shopInfo--\\w+')
SKU_ITEMS_RE_EXP = re.compile('^skuItem--\\w+')
SKU_INNER_ITEMS_RE_EXP = re.compile('^content--\\w+')
SKU_PRICE_RE_EXP = re.compile('^highlightPrice--\\w+')
SKU_PRICE_UNIT_RE_EXP = re.compile('^symbol--\\w+')
SKU_PRICE_VAL_RE_EXP = re.compile('^text--\\w+')
SKU_SALE_RE_EXP = re.compile('^salesDesc--\\w+')
SKU_TITLE_IMGS_RE_EXP = re.compile('^thumbnailsWrap--\\w+')
SKU_MAIN_IMGS_RE_EXP = re.compile('^descV8-container$')
SKU_MAIN_IMGS_SINGLE_IMG_RE_EXP = re.compile('^descV8-singleImage$')
SKU_MAIN_IMGS_RICHTEXT_RE_EXP = re.compile('^descV8-richtext$')
SKU_SHOP_HEADER_RE_EXP = re.compile('^shopHeader--\\w+')
SKU_TITLE_RE_EXP = re.compile('^ItemTitle--\\w+')
SHOP_TITLE_RE_EXP = re.compile('^title--\\w+')
SHOP_NAME_RE_EXP = re.compile('^shopName--\\w+')
SHOP_SKU_CARD_RE_EXP = re.compile('^cardContainer--\\w+')
SHOP_SKU_CARD_TITLE_RE_EXP = re.compile('^title--\\w+')
SHOP_SKU_CARD_PRICE_RE_EXP = re.compile('^price--\\w+')
SHOP_SKU_CARD_SALE_RE_EXP = re.compile('^count--\\w+')
SHOP_LOAD_MORE_FLAG_RE_EXP = re.compile('^loadmoreFlag--\\w+')
SHOP_LOAD_STATUS_RE_EXP = re.compile('^loadStatus--\\w+')


class WebDriverType(Enum):
    ChromDriver = 1
    SafariDriver = 2


def init_webdriver(webdriver_type: WebDriverType):
    logger = get_logger()
    driver = None
    if webdriver_type == WebDriverType.ChromDriver:
        # TBD: handle hiding selenium from chrome, remove 'chrome is controlled by automated test software'
        driver_service = ChromeDriverService('/Users/hengliu/Path/chromedriver')
        options = webdriver.ChromeOptions()
        # options.add_experimental_option("excludeSwitches", ['enable_automation'])
        # options.add_argument("--disable-infobars")
        # options.add_argument("--disable-notification")
        options.add_argument('--disable-blink-features=AutomationControlled')
        # options.add_argument('--disable-blink-features=AutomationControlled')
        # options.add_argument('--disable-gpu')  # 禁用GPU加速
        driver = webdriver.Chrome(options=options, service=driver_service)
    elif webdriver_type == WebDriverType.SafariDriver:
        options = webdriver.SafariOptions()
        driver = webdriver.Safari(options=options)
    assert (driver is not None)
    logger.info(f'{webdriver_type.name} is initialized')
    return driver


def login_taobao():
    logger = get_logger()
    logger.info('navigate to taobao login page')
    Driver.get(TB_LOGIN_PAGE)
    while True:
        try:
            logger.info('check taobao login status and wait in seconds')
            Driver.find_element(By.ID, 'login')
            time.sleep(LOGIN_CHECK_WAIT_IN_SECONDS)
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
                'we are not in taobao/personal homepage, '
                'finish authentication and navigate to taobao/personal homepage to continue crawling...')
            time.sleep(LOGIN_CHECK_WAIT_IN_SECONDS)
    set_window_size()


def zoom_content(ratio=1.0):
    logger = get_logger()
    zoom_script = 'document.body.style.zoom="%f"' % ratio
    logger.info(f'executing script {zoom_script} and wait for seconds')
    Driver.execute_script(zoom_script)
    time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)


def scroll_window(pos=None):
    logger = get_logger()
    x = pos[0] if pos is not None else 'document.body.scrollWidth'
    y = pos[1] if pos is not None else 'document.body.scrollHeight'
    scroll_script = 'window.scrollTo(%s, %s)' % (str(x), str(y))
    logger.info(f'executing script {scroll_script} and wait for seconds')
    Driver.execute_script(scroll_script)
    time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)


def set_window_size(size=None):
    logger = get_logger()
    if size is None:
        logger.info('maximizing window and wait for seconds')
        Driver.maximize_window()
    else:
        logger.info(f'set window size to ({size[0]},{size[1]}) and wait for seconds')
        Driver.set_window_size(size[0], size[1])
    time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)


def scroll_windows_to_element(element):
    logger = get_logger()
    script = 'arguments[0].scrollIntoView();'
    logger.info(f'executing script {script} to element location ({element.location["x"]},{element.location["y"]}) '
                'and wait for seconds')
    Driver.execute_script('arguments[0].scrollIntoView();', element)
    time.sleep(SHOP_PAGE_SKU_LOAD_WAIT_IN_SECONDS)


def create_element_screenshot(element, file_path):
    logger = get_logger()
    logger.info(f'take screenshot for element location ({element.location["x"]},{element.location["y"]}) '
                f'to file {file_path} and wait for seconds')
    element.screenshot(file_path)
    time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)


def parse_product_id_from_item(item_id):
    assert (item_id.rfind('_') != -1)
    product_id = item_id[item_id.rfind('_') + 1:]
    assert (len(product_id) > 0)
    return product_id


def parse_product_id_from_product_link(link):
    result = urlparse(link)
    qs = parse_qs(result.query)
    if 'id' in qs and len(qs['id']) == 1:
        return qs['id'][0]
    else:
        return None


def parse_sku_id_from_product_link(link):
    result = urlparse(link)
    qs = parse_qs(result.query)
    if 'skuId' in qs and len(qs['skuId']) == 1:
        return qs['skuId'][0]
    else:
        return None


def parse_sale_in_search(sale):
    assert (len(sale) > 3)
    desc = sale[-3:]
    if desc != '人付款' and desc != '人收货':
        return -1
    sale_num = sale[:-3]
    if sale_num[-1] == '+':
        sale_num = sale_num[:-1]
    if sale_num[-1] == '万':
        sale_num = sale_num[:-1] + '0000'
    return int(sale_num)


def parse_sale_in_detail(sale):
    idx = sale.rfind('已售')
    if idx == -1:
        return -1
    sale = sale[idx:]
    assert (len(sale) > 2)
    sale_num = sale[2:].strip()
    if sale_num[-1] == '+':
        sale_num = sale_num[:-1]
    if sale_num[-1] == '万':
        sale_num = sale_num[:-1] + '0000'
    return int(sale_num)


def craw_taobao_search_page(qstring, num_of_pages, sale_order, update_id):
    login_taobao()
    crawl_taobao_search_results(qstring, num_of_pages, sale_order, update_id)


def crawl_taobao_search_results(qstring, num_of_pages, sale_order, update_id, target_product_ids=None):
    logger = get_logger()
    logger.info(f'navigate to taobao search page and enter search string: {qstring}')
    Driver.get(TB_SEARCH_PAGE)
    qbox = Driver.find_element(By.ID, 'q')
    qbox.clear()
    qbox.send_keys(qstring)
    qbox.send_keys(Keys.RETURN)
    ids_set = set()
    for page in range(1, num_of_pages + 1):
        try:
            # TBD: 在这里检查是否有滑动验证弹窗，并解决 (<div class='nocaptcha>, XPATH 'div/div/div' .text)
            logger.info('wait search results ready for seconds')
            time.sleep(SEARCH_WAIT_IN_SECONDS)
            # press '销量' navigate bar on first page
            if page == 1 and sale_order:
                sale_order_div = None
                divs = Driver.find_elements(By.CLASS_NAME, 'next-tabs-tab-inner')
                for div in divs:
                    if div.text == '销量':
                        sale_order_div = div
                        break
                assert (sale_order_div is not None)
                sale_order_div.click()
                logger.info('wait search results ready for seconds')
                time.sleep(SEARCH_WAIT_IN_SECONDS)
            search_result_wrapper = Driver.find_element(By.ID, 'content_items_wrapper')
            search_results = search_result_wrapper.find_elements(By.XPATH, 'div/a')
            logger.info(f'find {len(search_results)} search results')
            for search_result in search_results:
                parse_taobao_search_result(search_result, ids_set, update_id, target_product_ids)
            if page < num_of_pages:
                btn_pages = Driver.find_elements(By.CLASS_NAME, 'next-pagination-pages')
                assert (len(btn_pages) >= 1)  # 至少下面会有一个导航栏
                btn_list = btn_pages[-1].find_elements(By.XPATH, 'button')
                assert (len(btn_list) == 3)  # 下面导航栏里直属三个按钮：上一页，下一页，确定
                logger.info(f'get search [{qstring}] results for page {page + 1} by press next page')
                btn_list[1].click()
        except AssertionError:
            logger.error(
                'assertion failed in search result page, just stop crawling, it is ok for single product search')
            traceback.print_exc()
            break
        except Exception:
            logger.error('get unexcepted exception while parsing search results, just stop crawling')
            traceback.print_exc()
            break


def parse_taobao_search_result(search_result, ids_set, update_id, target_product_ids=None):
    logger = get_logger()
    try:
        logger.info(f'parsing search result: {search_result.accessible_name}')
        item_id = search_result.get_attribute('id')
        product_id = parse_product_id_from_item(item_id)
        target_product_ids = target_product_ids or []
        if len(target_product_ids) > 0 and product_id not in target_product_ids:
            logger.info(f'product_id [{product_id}] not in target_product_ids {target_product_ids}, just ignore')
            return
        product_link = search_result.get_attribute('href')
        sku_id = parse_sku_id_from_product_link(product_link) or '0'
        product_items = search_result.find_elements(By.XPATH, 'div/div')
        assert (len(product_items) == 3)
        sku_summary = None
        shop_summary = None
        for item in product_items:
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
        sku_title_inner = sku_title_wrapper.find_element(By.XPATH, 'div/span')
        product_title = sku_title_inner.text
        price_spans = price_wrapper.find_elements(By.XPATH, 'div/span')
        assert (len(price_spans) >= 2)
        price_unit_span = None
        display_sale_span = None
        for span in price_spans:
            cls_name = span.get_attribute('class')
            if cls_name is None:
                continue
            elif re.match(SKU_SEARCH_UNIT_RE_EXP, cls_name):
                price_unit_span = span
            elif re.match(SKU_SEARCH_SALE_RE_EXP, cls_name):
                display_sale_span = span
        assert (price_unit_span is not None and display_sale_span is not None)
        price_unit = parse_price_unit(price_unit_span.text)
        display_sale = parse_sale_in_search(display_sale_span.text)
        price_divs_wrapper = price_wrapper.find_elements(By.XPATH, 'div/div')
        assert (len(price_divs_wrapper) >= 2)
        price_divs_inner = price_divs_wrapper[0].find_elements(By.XPATH, 'div')
        assert (len(price_divs_inner) == 2)
        display_price = '%s%s' % (price_divs_inner[0].text, price_divs_inner[1].text)
        display_price = parse_price(display_price)
        shop_info = shop_summary.find_element(By.XPATH, 'div/a')
        shop_link = shop_info.get_attribute('href')
        shop_link = shop_link if shop_link is not None else ''
        shop_name_wrapper = shop_info.find_elements(By.XPATH, 'div/span')
        shop_name = shop_name_wrapper[-1].text
        if product_id not in ids_set:
            save_taobao_search_result(product_id, sku_id, product_title, product_link,
                                      shop_name, shop_link,
                                      price_unit, display_price, display_sale,
                                      update_id)
        ids_set.add(product_id)
    except AssertionError:
        logger.error(f'assertion failed while parsing {search_result.accessible_name}')
        logger.error('it may be caused by unloaded resources, just ignore it')
        traceback.print_exc()
    except Exception:
        logger.error(f'get unhandled exception while parsing {search_result.accessible_name}')
        traceback.print_exc()


def save_taobao_search_result(product_id, sku_id, product_title, product_link, shop_name, shop_link, price_unit,
                              display_price, display_sale, update_id):
    # save shop info
    update_role = save_taobao_search_result.__name__
    # save shop info
    update_shop_info(shop_name, shop_link, None, update_id, update_role)
    # save product info
    update_product_info(product_id, sku_id, product_title, product_link, shop_name,
                        price_unit, display_price, display_sale,
                        None, None, None, None,
                        update_id, update_role)
    # save product sales info,
    # remember there can be same product in different search pages,
    # we only add one sale record for same product in one search process.
    add_product_sale(product_id, shop_name,
                     price_unit, display_price, display_sale, None,
                     update_id, update_role)


def craw_taobao_detail_page(product_link, product_id, update_id):
    login_taobao()
    craw_taobao_detail_page_result(product_link, product_id, update_id)


def craw_taobao_detail_page_result(product_link, product_id, update_id):
    logger = get_logger()
    logger.info(f'navigate to product [{product_id}] with link: [{product_link}] and wait for seconds')
    Driver.get(product_link)
    time.sleep(DETAIL_PAGE_WAIT_IN_SECONDS)
    # set zoom ratio
    logger.info('set detail page zoom ratio to %f' % TB_PAGE_DEFAULT_ZOOM_RATIO)
    zoom_content(TB_PAGE_DEFAULT_ZOOM_RATIO)
    # parse detail page
    sku_items_divs = []
    sku_price_div = None
    sku_sale_div = None
    title_image_div = None
    page_image_div = None
    shop_info_div = None
    sku_title_div = None
    while True:
        divs = Driver.find_elements(By.XPATH, '//div')
        go_login_div = None
        for div in divs:
            cls_name = div.get_attribute('class')
            if cls_name is None:
                continue
            if re.match(TB_GO_LOGIN_RE_EXP, cls_name):
                go_login_div = div
                break
            elif re.match(SKU_ITEMS_RE_EXP, cls_name):
                sku_items_divs.append(div)
            elif re.match(SKU_PRICE_RE_EXP, cls_name):
                sku_price_div = div
            elif re.match(SKU_SALE_RE_EXP, cls_name):
                sku_sale_div = div
            elif re.match(SKU_TITLE_IMGS_RE_EXP, cls_name):
                title_image_div = div
            elif re.match(SKU_MAIN_IMGS_RE_EXP, cls_name):
                page_image_div = div
            elif re.match(SKU_SHOP_HEADER_RE_EXP, cls_name):
                shop_info_div = div
            elif re.match(SKU_TITLE_RE_EXP, cls_name):
                sku_title_div = div
        if go_login_div is None:
            break
        else:
            logger.info('navigate to login page again because taobao log us off')
            login_taobao()
            logger.info('navigate to product link again and wait for seconds')
            Driver.get(product_link)
            time.sleep(DETAIL_PAGE_WAIT_IN_SECONDS)
    assert (len(sku_items_divs) < MAX_SKU_ITEMS_NUM)
    assert (sku_price_div is not None)
    assert (page_image_div is not None)
    update_sale = sku_sale_div is not None
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
            if re.match(SKU_INNER_ITEMS_RE_EXP, cls_name):
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
    # parse all offers
    offers, price_unit, lowest_price = craw_taobao_sku_prices(value_items_divs, sku_price_div)
    product_details = {
        "sku_items": sku_items,
        "valid_offers": offers
    }
    # parse sku sale
    sale_val = -1
    if update_sale:
        sale_val = parse_sale_in_detail(sku_sale_div.text)
    # parse product title and shop info
    product_title = sku_title_div.find_element(By.XPATH, 'h1').text
    shop_info_inner = shop_info_div.find_element(By.XPATH, 'a')
    assert (shop_info_inner is not None)
    shop_name_span = shop_info_inner.find_element(By.XPATH, 'div/div/span')
    assert (shop_name_span is not None)
    shop_name = shop_name_span.text
    shop_link = shop_info_inner.get_attribute('href')
    # parse title images
    title_imgs = title_image_div.find_elements(By.XPATH, 'ul/li/img')
    title_images = [title_img.get_attribute('src') for title_img in title_imgs]
    logger.info('get title image list: %s' % title_images)
    # parse main images, descV8-richtext or descV8-singleImage
    main_images = []
    main_imgs = page_image_div.find_elements(By.XPATH, './/div')
    for main_img in main_imgs:
        cls_name = main_img.get_attribute('class')
        if cls_name is None:
            continue
        if re.match(SKU_MAIN_IMGS_SINGLE_IMG_RE_EXP, cls_name):
            # we only get pic links and ignore other format
            try:
                data_src = main_img.find_element(By.XPATH, 'img').get_attribute('data-src')
                if data_src is not None:
                    main_images.append(data_src)
                else:
                    main_images.append(main_img.find_element(By.XPATH, 'img').get_attribute('src'))
            except NoSuchElementException:
                logger.info('detail page material is not an image, ignore')
        elif re.match(SKU_MAIN_IMGS_RICHTEXT_RE_EXP, cls_name):
            # we only get pic links and ignore other format
            try:
                for img_element in main_img.find_elements(By.XPATH, 'p/img'):
                    scroll_windows_to_element(img_element)
                img_elements = main_img.find_elements(By.XPATH, 'p/img')
                main_images += [img_element.get_attribute('src') for img_element in img_elements]
            except NoSuchElementException:
                logger.info('detail page material is not an image, ignore')
    logger.info('get main image list: %s' % main_images)
    # update product info in DB
    product_id = product_id or parse_product_id_from_product_link(product_link)
    sku_id = parse_sku_id_from_product_link(product_link) or '0'
    update_role = craw_taobao_detail_page_result.__name__
    if product_id is not None:
        update_product_info(product_id, sku_id, product_title, product_link, shop_name,
                            price_unit, lowest_price, sale_val,
                            title_images, main_images, product_details, None,
                            update_id, update_role)
        if update_sale:
            add_product_sale(product_id, shop_name, price_unit, lowest_price, sale_val, None, update_id, update_role)
        update_shop_info(shop_name, shop_link, None, update_id, update_role)


def craw_taobao_sku_prices(value_items_divs, sku_price_div):
    combos = get_value_item_combos(value_items_divs)
    offers = []
    lowest_price = 6553500
    price_unit = ''
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
        price_unit = parse_price_unit(price_unit_span.text)
        offer.append(price_unit)
        price_val = parse_price(price_val_span.text)
        if price_val < lowest_price:
            lowest_price = price_val
        offer.append(price_val)
        offers.append(offer)
    return offers, price_unit, lowest_price


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
        logger.error(f'get exception while parsing value_item span {value_item.accessible_name}')
        traceback.print_exc()
        return None
    try:
        img = value_item.find_element(By.XPATH, 'img')
        sku_item['img'] = img.get_attribute('src')
    except Exception:
        logger.error('some sku_item do not have img, just ignore')
    return sku_item


def craw_taobao_shop_page(shop_link, update_id, target_product_ids=None):
    login_taobao()
    craw_taobao_shop_page_results(shop_link, update_id, target_product_ids)


def craw_taobao_shop_page_results(shop_link, update_id, target_product_ids=None):
    logger = get_logger()
    logger.info(f'navigate to shop link [{shop_link}] and wait for seconds')
    Driver.get(shop_link)
    time.sleep(SHOP_PAGE_WAIT_IN_SECONDS)
    while True:
        divs = Driver.find_elements(By.XPATH, '//div')
        load_more_flag_div = None
        loaded = False
        for div in divs:
            cls_name = div.get_attribute('class')
            if cls_name is None:
                continue
            if re.match(SHOP_LOAD_STATUS_RE_EXP, cls_name):
                if div.text == '没有更多商品':
                    loaded = True
                    break
            elif re.match(SHOP_LOAD_MORE_FLAG_RE_EXP, cls_name):
                load_more_flag_div = div
        if loaded:
            scroll_window((0, 0))
            break
        # 有些特殊店铺没有 load_more_flag_div, 这种店铺是完全定制的页面（非淘宝模板）
        # 我们暂时不支持这种店铺。参考：https://shop61333799.taobao.com/
        # 这种店铺的商品仍然可以通过search或detail页面抓取来收录
        assert (load_more_flag_div is not None)
        scroll_windows_to_element(load_more_flag_div)
    shop_sku_divs = []
    shop_name_div = None
    divs = Driver.find_elements(By.XPATH, '//div')
    for div in divs:
        cls_name = div.get_attribute('class')
        if cls_name is None:
            continue
        if re.match(SHOP_SKU_CARD_RE_EXP, cls_name):
            shop_sku_divs.append(div)
        elif re.match(SHOP_NAME_RE_EXP, cls_name):
            shop_name_div = div
    assert (shop_name_div is not None)
    shop_name = shop_name_div.find_element(By.XPATH, 'span').text
    update_shop_info(shop_name, shop_link, None, update_id, craw_taobao_shop_page_results.__name__)
    for shop_sku_div in shop_sku_divs:
        try:
            craw_taobao_shop_sku_result(shop_sku_div, shop_name, update_id, target_product_ids)
        except PriceOCRError:
            logger.error('get PriceOCRGetEmptyError, nothing will be updated and just continue crawling')
            traceback.print_exc()
            continue


def craw_taobao_shop_sku_result(shop_sku_div, shop_name, update_id, target_product_ids=None):
    logger = get_logger()
    sku_link_a = shop_sku_div.find_element(By.XPATH, 'a')
    assert (sku_link_a is not None)
    product_link = sku_link_a.get_attribute('href')
    product_id = parse_product_id_from_product_link(product_link)
    target_product_ids = target_product_ids or []
    if len(target_product_ids) > 0 and product_id not in target_product_ids:
        logger.info(f'parsed product_id [{product_id}] not in target_product_ids, ignore this product')
        return
    sku_id = parse_sku_id_from_product_link(product_link) or ''
    divs = shop_sku_div.find_elements(By.XPATH, './/div')
    title_div = None
    price_div = None
    sale_div = None
    for div in divs:
        cls_name = div.get_attribute('class')
        if cls_name is None:
            continue
        if re.match(SHOP_SKU_CARD_TITLE_RE_EXP, cls_name):
            title_div = div
        elif re.match(SHOP_SKU_CARD_PRICE_RE_EXP, cls_name):
            price_div = div
        elif re.match(SHOP_SKU_CARD_SALE_RE_EXP, cls_name):
            sale_div = div
    assert (title_div is not None and price_div is not None and sale_div is not None)
    product_title = title_div.text
    price_spans = price_div.find_elements(By.XPATH, 'span')
    assert (len(price_spans) == 2)
    price_unit = parse_price_unit(price_spans[0].text)
    price_val = parse_price_span(price_spans[1], product_id)
    product_sale = parse_sale_in_search(sale_div.text)
    # update product_info and product_sales table
    update_role = craw_taobao_shop_sku_result.__name__
    update_product_info(product_id, sku_id, product_title, product_link, shop_name,
                        price_unit, price_val, product_sale,
                        None, None, None, None,
                        update_id, update_role)
    add_product_sale(product_id, shop_name, price_unit, price_val, product_sale, None, update_id, update_role)


def crawl_shop_link_by_search(shop_name, update_id):
    login_taobao()
    crawl_shop_link_by_search_results(shop_name, update_id)


def crawl_shop_link_by_search_results(shop_name, update_id):
    logger = get_logger()
    logger.info('navigate to taobao shop search page')
    Driver.get(TB_SEARCH_PAGE)
    shop_tab_div = None
    divs = Driver.find_elements(By.XPATH, '//div')
    for div in divs:
        title = div.text.strip()
        if title == '店铺':
            shop_tab_div = div
            break
    assert (shop_tab_div is not None)
    shop_tab_div.click()
    qbox = Driver.find_element(By.ID, 'q')
    qbox.clear()
    qbox.send_keys(shop_name)
    qbox.send_keys(Keys.RETURN)
    logger.info(f'wait for shop [{shop_name}] search result for seconds')
    time.sleep(SEARCH_WAIT_IN_SECONDS)
    shop_wrapper_div = Driver.find_element(By.ID, 'srp_shopLayout_shopContentWrapper')
    assert (shop_wrapper_div is not None)
    shop_link = None
    for shop_a in shop_wrapper_div.find_elements(By.XPATH, 'a'):
        title_div = None
        shop_divs = shop_a.find_elements(By.XPATH, './/div')
        for shop_div in shop_divs:
            cls_name = shop_div.get_attribute('class')
            if cls_name is None:
                continue
            if re.match(SHOP_TITLE_RE_EXP, cls_name):
                title_div = shop_div
                break
        assert (title_div is not None)
        name = title_div.text.strip()
        if name == shop_name:
            shop_link = shop_a.get_attribute('href')
            break
    if shop_link is not None:
        logger.info(f'update shop [{shop_name}] link to {shop_link}')
        update_shop_info(shop_name, shop_link, None, update_id, crawl_shop_link_by_search_results.__name__)


def parse_price_span(price_span, product_id):
    temp_file_name = f'{IMAGE_DIR}/{product_id}-{uuid.uuid4().hex}.png'
    create_element_screenshot(price_span, temp_file_name)
    return par_price_ocr(temp_file_name)


Driver = init_webdriver(WebDriverType.ChromDriver)
