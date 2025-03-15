# coding: utf-8
# !./bin/python

import os
import traceback
import uuid
from enum import Enum
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeDriverService
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from taobao.config import *
from taobao.exceptions import *
from taobao.utils import *
from taobao.models import *

TB_LOGIN_PAGE = 'https://login.taobao.com/member/login.jhtml'
TB_SEARCH_PAGE = 'https://s.taobao.com/search'
TB_HOMEPAGE_TITLE_NAME = '淘宝'
TB_PERSONAL_HOMEPAGE_TITLE_NAME = '我的淘宝'
TB_LOGIN_AUTH_TITLE_NAME = '登录-身份验证'
LOGIN_CHECK_WAIT_IN_SECONDS = 5
LOGIN_CONFIRM_WAIT_IN_SECONDS = 15
SEARCH_WAIT_IN_SECONDS = 5
DETAIL_PAGE_WAIT_IN_SECONDS = 5
SHOP_PAGE_WAIT_IN_SECONDS = 5
DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS = 1
TB_PAGE_DEFAULT_ZOOM_RATIO = 0.5

# search page related controls
SEARCH_MAIN_PIC_AND_DESC_RE_EXP = re.compile('^mainPicAndDesc--\\w+')
SEARCH_SHOP_INFO_RE_EXP = re.compile('^shopInfo--\\w+')
SEARCH_DESC_WRAPPER_RE_EXP = re.compile('^[\s\S]*descWrapper--\\w+')
SEARCH_PRICE_WRAPPER_RE_EXP = re.compile('^priceWrapper--\\w+')
SEARCH_SKU_UNIT_RE_EXP = re.compile('^unit--\\w+')

# shop page related controls
SHOP_SKU_CARD_RE_EXP = re.compile('^cardContainer--\\w+')
SHOP_NAME_RE_EXP = re.compile('^shopName--\\w+')
SHOP_LOAD_STATUS_RE_EXP = re.compile('^loadStatus--\\w+')
SHOP_LOAD_MORE_FLAG_RE_EXP = re.compile('^loadmoreFlag--\\w+')
SHOP_SKU_CARD_TITLE_RE_EXP = re.compile('^title--\\w+')
SHOP_SKU_CARD_PRICE_RE_EXP = re.compile('^price--\\w+')
SHOP_SKU_CARD_SALE_RE_EXP = re.compile('^count--\\w+')
SEARCH_SKU_SALE_RE_EXP = re.compile('^realSales--\\w+')

# shop search related controls
SHOP_SEARCH_TITLE_RE_EXP = re.compile('^title--\\w+')

# product detail related controls
DETAIL_OFFER_ITEMS_RE_EXP = re.compile('^skuItem--\\w+')
DETAIL_PRICE_RE_EXP = re.compile('^highlightPrice--\\w+')
DETAIL_SALE_RE_EXP = re.compile('^salesDesc--\\w+')
DETAIL_TITLE_IMGS_RE_EXP = re.compile('^thumbnailsWrap--\\w+')
DETAIL_MAIN_IMGS_V8_RE_EXP = re.compile('^descV8-container$')
DETAIL_MAIN_IMGS_V6_RE_EXP = re.compile('^descV6-container$')
DETAIL_SHOP_INFO_RE_EXP = re.compile('^shopHeader--\\w+')
DETAIL_PRODUCT_TITLE_RE_EXP = re.compile('^ItemTitle--\\w+')
DETAIL_OFFER_INNER_ITEMS_RE_EXP = re.compile('^content--\\w+')
DETAIL_PRICE_UNIT_RE_EXP = re.compile('^symbol--\\w+')
DETAIL_PRICE_VAL_RE_EXP = re.compile('^text--\\w+')
DETAIL_MAIN_IMGS_SINGLE_IMG_V8_RE_EXP = re.compile('^descV8-singleImage$')
DETAIL_MAIN_IMGS_RICHTEXT_V8_RE_EXP = re.compile('^descV8-richtext$')
DETAIL_IMG_LINK_VALIDATE_RE_EXP = re.compile('^https://\\w+')


class WebDriverType(Enum):
    ChromDriver = 1
    SafariDriver = 2


def init_webdriver(webdriver_type: WebDriverType):
    logger = get_logger()
    if DEBUG:
        os.chdir(DEBUG_ROOT_DIR)
    driver = None
    if webdriver_type == WebDriverType.ChromDriver:
        # TBD: handle hiding selenium from chrome, remove 'chrome is controlled by automated test software'
        driver_service = ChromeDriverService('./chromedriver')
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['load-extension', 'enable-automation'])
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=options, service=driver_service)
    elif webdriver_type == WebDriverType.SafariDriver:
        options = webdriver.SafariOptions()
        driver = webdriver.Safari(options=options)
    assert (driver is not None)
    logger.info(f'{webdriver_type.name} is initialized')
    return driver


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


def scroll_window_to_element(element):
    logger = get_logger()
    script = 'arguments[0].scrollIntoView();'
    logger.info(f'executing script {script} to element location ({element.location["x"]},{element.location["y"]}) '
                'and wait for seconds')
    Driver.execute_script('arguments[0].scrollIntoView();', element)
    time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)


def element_screenshot(element, file_path):
    logger = get_logger()
    logger.info(f'take screenshot for element location ({element.location["x"]},{element.location["y"]}) '
                f'to file {file_path} and wait for seconds')
    element.screenshot(file_path)
    time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)


def element_click(element):
    logger = get_logger()
    logger.info(f'element={element.accessible_name} clicked and wait for seconds')
    element.click()
    time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)


def parse_product_id_from_item(item_id):
    assert (item_id is not None and item_id.rfind('_') != -1)
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
    logger = get_logger()
    assert (len(sale) > 3)
    desc = sale[-3:]
    if desc != '人付款' and desc != '人收货':
        logger.info(f'parse_sale_in_search get unexpected description, sale={sale}, desc={desc}, just return -1')
        return -1
    sale_num = sale[:-3]
    if sale_num[-1] == '+':
        sale_num = sale_num[:-1]
    if sale_num[-1] == '万':
        sale_num = sale_num[:-1] + '0000'
    return int(sale_num)


def parse_sale_in_detail(sale):
    logger = get_logger()
    idx = sale.rfind('已售')
    if idx == -1:
        logger.info(f'parse_sale_in_detail get unexpected sale={sale}, return -1')
        return -1
    sale = sale[idx:]
    assert (len(sale) > 2)
    sale_num = sale[2:].strip()
    if sale_num[-1] == '+':
        sale_num = sale_num[:-1]
    if sale_num[-1] == '万':
        sale_num = sale_num[:-1] + '0000'
    return int(sale_num)


def is_valid_image_link(link):
    if link[link.rfind('/') + 1:] == 's.gif':
        return False
    elif re.match(DETAIL_IMG_LINK_VALIDATE_RE_EXP, link):
        return True


def handle_taobao_login_page():
    logger = get_logger()
    logger.info('navigate to taobao login page and wait in seconds')
    Driver.get(TB_LOGIN_PAGE)
    time.sleep(LOGIN_CHECK_WAIT_IN_SECONDS)
    while True:
        try:
            user_input = Driver.find_element(By.ID, 'fm-login-id')
            passwd_input = Driver.find_element(By.ID, 'fm-login-password')
            login_button = Driver.find_element(By.CLASS_NAME, 'fm-btn').find_element(By.XPATH, 'button')
            assert (user_input is not None and passwd_input is not None and login_button is not None)
            user_input.clear()
            user_input.send_keys(TB_USERNAME)
            passwd_input.clear()
            passwd_input.send_keys(TB_PASSWORD)
            element_click(login_button)
            time.sleep(LOGIN_CONFIRM_WAIT_IN_SECONDS)
            break
        except NoSuchElementException:
            logger.info('can not find login form, wait for seconds an retry')
            time.sleep(LOGIN_CHECK_WAIT_IN_SECONDS)


def handle_taobao_post_login_page():
    logger = get_logger()
    logger.info('check if we are in taobao/personal homepage')
    while True:
        if Driver.title == TB_PERSONAL_HOMEPAGE_TITLE_NAME or Driver.title == TB_HOMEPAGE_TITLE_NAME:
            logger.info('we are already in taobao/personal homepage, now perform following crawling')
            break
        elif Driver.title == TB_LOGIN_AUTH_TITLE_NAME:
            logger.info('we are in login verification page, use SMS to get auth code')
            iframe = Driver.find_element(By.XPATH, '//*[@id="content"]/div/div[1]/iframe')
            Driver.switch_to.frame(iframe)
            code_input = Driver.find_element(By.ID, 'J_Phone_Checkcode')
            sms_btn = Driver.find_element(By.ID, 'J_GetCode')
            confirm_btn = Driver.find_element(By.ID, 'submitBtn')
            sms_btn.click()
            sms_code = input(f'Please input SMS verification code for user={TB_USERNAME}: ')
            code_input.send_keys(sms_code)
            confirm_btn.click()
            time.sleep(LOGIN_CHECK_WAIT_IN_SECONDS)
            break
        else:
            logger.info(
                'we are not in taobao/personal homepage, '
                'finish authentication and navigate to taobao/personal homepage to continue crawling...')
            time.sleep(LOGIN_CHECK_WAIT_IN_SECONDS)


def login_taobao():
    logger = get_logger()
    handle_taobao_login_page()
    handle_taobao_post_login_page()
    set_window_size()


def crawl_taobao_search_results(search_key, num_of_pages, sale_order, update_id, target_product_ids=None):
    logger = get_logger()
    logger.info(
        f'navigate to taobao search page with search_key={search_key} and num_of_pages={num_of_pages}, sale_order={sale_order}')
    Driver.get(TB_SEARCH_PAGE)
    qbox = Driver.find_element(By.ID, 'q')
    qbox.clear()
    qbox.send_keys(search_key)
    qbox.send_keys(Keys.RETURN)
    ids_set = set()
    for page in range(1, num_of_pages + 1):
        try:
            logger.info('wait search results ready for seconds')
            time.sleep(SEARCH_WAIT_IN_SECONDS)
            # press '销量' navigate bar on first page if sale_order is True
            if page == 1 and sale_order:
                sale_order_div = None
                divs = Driver.find_elements(By.CLASS_NAME, 'next-tabs-tab-inner')
                for div in divs:
                    if div.text == '销量':
                        sale_order_div = div
                        break
                assert (sale_order_div is not None)
                element_click(sale_order_div)
                logger.info('wait search results ready by press order first for seconds')
                time.sleep(SEARCH_WAIT_IN_SECONDS)
            search_result_wrapper = Driver.find_element(By.ID, 'content_items_wrapper')
            search_results = search_result_wrapper.find_elements(By.XPATH, 'div/a')
            logger.info(f'find {len(search_results)} search results with search_key={search_key} and page= {page}')
            for search_result in search_results:
                parse_taobao_search_result(search_result, ids_set, update_id, target_product_ids)
            if page < num_of_pages:
                btn_pages = Driver.find_elements(By.CLASS_NAME, 'next-pagination-pages')
                assert (len(btn_pages) >= 1)  # 至少下面会有一个导航栏
                btn_list = btn_pages[-1].find_elements(By.XPATH, 'button')
                assert (len(btn_list) == 3)  # 下面导航栏里直属三个按钮：上一页，下一页，确定
                logger.info(
                    f'get next page search results for search_key={search_key} and page={page + 1} by press next page')
                element_click(btn_list[1])
        except AssertionError:
            logger.error(
                'assertion failed in search result page, just stop crawling')
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
        product_id = parse_product_id_from_item(search_result.get_attribute('id'))
        target_product_ids = target_product_ids or []  # None表示不限制target product id
        if len(target_product_ids) > 0 and product_id not in target_product_ids:
            logger.info(
                f'product_id={product_id} not in target_product_ids={target_product_ids}, just ignore and return')
            return
        product_link = search_result.get_attribute('href')
        sku_id = parse_sku_id_from_product_link(product_link) or '0'
        product_items = search_result.find_elements(By.XPATH, 'div/div')
        sku_summary, shop_summary = None, None
        for item in product_items:
            cls_name = item.get_attribute('class')
            if cls_name is None:
                continue
            if re.match(SEARCH_MAIN_PIC_AND_DESC_RE_EXP, cls_name):
                sku_summary = item
            if re.match(SEARCH_SHOP_INFO_RE_EXP, cls_name):
                shop_summary = item
        assert (sku_summary is not None and shop_summary is not None)
        sku_items = sku_summary.find_elements(By.XPATH, 'div')
        sku_title_wrapper, price_wrapper = None, None
        for item in sku_items:
            cls_name = item.get_attribute('class')
            if cls_name is None:
                continue
            if re.match(SEARCH_DESC_WRAPPER_RE_EXP, cls_name):
                sku_title_wrapper = item
            if re.match(SEARCH_PRICE_WRAPPER_RE_EXP, cls_name):
                price_wrapper = item
        assert (sku_title_wrapper is not None and price_wrapper is not None)
        product_title = sku_title_wrapper.find_element(By.XPATH, 'div/span').text
        price_unit_span, display_sale_span = None, None
        for span in price_wrapper.find_elements(By.XPATH, 'div/span'):
            cls_name = span.get_attribute('class')
            if cls_name is None:
                continue
            elif re.match(SEARCH_SKU_UNIT_RE_EXP, cls_name):
                price_unit_span = span
            elif re.match(SEARCH_SKU_SALE_RE_EXP, cls_name):
                display_sale_span = span
        assert (price_unit_span is not None and display_sale_span is not None)
        price_unit = parse_price_unit(price_unit_span.text)
        display_sale = parse_sale_in_search(display_sale_span.text)
        price_divs = price_wrapper.find_elements(By.XPATH, 'div/div/div')
        assert (len(price_divs) == 2)
        display_price = parse_price('%s%s' % (price_divs[0].text, price_divs[1].text))
        shop_link = shop_summary.find_element(By.XPATH, 'div/a').get_attribute('href') or ''
        shop_name = shop_summary.find_elements(By.XPATH, 'div/a/div/span')[-1].text
        if product_id not in ids_set:
            save_taobao_search_result(product_id, sku_id, product_title, product_link,
                                      shop_name, shop_link,
                                      price_unit, display_price, display_sale,
                                      update_id)
        ids_set.add(product_id)
    except AssertionError:
        logger.error(f'assertion failed while parsing {search_result.accessible_name}, just ignore')
        traceback.print_exc()
        return
    except Exception:
        logger.error(f'get unhandled exception while parsing {search_result.accessible_name}, just ignore')
        traceback.print_exc()
        return


def save_taobao_search_result(product_id, sku_id, product_title, product_link, shop_name, shop_link, price_unit,
                              display_price, display_sale, update_id):
    logger = get_logger()
    logger.info(f'save_taobao_search_result parsed record:\n'
                f'\t\tproduct_id={product_id}\n'
                f'\t\tsku_id={sku_id}\n'
                f'\t\tproduct_title={product_title}\n'
                f'\t\tproduct_link={product_link}\n'
                f'\t\tshop_name={shop_name}\n'
                f'\t\tshop_link={shop_link}\n'
                f'\t\tprice_unit={price_unit}\n'
                f'\t\tdisplay_price={display_price}\n'
                f'\t\tdisplay_sale={display_sale}\n'
                f'\t\tupdate_id={update_id}\n')
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


def craw_taobao_shop_page(shop_link, update_id, target_product_ids=None):
    logger = get_logger()
    load_shop_and_products(shop_link)
    divs = Driver.find_elements(By.XPATH, '//div')
    shop_name = None
    sku_divs = []
    for div in divs:
        cls_name = div.get_attribute('class')
        if cls_name is None:
            continue
        if re.match(SHOP_SKU_CARD_RE_EXP, cls_name):
            sku_divs.append(div)
        elif re.match(SHOP_NAME_RE_EXP, cls_name):
            shop_name = div.find_element(By.XPATH, 'span').text
    assert (shop_name is not None)
    update_shop_info(shop_name, shop_link, None, update_id, craw_taobao_shop_page.__name__)
    for sku_div in sku_divs:
        try:
            craw_taobao_shop_sku(sku_div, shop_name, update_id, target_product_ids)
        except PriceOCRError as e:
            logger.error(f'get PriceOCRGetEmptyError={e}, nothing will be updated and just continue')
            traceback.print_exc()
            continue


def load_shop_and_products(shop_link):
    logger = get_logger()
    logger.info(f'navigate to shop_link={shop_link} and wait for seconds')
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
        # 有些特殊店铺没有 load_more_flag_div, 会触发此处断言。这种店铺是完全定制的页面（非淘宝模板）
        # 我们暂时不支持这种店铺，未来可能将对重点其他模板进行支持。
        # 这种店铺的商品仍然可以通过search或detail页面抓取来收录
        if load_more_flag_div is None:
            msg = f'shop is not taobao standard shop page, shop_link={shop_link}'
            logger.error(msg)
            raise NotStandardShop(msg)
        scroll_window_to_element(load_more_flag_div)


def craw_taobao_shop_sku(shop_sku_div, shop_name, update_id, target_product_ids=None):
    logger = get_logger()
    product_link = shop_sku_div.find_element(By.XPATH, 'a').get_attribute('href')
    product_id = parse_product_id_from_product_link(product_link)
    target_product_ids = target_product_ids or []
    if len(target_product_ids) > 0 and product_id not in target_product_ids:
        logger.info(f'parsed product_id={product_id} not in target_product_ids, ignore this product')
        return
    sku_id = parse_sku_id_from_product_link(product_link) or ''
    divs = shop_sku_div.find_elements(By.XPATH, './/div')
    title_div, price_div, sale_div = None, None, None
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
    display_price = parse_price_span(price_spans[1], product_id)
    product_sale = parse_sale_in_search(sale_div.text)
    # update product_info and product_sales table
    save_taobao_shop_sku_result(product_id, sku_id, product_title, product_link, shop_name,
                                price_unit, display_price, product_sale, update_id)


def save_taobao_shop_sku_result(product_id, sku_id, product_title, product_link, shop_name,
                                price_unit, display_price, display_sale, update_id):
    logger = get_logger()
    logger.info(f'save_taobao_shop_sku_result parsed record:\n'
                f'\t\tproduct_id={product_id}\n'
                f'\t\tsku_id={sku_id}\n'
                f'\t\tproduct_title={product_title}\n'
                f'\t\tproduct_link={product_link}\n'
                f'\t\tshop_name={shop_name}\n'
                f'\t\tprice_unit={price_unit}\n'
                f'\t\tdisplay_price={display_price}\n'
                f'\t\tdisplay_sale={display_sale}\n'
                f'\t\tupdate_id={update_id}\n')
    update_role = save_taobao_shop_sku_result.__name__
    update_product_info(product_id, sku_id, product_title, product_link, shop_name,
                        price_unit, display_price, display_sale,
                        None, None, None, None,
                        update_id, update_role)
    add_product_sale(product_id, shop_name, price_unit, display_price, display_sale, None, update_id, update_role)


def crawl_taobao_shop_link_by_search(shop_name, update_id):
    logger = get_logger()
    logger.info('navigate to taobao shop search page')
    Driver.get(TB_SEARCH_PAGE)
    divs = Driver.find_elements(By.XPATH, '//div')
    shop_tab_div = None
    for div in divs:
        title = div.text.strip()
        if title == '店铺':
            shop_tab_div = div
            break
    assert (shop_tab_div is not None)
    element_click(shop_tab_div)
    qbox = Driver.find_element(By.ID, 'q')
    qbox.clear()
    qbox.send_keys(shop_name)
    qbox.send_keys(Keys.RETURN)
    logger.info(f'search shop_name={shop_name} and wait for seconds')
    time.sleep(SEARCH_WAIT_IN_SECONDS)
    shop_wrapper_div = Driver.find_element(By.ID, 'srp_shopLayout_shopContentWrapper')
    assert (shop_wrapper_div is not None)
    shop_link = None
    for shop_a in shop_wrapper_div.find_elements(By.XPATH, 'a'):
        shop_divs = shop_a.find_elements(By.XPATH, './/div')
        for shop_div in shop_divs:
            cls_name = shop_div.get_attribute('class')
            if cls_name is None:
                continue
            if re.match(SHOP_SEARCH_TITLE_RE_EXP, cls_name) and shop_name == shop_div.text.strip():
                shop_link = shop_a.get_attribute('href')
                break
    if shop_link is not None:
        logger.info(f'update shop_name={shop_name} and shop_link={shop_link}')
        update_shop_info(shop_name, shop_link, None, update_id,
                         crawl_taobao_shop_link_by_search.__name__)


def parse_price_span(price_span, product_id):
    temp_file_name = f'{IMAGE_DIR}/{product_id}-{uuid.uuid4().hex}.png'
    element_screenshot(price_span, temp_file_name)
    return par_price_ocr(temp_file_name)


def craw_taobao_detail_page(product_id, product_link, update_id):
    logger = get_logger()
    logger.info(f'navigate to product_id={product_id} with product_link={product_link} and wait for seconds')
    Driver.get(product_link)
    time.sleep(DETAIL_PAGE_WAIT_IN_SECONDS)
    # set zoom ratio
    zoom_content(TB_PAGE_DEFAULT_ZOOM_RATIO)
    # parse detail page
    title_div, price_div, shop_info_div = None, None, None
    display_sale_div = None
    title_image_div = None
    page_image_v6_div, page_image_v8_div = None, None
    offer_items_divs_wrapper = []
    divs = Driver.find_elements(By.XPATH, '//div')
    for div in divs:
        cls_name = div.get_attribute('class')
        if cls_name is None:
            continue
        elif re.match(DETAIL_OFFER_ITEMS_RE_EXP, cls_name):
            offer_items_divs_wrapper.append(div)
        elif re.match(DETAIL_PRICE_RE_EXP, cls_name):
            price_div = div
        elif re.match(DETAIL_SALE_RE_EXP, cls_name):
            display_sale_div = div
        elif re.match(DETAIL_TITLE_IMGS_RE_EXP, cls_name):
            title_image_div = div
        elif re.match(DETAIL_MAIN_IMGS_V8_RE_EXP, cls_name):
            page_image_v8_div = div
        elif re.match(DETAIL_MAIN_IMGS_V6_RE_EXP, cls_name):
            page_image_v6_div = div
        elif re.match(DETAIL_SHOP_INFO_RE_EXP, cls_name):
            shop_info_div = div
        elif re.match(DETAIL_PRODUCT_TITLE_RE_EXP, cls_name):
            title_div = div
    assert (title_div is not None and price_div is not None and shop_info_div is not None)
    assert (title_image_div is not None)
    assert (page_image_v8_div is not None or page_image_v6_div is not None)
    # parse product title and shop info
    sku_id = parse_sku_id_from_product_link(product_link) or '0'
    product_title = title_div.find_element(By.XPATH, 'h1').text
    shop_info_inner = shop_info_div.find_element(By.XPATH, 'a')
    shop_name = shop_info_inner.find_element(By.XPATH, 'div/div/span').text
    shop_link = shop_info_inner.get_attribute('href')
    # parse product sale
    display_sale = parse_sale_in_detail(display_sale_div.text) if display_sale_div is not None else -1
    # parse product offer items
    offer_details, price_unit, lowest_price = craw_taobao_detail_offer_details(offer_items_divs_wrapper, price_div)
    # parse title images
    title_images = crawl_taobao_detail_title_images(title_image_div)
    # parse main images
    main_images = crawl_taobao_detail_main_images(page_image_v8_div, page_image_v6_div)
    # update product info in DB
    save_taobao_detail_result(product_id, sku_id, product_title, product_link,
                              shop_name, shop_link,
                              price_unit, lowest_price, display_sale,
                              title_images, main_images, offer_details,
                              update_id)


def craw_taobao_detail_offer_details(offer_items_divs_wrapper, price_div):
    logger = get_logger()
    offer_items_divs = []
    offer_items = []
    for offer_items_div in offer_items_divs_wrapper:
        content_div = None
        inner_divs = offer_items_div.find_elements(By.XPATH, 'div')
        for inner_div in inner_divs:
            cls_name = inner_div.get_attribute('class')
            if cls_name is None:
                continue
            if re.match(DETAIL_OFFER_INNER_ITEMS_RE_EXP, cls_name):
                content_div = inner_div
                break
        assert (content_div is not None)
        offer_item_divs_inner = content_div.find_elements(By.XPATH, 'div')
        offer_items_divs.append(offer_item_divs_inner)
        offer_items.append([craw_taobao_detail_offer_items(v) for v in offer_item_divs_inner])
    logger.info(f'get offer items: {offer_items}')
    # parse all offers
    offers, price_unit, lowest_price = craw_taobao_detail_offers(offer_items_divs, price_div)
    offer_details = {
        "offer_items": offer_items,
        "valid_offers": offers
    }
    logger.info(f'get offer details: {offer_details}')
    return offer_details, price_unit, lowest_price


def crawl_taobao_detail_title_images(title_image_div):
    logger = get_logger()
    title_imgs = title_image_div.find_elements(By.XPATH, 'ul/li/img')
    title_images = [title_img.get_attribute('src') for title_img in title_imgs]
    logger.info(f'get title image list: {title_images}')
    return title_images


def crawl_taobao_detail_main_images(page_image_v8_div, page_image_v6_div):
    main_images = []
    if page_image_v8_div is not None:
        main_images = crawl_taobao_detail_main_images_v8(page_image_v8_div)
    elif page_image_v6_div is not None:
        main_images = crawl_taobao_detail_main_images_v6(page_image_v6_div)
    return main_images


def crawl_taobao_detail_main_images_v8(page_image_v8_div):
    logger = get_logger()
    main_images = []
    main_imgs = page_image_v8_div.find_elements(By.XPATH, './/div')
    for main_img in main_imgs:
        cls_name = main_img.get_attribute('class')
        if cls_name is None:
            continue
        if re.match(DETAIL_MAIN_IMGS_SINGLE_IMG_V8_RE_EXP, cls_name):
            # we only get pic links and ignore other format
            try:
                data_src = main_img.find_element(By.XPATH, 'img').get_attribute('data-src')
                if data_src is not None and is_valid_image_link(data_src):
                    main_images.append(data_src)
                else:
                    src = main_img.find_element(By.XPATH, 'img').get_attribute('src')
                    if is_valid_image_link(src):
                        main_images.append(src)
            except NoSuchElementException:
                logger.info('detail page material is not an image, ignore')
        elif re.match(DETAIL_MAIN_IMGS_RICHTEXT_V8_RE_EXP, cls_name):
            # we only get pic links and ignore other format
            try:
                for img_element in main_img.find_elements(By.XPATH, 'p/img'):
                    scroll_window_to_element(img_element)  # the resource is lazy loaded
                img_elements = main_img.find_elements(By.XPATH, 'p/img')
                for img_element in img_elements:
                    src = img_element.get_attribute('src')
                    if is_valid_image_link(src):
                        main_images.append(src)
            except NoSuchElementException:
                logger.info('detail page material is not an image, ignore')
    logger.info(f'get main image list: {main_images}')
    return main_images


def crawl_taobao_detail_main_images_v6(page_image_v6_div):
    logger = get_logger()
    main_images = []
    for img_element in page_image_v6_div.find_elements(By.XPATH, 'div/div/img'):
        scroll_window_to_element(img_element)  # the resource is lazy loaded
    for img_element in page_image_v6_div.find_elements(By.XPATH, 'div/div/img'):
        src = img_element.get_attribute('src')
        if is_valid_image_link(src):
            main_images.append(src)
    logger.info(f'get main image list: {main_images}')
    return main_images


def craw_taobao_detail_offers(value_items_divs, sku_price_div):
    logger = get_logger()
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
            try:
                element_click(value_item)
            except ElementClickInterceptedException:
                scroll_window_to_element(value_item)
                element_click(value_item)
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
            elif re.match(DETAIL_PRICE_UNIT_RE_EXP, cls_name):
                price_unit_span = price_span
            elif re.match(DETAIL_PRICE_VAL_RE_EXP, cls_name):
                price_val_span = price_span
        assert (price_unit_span is not None and price_val_span is not None)
        price_unit = parse_price_unit(price_unit_span.text)
        offer.append(price_unit)
        price_val = parse_price(price_val_span.text)
        if price_val < lowest_price:
            lowest_price = price_val
        offer.append(price_val)
        offers.append(offer)
    logger.info(f'get offers={offers}, price_unit={price_unit}, lowest_price={lowest_price}')
    return offers, price_unit, lowest_price


def get_value_item_combos(value_items_divs):
    combos, combo = [], []
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


def craw_taobao_detail_offer_items(offer_item_div):
    logger = get_logger()
    offer_item = {}
    try:
        span = offer_item_div.find_element(By.XPATH, 'span')
        offer_item['name'] = span.text
    except Exception:
        logger.error(f'get exception while parsing offer_item span {offer_item_div.accessible_name}')
        traceback.print_exc()
        return None
    try:
        img = offer_item_div.find_element(By.XPATH, 'img')
        offer_item['img'] = img.get_attribute('src')
    except Exception:
        logger.error('some sku_item do not have img, just ignore')
    return offer_item


def save_taobao_detail_result(product_id, sku_id, product_title, product_link,
                              shop_name, shop_link,
                              price_unit, display_price, display_sale,
                              title_images, main_images, offer_details,
                              update_id):
    logger = get_logger()
    logger.info(f'save_taobao_detail_result parsed record:\n'
                f'\t\tproduct_id={product_id}\n'
                f'\t\tsku_id={sku_id}\n'
                f'\t\tproduct_title={product_title}\n'
                f'\t\tproduct_link={product_link}\n'
                f'\t\tshop_name={shop_name}\n'
                f'\t\tshop_link={shop_link}\n'
                f'\t\tprice_unit={price_unit}\n'
                f'\t\tdisplay_price={display_price}\n'
                f'\t\tdisplay_sale={display_sale}\n'
                f'\t\ttitle_images={title_images}\n'
                f'\t\tmain_images={main_images}\n'
                f'\t\toffer_details={offer_details}\n'
                f'\t\tupdate_id={update_id}\n')
    update_role = save_taobao_detail_result.__name__
    update_product_info(product_id, sku_id, product_title, product_link, shop_name,
                        price_unit, display_price, display_sale,
                        title_images, main_images, offer_details, None,
                        update_id, update_role)
    add_product_sale(product_id, shop_name, price_unit, display_price, display_sale, None,
                     update_id, update_role)
    update_shop_info(shop_name, shop_link, None, update_id, update_role)


Driver = init_webdriver(WebDriverType.ChromDriver)
