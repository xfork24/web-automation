# coding: utf-8
# !./bin/python

import os
import shutil
import time
from pathlib import Path
import traceback
import uuid
from enum import Enum
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeDriverService
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from core.config import *
from core.exceptions import *
from core.models import *

TB_LOGIN_PAGE = 'https://login.taobao.com/member/login.jhtml'
TB_SEARCH_PAGE = 'https://s.taobao.com/search'
TB_ONSHELF_PAGE = 'https://item.upload.taobao.com/sell/v2/publish.htm?catId=201160807'
TB_IMAGE_SPACE_PAGE = 'https://qn.taobao.com/home.htm/sucai-tu/home'
REDNOTE_LOGIN_PAGE = 'https://customer.xiaohongshu.com/login?service=https://ark.xiaohongshu.com/app-item/good/create'
REDNOTE_ONSHELF_PAGE = 'https://ark.xiaohongshu.com/app-item/good/create'
REDNOTE_LIST_SHELF_PAGE = 'https://ark.xiaohongshu.com/app-item/list/shelf'
REDNOTE_IMAGE_SPACE_PAGE = 'https://ark.xiaohongshu.com/app-system/pictureSpace'
TB_HOMEPAGE_TITLE_NAME = '淘宝'
TB_SHOP_BROWSE_TITLE_NAME = '店铺浏览-淘宝网'
TB_PERSONAL_HOMEPAGE_TITLE_NAME = '我的淘宝'
TB_LOGIN_AUTH_TITLE_NAME = '登录-身份验证'

CRAWL_PAGE_WAIT_IN_SECONDS = 5
CRAWL_OPERATION_TRY_COUNT = 3
LOGIN_SLIDE_RETRY_COUNT = 5
LOGIN_CONFIRM_PAGE_WAIT_IN_SECONDS = 15
DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS = 1
TB_PAGE_DEFAULT_ZOOM_RATIO = 0.5
SHOP_PAGE_MAX_SKU_NUM = 100
SHOP_PAGE_LOAD_MAX_COUNT = 10

# search page related controls
SEARCH_MAIN_PIC_AND_DESC_RE_EXP = re.compile('^mainPicAndDesc--\\w+')
SEARCH_SHOP_INFO_RE_EXP = re.compile('^shopInfo--\\w+')
SEARCH_DESC_WRAPPER_RE_EXP = re.compile('^[\\s\\S]*descWrapper--\\w+')
SEARCH_IMAGE_WRAPPER_RE_EXP = re.compile('^imageSwitch--\\w+')
SEARCH_PRICE_WRAPPER_RE_EXP = re.compile('^priceWrapper--\\w+')
SEARCH_SKU_UNIT_RE_EXP = re.compile('^unit--\\w+')
SEARCH_SKU_SALE_RE_EXP = re.compile('^realSales--\\w+')

# shop page related controls
SHOP_SKU_CARD_RE_EXP = re.compile('^cardContainer--\\w+')
SHOP_NAME_RE_EXP = re.compile('^shopName--\\w+')
SHOP_LOAD_STATUS_RE_EXP = re.compile('^loadStatus--\\w+')
SHOP_LOAD_MORE_FLAG_RE_EXP = re.compile('^loadmoreFlag--\\w+')
SHOP_SKU_CARD_TITLE_RE_EXP = re.compile('^title--\\w+')
SHOP_SKU_CARD_PRICE_RE_EXP = re.compile('^price--\\w+')
SHOP_SKU_CARD_SALE_RE_EXP = re.compile('^count--\\w+')
SHOP_SALE_ORDER_TAGS_RE_EXP = re.compile('^tagsContainer--\\w+')
SHOP_IMG_WRAPPER_RE_EXP = re.compile('^shopLogoUrlWrapper--\\w+')

# shop search related controls
SHOP_SEARCH_IMG_RE_EXP = re.compile('^imgWrapper--\\w+')
SHOP_SEARCH_TITLE_RE_EXP = re.compile('^title--\\w+')
SHOP_SEARCH_TIPS_RE_EXP = re.compile('^tips--\\w+')

# product detail related controls
DETAIL_OFFER_ITEMS_RE_EXP = re.compile('^\w+--skuItem--\\w+')
DETAIL_PRICE_RE_EXP = re.compile('^\w+--highlightPrice--\\w+')
DETAIL_SALE_RE_EXP = re.compile('^\w+--salesDesc--\\w+')
DETAIL_TITLE_IMGS_RE_EXP = re.compile('^\w+--thumbnailsWrap--\\w+')
DETAIL_MAIN_IMGS_V8_RE_EXP = re.compile('^descV8-container$')
DETAIL_MAIN_IMGS_V6_RE_EXP = re.compile('^descV6-container$')
DETAIL_SHOP_INFO_RE_EXP = re.compile('^\w+--shopHeader--\\w+')
DETAIL_PRODUCT_TITLE_RE_EXP = re.compile('^\\w+--ItemTitle--\\w+')
DETAIL_OFFER_INNER_ITEMS_RE_EXP = re.compile('^\w+--content--\\w+')
DETAIL_PRICE_UNIT_RE_EXP = re.compile('^\w+--symbol--\\w+')
DETAIL_PRICE_VAL_RE_EXP = re.compile('^\w+--text--\\w+')
DETAIL_MAIN_IMGS_SINGLE_IMG_V8_RE_EXP = re.compile('^descV8-singleImage$')
DETAIL_MAIN_IMGS_RICHTEXT_V8_RE_EXP = re.compile('^descV8-richtext$')
DETAIL_IMG_LINK_VALIDATE_RE_EXP = re.compile('^https://\\w+')

# Taobao product manage controls
ONSHELF_TAOBAO_NAV_BAR_RE_EXP = re.compile('^PicGroupList_treeDom__\\w+$')
ONSHELF_TAOBAO_UPLOAD_PANEL_RE_EXP = re.compile('^UploadPanel_baseConfig__\\w+$')


class WebDriverType(Enum):
    ChromDriver = 1
    SafariDriver = 2


class Crawler:
    def __init__(self, webdriver_type=WebDriverType.ChromDriver, headless=True, debug=True):
        self.logger = get_logger()
        self.headless = headless
        self.debug = debug
        if debug:
            os.chdir(DEBUG_ROOT_DIR)
        self.driver = self.init_webdriver(webdriver_type, headless)
        self.ocr = OcrParser()

    def __del__(self):
        self.close_driver()

    def init_webdriver(self, webdriver_type, headless):
        if DEBUG:
            os.chdir(DEBUG_ROOT_DIR)
        driver = None
        if webdriver_type == WebDriverType.ChromDriver:
            # TBD: handle hiding selenium from chrome, remove 'chrome is controlled by automated test software'
            if sys.platform == 'win32':
                driver_service = ChromeDriverService('./chromedriver.exe')
            elif sys.platform == 'darwin':
                driver_service = ChromeDriverService('./chromedriver')
            else:
                raise RuntimeError('Unsupported platform')
            options = webdriver.ChromeOptions()
            options.add_experimental_option('excludeSwitches', ['load-extension', 'enable-automation'])
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--ignore-certificate-errors')
            if headless:
                options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(options=options, service=driver_service)
        elif webdriver_type == WebDriverType.SafariDriver:
            options = webdriver.SafariOptions()
            driver = webdriver.Safari(options=options)
        assert (driver is not None)
        self.logger.info(f'{webdriver_type.name} is initialized')
        return driver

    def close_driver(self):
        self.logger.info('quit webdriver ...')
        self.driver.quit()

    def zoom_content(self, ratio=1.0):
        zoom_script = 'document.body.style.zoom="%f"' % ratio
        self.logger.info(f'executing script {zoom_script} and wait for seconds')
        self.driver.execute_script(zoom_script)
        time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)

    def scroll_window(self, pos=None):
        x = pos[0] if pos is not None else 'document.body.scrollWidth'
        y = pos[1] if pos is not None else 'document.body.scrollHeight'
        scroll_script = 'window.scrollTo(%s, %s)' % (str(x), str(y))
        self.logger.info(f'executing script {scroll_script} and wait for seconds')
        self.driver.execute_script(scroll_script)
        time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)

    def set_window_size(self, size=None):
        if size is None:
            self.logger.info('maximizing window and wait for seconds')
            self.driver.maximize_window()
        else:
            self.logger.info(f'set window size to ({size[0]},{size[1]}) and wait for seconds')
            self.driver.set_window_size(size[0], size[1])
        time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)

    def scroll_window_to_element(self, element):
        script = 'arguments[0].scrollIntoView();'
        self.logger.info(
            f'executing script {script} to element location ({element.location["x"]},{element.location["y"]}) '
            'and wait for seconds')
        self.driver.execute_script('arguments[0].scrollIntoView();', element)
        time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)

    def element_screenshot(self, element, file_path):
        self.logger.info(f'take screenshot for element location ({element.location["x"]},{element.location["y"]}) '
                         f'to file {file_path} and wait for seconds')
        element.screenshot(file_path)
        time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)

    def element_click(self, element, sleep=DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS):
        self.logger.info(f'element={element.accessible_name} clicked and wait for seconds')
        element.click()
        time.sleep(sleep)

    def switch_to_frame(self, iframe):
        self.logger.info(f'switch to iframe={iframe.accessible_name} and wait for seconds')
        self.driver.switch_to.frame(iframe)
        time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)

    def switch_to_default(self):
        self.logger.info(f'switch to default frame and wait for seconds')
        self.driver.switch_to.default_content()
        time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)

    def handle_taobao_login_page(self, user):
        try_count = 0
        while True:
            try:
                try_count += 1
                if try_count >= LOGIN_SLIDE_RETRY_COUNT:
                    msg = 'login retry max count exceeded, login failed.'
                    self.logger.error(msg)
                    raise LoginFailed(msg)
                self.logger.info('navigate to taobao login page and wait in seconds')
                self.driver.get(TB_LOGIN_PAGE)
                time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
                login_button = self.driver.find_element(By.CLASS_NAME, 'fm-btn').find_element(By.XPATH, 'button')
                assert (login_button is not None)
                if login_button.text == '快速进入':
                    # already logged in
                    self.element_click(login_button)
                else:
                    user_input = self.driver.find_element(By.ID, 'fm-login-id')
                    passwd_input = self.driver.find_element(By.ID, 'fm-login-password')
                    assert (user_input is not None and passwd_input is not None)
                    user_input.clear()
                    user_input.send_keys(user)
                    passwd_input.clear()
                    passwd_input.send_keys(TB_USERS[user])
                    self.element_click(login_button)
                # check whether slide check is required
                try:
                    if self.headless:
                        self.driver.find_element(By.XPATH, '//*[@id="baxia-dialog-content"]')
                        self.logger.info('slide check needed, just try to bypass it by reinitialize webdriver')
                        self.close_driver()
                        self.driver = self.init_webdriver(WebDriverType.ChromDriver, self.headless)
                        continue
                except NoSuchElementException:
                    self.logger.info('do not need slide check this time, just continue')
                time.sleep(LOGIN_CONFIRM_PAGE_WAIT_IN_SECONDS)
                break
            except NoSuchElementException:
                self.logger.info('can not find login form, wait for seconds an retry')
                time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)

    def handle_taobao_post_login_page(self, user):
        self.logger.info('check if we are in taobao/personal homepage')
        while True:
            if self.driver.title == TB_PERSONAL_HOMEPAGE_TITLE_NAME or self.driver.title == TB_HOMEPAGE_TITLE_NAME:
                self.logger.info('we are already in taobao/personal homepage, now perform following crawling')
                break
            elif self.driver.title == TB_LOGIN_AUTH_TITLE_NAME:
                self.logger.info('we are in login verification page, use SMS to get auth code')
                iframe = self.driver.find_element(By.XPATH, '//*[@id="content"]/div/div[1]/iframe')
                self.driver.switch_to.frame(iframe)
                code_input = self.driver.find_element(By.ID, 'J_Phone_Checkcode')
                sms_btn = self.driver.find_element(By.ID, 'J_GetCode')
                confirm_btn = self.driver.find_element(By.ID, 'submitBtn')
                sms_btn.click()
                sms_code = input(f'Please input SMS verification code for user={user}: ')
                code_input.send_keys(sms_code)
                confirm_btn.click()
                time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
                break
            else:
                self.logger.info(
                    'we are not in taobao/personal homepage, '
                    'finish authentication and navigate to taobao/personal homepage to continue crawling...')
                time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)

    def login_taobao(self, user=TB_CRAWL_USER):
        self.handle_taobao_login_page(user)
        self.handle_taobao_post_login_page(user)
        self.set_window_size()

    def login_rednote(self, user=REDNOTE_SHOP_USER):
        self.driver.get(REDNOTE_LOGIN_PAGE)
        time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
        tab_div = self.driver.find_element(By.CLASS_NAME, 'beer-login-container')
        account_div = tab_div.find_element(By.XPATH, 'div/div/div[1]/div[2]/div[1]')
        self.element_click(account_div)
        login_form = self.driver.find_element(By.ID, 'login-form')
        login_inputs = login_form.find_elements(By.XPATH, 'div/div/input')
        assert (len(login_inputs) == 2)
        email_input, password_input = login_inputs
        email_input.clear()
        email_input.send_keys(user)
        password_input.clear()
        password_input.send_keys(REDNOTE_USERS[user])
        btns = self.driver.find_elements(By.XPATH, '//button')
        assert (len(btns) == 1)
        btns[0].click()
        time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)

    def crawl_taobao_search_results(self, search_key, num_of_pages, sale_order, update_id, target_product_ids=None):
        self.logger.info(
            f'navigate to taobao search page with search_key={search_key} and num_of_pages={num_of_pages}, sale_order={sale_order}')
        self.driver.get(TB_SEARCH_PAGE)
        qbox = self.driver.find_element(By.ID, 'q')
        qbox.clear()
        qbox.send_keys(search_key)
        qbox.send_keys(Keys.RETURN)
        ids_set = set()
        for page in range(1, num_of_pages + 1):
            try:
                self.logger.info('wait search results ready for seconds')
                time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
                # press '销量' navigate bar on first page if sale_order is True
                if page == 1 and sale_order:
                    sale_order_div = None
                    divs = self.driver.find_elements(By.CLASS_NAME, 'next-tabs-tab-inner')
                    for div in divs:
                        if div.text == '销量':
                            sale_order_div = div
                            break
                    assert (sale_order_div is not None)
                    self.element_click(sale_order_div)
                    self.logger.info('wait search results ready by press order first for seconds')
                    time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
                search_result_wrapper = self.driver.find_element(By.ID, 'content_items_wrapper')
                search_results = search_result_wrapper.find_elements(By.XPATH, 'div/a')
                self.logger.info(
                    f'find {len(search_results)} search results with search_key={search_key} and page= {page}')
                for search_result in search_results:
                    self.parse_taobao_search_result(search_result, ids_set, update_id, target_product_ids)
                if page < num_of_pages:
                    btn_pages = self.driver.find_elements(By.CLASS_NAME, 'next-pagination-pages')
                    assert (len(btn_pages) >= 1)  # 至少下面会有一个导航栏
                    btn_list = btn_pages[-1].find_elements(By.XPATH, 'button')
                    assert (len(btn_list) == 3)  # 下面导航栏里直属三个按钮：上一页，下一页，确定
                    self.logger.info(
                        f'get next page search results for search_key={search_key} and page={page + 1} by press next page')
                    self.element_click(btn_list[1])
            except AssertionError:
                self.logger.error(
                    'assertion failed in search result page, just stop crawling')
                traceback.print_exc()
                break
            except Exception:
                self.logger.error('get unexcepted exception while parsing search results, just stop crawling')
                traceback.print_exc()
                break

    def parse_taobao_search_result(self, search_result, ids_set, update_id, target_product_ids=None):
        try:
            self.logger.info(f'parsing search result: {search_result.accessible_name}')
            product_id = self.parse_product_id_from_item(search_result.get_attribute('id'))
            target_product_ids = target_product_ids or []  # None表示不限制target product id
            if len(target_product_ids) == 0 or product_id in target_product_ids:
                self.logger.info(f'parsed product_id={product_id} in target_product_ids={target_product_ids}')
            else:
                self.logger.info(
                    f'parsed product_id={product_id} not in target_product_ids={target_product_ids}, crawl it too')
            product_link = search_result.get_attribute('href')
            sku_id = self.parse_sku_id_from_product_link(product_link) or '0'
            product_items = search_result.find_elements(By.XPATH, 'div/div')
            sku_summary, shop_summary = None, None
            for item in product_items:
                cls_name = item.get_attribute('class')
                if cls_name is None:
                    continue
                elif re.match(SEARCH_MAIN_PIC_AND_DESC_RE_EXP, cls_name):
                    sku_summary = item
                elif re.match(SEARCH_SHOP_INFO_RE_EXP, cls_name):
                    shop_summary = item
            assert (sku_summary is not None and shop_summary is not None)
            sku_items = sku_summary.find_elements(By.XPATH, 'div')
            image_wrapper, sku_title_wrapper, price_wrapper = None, None, None
            for item in sku_items:
                cls_name = item.get_attribute('class')
                if cls_name is None:
                    continue
                elif re.match(SEARCH_DESC_WRAPPER_RE_EXP, cls_name):
                    sku_title_wrapper = item
                elif re.match(SEARCH_PRICE_WRAPPER_RE_EXP, cls_name):
                    price_wrapper = item
                elif re.match(SEARCH_IMAGE_WRAPPER_RE_EXP, cls_name):
                    image_wrapper = item
            assert (sku_title_wrapper is not None and price_wrapper is not None and image_wrapper is not None)
            product_title = self.parse_product_title(sku_title_wrapper.find_element(By.XPATH, 'div/span').text)
            if len(product_title) == 0:
                title_spans = sku_title_wrapper.find_elements(By.XPATH, 'div/span/span')
                if len(title_spans) > 0:
                    for title_span in title_spans:
                        product_title += self.parse_product_title(title_span.text)
            product_cover = image_wrapper.find_element(By.XPATH, 'img').get_attribute('src')
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
            price_unit = self.parse_price_unit(price_unit_span.text)
            display_sale = self.parse_sale_in_search(display_sale_span.text)
            price_divs = price_wrapper.find_elements(By.XPATH, 'div/div/div')
            assert (len(price_divs) == 2)
            display_price = self.parse_price('%s%s' % (price_divs[0].text, price_divs[1].text))
            shop_link = shop_summary.find_element(By.XPATH, 'div/a').get_attribute('href') or ''
            shop_name = shop_summary.find_elements(By.XPATH, 'div/a/div/span')[-1].text
            if product_id not in ids_set:
                self.save_taobao_search_result(product_id, sku_id, product_title,
                                               product_link, product_cover,
                                               shop_name, shop_link,
                                               price_unit, display_price, display_sale,
                                               update_id)
            ids_set.add(product_id)
        except AssertionError:
            self.logger.error(f'assertion failed while parsing {search_result.accessible_name}, just ignore')
            traceback.print_exc()
            return
        except Exception:
            self.logger.error(f'get unhandled exception while parsing {search_result.accessible_name}, just ignore')
            traceback.print_exc()
            return

    def save_taobao_search_result(self, product_id, sku_id, product_title, product_link, product_cover,
                                  shop_name, shop_link, price_unit,
                                  display_price, display_sale, update_id):
        self.logger.info(f'save_taobao_search_result parsed record:\n'
                         f'\t\tproduct_id={product_id}\n'
                         f'\t\tsku_id={sku_id}\n'
                         f'\t\tproduct_title={product_title}\n'
                         f'\t\tproduct_cover={product_cover}\n'
                         f'\t\tproduct_link={product_link}\n'
                         f'\t\tshop_name={shop_name}\n'
                         f'\t\tshop_link={shop_link}\n'
                         f'\t\tprice_unit={price_unit}\n'
                         f'\t\tdisplay_price={display_price}\n'
                         f'\t\tdisplay_sale={display_sale}\n'
                         f'\t\tupdate_id={update_id}\n')
        # save shop info
        update_role = self.save_taobao_search_result.__name__
        # save shop info
        update_shop_info(shop_name, update_id, update_role, shop_link, SHOP_COVER_DEFAULT_LINK, None)
        # save product info
        update_product_info(product_id, update_id, update_role,
                            sku_id, product_title, product_link, product_cover,
                            shop_name, shop_link,
                            price_unit, display_price, display_sale,
                            None, None, None, None)
        # save product sales info,
        # remember there can be same product in different search pages,
        # we only add one sale record for same product in one search process.
        add_product_sale(product_id, shop_name,
                         price_unit, display_price, display_sale, None,
                         update_id, update_role)

    def craw_taobao_shop_page(self, shop_link, sale_order, update_id, target_product_ids=None):
        self.load_shop_and_products(shop_link, sale_order)
        divs = self.driver.find_elements(By.XPATH, '//div')
        shop_name = None
        shop_cover = ''
        sku_divs = []
        for div in divs:
            cls_name = div.get_attribute('class')
            if cls_name is None:
                continue
            elif re.match(SHOP_SKU_CARD_RE_EXP, cls_name):
                sku_divs.append(div)
            elif re.match(SHOP_NAME_RE_EXP, cls_name):
                child_spans = div.find_elements(By.XPATH, 'span')
                if len(child_spans) == 0:
                    shop_name = div.text
                else:
                    shop_name = child_spans[0].text
            elif re.match(SHOP_IMG_WRAPPER_RE_EXP, cls_name):
                shop_cover = div.find_element(By.XPATH, 'img').get_attribute('src')
        assert (shop_name is not None)
        update_shop_info(shop_name, update_id, self.craw_taobao_shop_page.__name__, shop_link, shop_cover, None)
        # for craw_taobao_shop_sku_v2
        target_products = []
        if target_products is not None:
            for target_id in target_product_ids:
                try:
                    target_products.append(ProductInfo.get(ProductInfo.product_id == target_id))
                except DoesNotExist:
                    self.logger.info(
                        f'target product_id={target_id} in target_product_ids={target_product_ids} does not exist, just ignore')
                    continue
        for sku_div in sku_divs:
            try:
                self.craw_taobao_shop_sku_v2(sku_div, shop_name, shop_link, update_id, target_products)
            except PriceOCRError as e:
                self.logger.error(f'get PriceOCRGetEmptyError={e}, nothing will be updated and just continue')
                traceback.print_exc()
                continue

    def load_shop_and_products(self, shop_link, sale_order):
        self.logger.info(f'navigate to shop_link={shop_link} and wait for seconds')
        self.driver.get(shop_link)
        time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
        if self.driver.title == TB_SHOP_BROWSE_TITLE_NAME or self.driver.title == TB_HOMEPAGE_TITLE_NAME:
            # "没有找到相应的店铺信息" 页面
            msg = f'shop_link={shop_link} not found'
            self.logger.error(msg)
            raise ShopLinkNotFound(msg)
        if len(self.driver.find_elements(By.ID, 'banner')) > 0 and len(self.driver.find_elements(By.ID, 'err')) > 0:
            tip = self.driver.find_element(By.ID, 'err').find_elements(By.XPATH, 'div/p')[0].text
            if tip == '抱歉！页面无法访问……':
                # "抱歉！页面无法访问" 页面
                msg = f'shop_link={shop_link} can not be accessed now'
                self.logger.error(msg)
                raise ShopLinkNotAccessible(msg)
        # 如果找到销量排序按钮，点击按销量排序
        if sale_order:
            divs = self.driver.find_elements(By.XPATH, '//div')
            for div in divs:
                cls_name = div.get_attribute('class')
                if cls_name is None:
                    continue
                elif re.match(SHOP_SALE_ORDER_TAGS_RE_EXP, cls_name):
                    tag_divs = div.find_elements(By.XPATH, 'div/div')
                    for tag_div in tag_divs:
                        if tag_div.find_element(By.XPATH, 'span').text == '销量':
                            self.element_click(tag_div)
                            break
                    break
        load_count = 0
        while True:
            if load_count >= SHOP_PAGE_LOAD_MAX_COUNT:
                self.logger.info('may not scrolled to the end of shop page, max load_count exceeded')
                break
            divs = self.driver.find_elements(By.XPATH, '//div')
            num_of_skus = 0
            sku_exceeded = False
            load_more_flag_div = None
            loaded = False
            for div in divs:
                cls_name = div.get_attribute('class')
                if cls_name is None:
                    continue
                elif re.match(SHOP_SKU_CARD_RE_EXP, cls_name):
                    num_of_skus += 1
                    if num_of_skus > SHOP_PAGE_MAX_SKU_NUM:
                        self.logger.info('may not scrolled to the end of shop page, max sku exceeded')
                        sku_exceeded = True
                        break
                elif re.match(SHOP_LOAD_STATUS_RE_EXP, cls_name):
                    if div.text == '没有更多商品':
                        self.logger.info('scrolled to the end of shop page')
                        loaded = True
                        break
                elif re.match(SHOP_LOAD_MORE_FLAG_RE_EXP, cls_name):
                    load_more_flag_div = div
            if loaded or sku_exceeded:
                self.scroll_window((0, 0))
                break
            # 有些特殊店铺没有 load_more_flag_div, 会触发此处断言。这种店铺是完全定制的页面（非淘宝模板）
            # 我们暂时不支持这种店铺，未来可能将对重点其他模板进行支持。
            # 这种店铺的商品仍然可以通过search或detail页面抓取来收录
            if load_more_flag_div is None:
                msg = f'shop is not taobao standard shop page, shop_link={shop_link}'
                self.logger.error(msg)
                raise NotStandardShop(msg)
            self.scroll_window_to_element(load_more_flag_div)
            load_count += 1

    def craw_taobao_shop_sku(self, shop_sku_div, shop_name, shop_link, update_id, target_product_ids=None):
        target_product_ids = target_product_ids or []
        product_link = shop_sku_div.find_element(By.XPATH, 'a').get_attribute('href')
        product_id = self.parse_product_id_from_product_link(product_link)
        if len(target_product_ids) == 0 or product_id in target_product_ids:
            self.logger.info(f'parsed product_id={product_id} in target_product_ids={target_product_ids}')
        else:
            self.logger.info(
                f'parsed product_id={product_id} not in target_product_ids={target_product_ids}, crawl it too')
        product_cover = SHOP_PRODUCT_COVER_PLACEHOLDER_LINK
        for _ in range(CRAWL_OPERATION_TRY_COUNT):
            self.scroll_window_to_element(shop_sku_div)
            product_cover = shop_sku_div.find_element(By.XPATH, 'img').get_attribute('src')
            if product_cover != SHOP_PRODUCT_COVER_PLACEHOLDER_LINK:
                break
        sku_id = self.parse_sku_id_from_product_link(product_link) or ''
        divs = shop_sku_div.find_elements(By.XPATH, './/div')
        title_div, price_div, sale_div = None, None, None
        for div in divs:
            cls_name = div.get_attribute('class')
            if cls_name is None:
                continue
            elif re.match(SHOP_SKU_CARD_TITLE_RE_EXP, cls_name):
                title_div = div
            elif re.match(SHOP_SKU_CARD_PRICE_RE_EXP, cls_name):
                price_div = div
            elif re.match(SHOP_SKU_CARD_SALE_RE_EXP, cls_name):
                sale_div = div
        assert (title_div is not None and price_div is not None and sale_div is not None)
        product_title = self.parse_product_title(title_div.text)
        price_spans = price_div.find_elements(By.XPATH, 'span')
        assert (len(price_spans) == 2)
        price_unit = self.parse_price_unit(price_spans[0].text)
        display_price = self.parse_price_span(price_spans[1], product_id)
        product_sale = self.parse_sale_in_search(sale_div.text)
        # update product_info and product_sales table
        self.save_taobao_shop_sku_result(product_id, sku_id, product_title, product_link, product_cover,
                                         shop_name, shop_link,
                                         price_unit, display_price, product_sale, update_id)

    def craw_taobao_shop_sku_v2(self, shop_sku_div, shop_name, shop_link, update_id, target_products):
        if len(target_products) == 0:
            self.logger.info('there is no target products, just return in v2')
            return
        self.logger.info('we can not parse product_id in v2, just ignore and compare product title')
        product_cover = SHOP_PRODUCT_COVER_PLACEHOLDER_LINK
        for _ in range(CRAWL_OPERATION_TRY_COUNT):
            self.scroll_window_to_element(shop_sku_div)
            product_cover = shop_sku_div.find_element(By.XPATH, 'img').get_attribute('src')
            if product_cover != SHOP_PRODUCT_COVER_PLACEHOLDER_LINK:
                break
        divs = shop_sku_div.find_elements(By.XPATH, './/div')
        title_div, price_div, sale_div = None, None, None
        for div in divs:
            cls_name = div.get_attribute('class')
            if cls_name is None:
                continue
            elif re.match(SHOP_SKU_CARD_TITLE_RE_EXP, cls_name):
                title_div = div
            elif re.match(SHOP_SKU_CARD_PRICE_RE_EXP, cls_name):
                price_div = div
            elif re.match(SHOP_SKU_CARD_SALE_RE_EXP, cls_name):
                sale_div = div
        assert (title_div is not None and price_div is not None and sale_div is not None)
        product_title = self.parse_product_title(title_div.text)
        for product in target_products:
            if product.product_title == product_title:
                product_id = product.product_id
                price_spans = price_div.find_elements(By.XPATH, 'span')
                assert (len(price_spans) == 2)
                price_unit = self.parse_price_unit(price_spans[0].text)
                display_price = self.parse_price_span(price_spans[1], product_id)
                product_sale = self.parse_sale_in_search(sale_div.text)
                # update product_info and product_sales table
                self.save_taobao_shop_sku_result_v2(product_id, product_cover,
                                                    shop_name, shop_link,
                                                    price_unit, display_price,
                                                    product_sale, update_id)
                break

    def save_taobao_shop_sku_result(self, product_id, sku_id, product_title, product_link, product_cover,
                                    shop_name, shop_link,
                                    price_unit, display_price, display_sale, update_id):
        self.logger.info(f'save_taobao_shop_sku_result parsed record:\n'
                         f'\t\tproduct_id={product_id}\n'
                         f'\t\tsku_id={sku_id}\n'
                         f'\t\tproduct_title={product_title}\n'
                         f'\t\tproduct_link={product_link}\n'
                         f'\t\tproduct_cover={product_cover}\n'
                         f'\t\tshop_name={shop_name}\n'
                         f'\t\tshop_link={shop_link}\n'
                         f'\t\tprice_unit={price_unit}\n'
                         f'\t\tdisplay_price={display_price}\n'
                         f'\t\tdisplay_sale={display_sale}\n'
                         f'\t\tupdate_id={update_id}\n')
        update_role = self.save_taobao_shop_sku_result.__name__
        update_product_info(product_id, update_id, update_role,
                            sku_id, product_title, product_link, product_cover,
                            shop_name, shop_link,
                            price_unit, display_price, display_sale,
                            None, None, None, None)
        add_product_sale(product_id, shop_name, price_unit, display_price, display_sale, None, update_id, update_role)

    def save_taobao_shop_sku_result_v2(self, product_id, product_cover,
                                       shop_name, shop_link,
                                       price_unit, display_price, display_sale, update_id):
        self.logger.info(f'save_taobao_shop_sku_result parsed record:\n'
                         f'\t\tproduct_id={product_id}\n'
                         f'\t\tproduct_cover={product_cover}\n'
                         f'\t\tshop_name={shop_name}\n'
                         f'\t\tshop_link={shop_link}\n'
                         f'\t\tprice_unit={price_unit}\n'
                         f'\t\tdisplay_price={display_price}\n'
                         f'\t\tdisplay_sale={display_sale}\n'
                         f'\t\tupdate_id={update_id}\n')
        update_role = self.save_taobao_shop_sku_result.__name__
        update_product_info(product_id, update_id, update_role,
                            product_cover=product_cover,
                            shop_name=shop_name, shop_link=shop_link,
                            price_unit=price_unit, display_price=display_price, display_sale=display_sale)
        add_product_sale(product_id, shop_name, price_unit, display_price, display_sale, None, update_id, update_role)

    def crawl_taobao_shop_link_by_search(self, shop_name, update_id):
        self.logger.info('navigate to taobao shop search page')
        self.driver.get(TB_SEARCH_PAGE)
        divs = self.driver.find_elements(By.XPATH, '//div')
        shop_tab_div = None
        for div in divs:
            title = div.text.strip()
            if title == '店铺':
                shop_tab_div = div
                break
        assert (shop_tab_div is not None)
        self.element_click(shop_tab_div)
        qbox = self.driver.find_element(By.ID, 'q')
        qbox.clear()
        qbox.send_keys(shop_name)
        qbox.send_keys(Keys.RETURN)
        self.logger.info(f'search shop_name={shop_name} and wait for seconds')
        time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
        shop_wrapper_div = self.driver.find_element(By.ID, 'srp_shopLayout_shopContentWrapper')
        assert (shop_wrapper_div is not None)
        for div in shop_wrapper_div.find_elements(By.XPATH, 'div/div'):
            cls_name = div.get_attribute('class')
            if cls_name is None:
                continue
            elif re.match(SHOP_SEARCH_TIPS_RE_EXP, cls_name) and div.text == '“没有找到相关宝贝”':
                msg = f'can not find shop_name={shop_name} by shop search, no results found'
                self.logger.error(msg)
                raise ShopNotFoundInSearch(msg)
        shop_link = None
        shop_cover = ''
        for shop_a in shop_wrapper_div.find_elements(By.XPATH, 'a'):
            shop_divs = shop_a.find_elements(By.XPATH, './/div')
            shop_found = False
            for shop_div in shop_divs:
                cls_name = shop_div.get_attribute('class')
                if cls_name is None:
                    continue
                elif re.match(SHOP_SEARCH_TITLE_RE_EXP, cls_name) and shop_name == shop_div.text.strip():
                    shop_link = shop_a.get_attribute('href')
                    shop_found = True
                elif re.match(SHOP_SEARCH_IMG_RE_EXP, cls_name):
                    shop_cover = shop_div.find_element(By.XPATH, 'img').get_attribute('src')
            if shop_found:
                break
        if shop_link is not None:
            self.logger.info(f'update shop_name={shop_name} and shop_link={shop_link}')
            update_shop_info(shop_name, update_id, self.crawl_taobao_shop_link_by_search.__name__, shop_link,
                             shop_cover, None)
        else:
            msg = f'can not find shop_name={shop_name} by shop search, all results parsed'
            self.logger.error(msg)
            raise ShopNotFoundInSearch(msg)

    def parse_price_span(self, price_span, product_id):
        temp_file_name = f'{IMAGE_DIR}/{product_id}-{uuid.uuid4().hex}.png'
        self.element_screenshot(price_span, temp_file_name)
        return self.ocr.par_price_ocr(temp_file_name)

    def craw_taobao_detail_page(self, product_id, product_link, update_id):
        self.logger.info(f'navigate to product_id={product_id} with product_link={product_link} and wait for seconds')
        self.driver.get(product_link)
        time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
        # set zoom ratio
        self.zoom_content(TB_PAGE_DEFAULT_ZOOM_RATIO)
        # parse detail page
        title_div, price_div, shop_info_div = None, None, None
        display_sale_div = None
        title_image_div = None
        page_image_v6_div, page_image_v8_div = None, None
        offer_items_divs_wrapper = []
        divs = self.driver.find_elements(By.XPATH, '//div')
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
        sku_id = self.parse_sku_id_from_product_link(product_link) or '0'
        product_title = self.parse_product_title(title_div.find_element(By.XPATH, 'h1').text)
        shop_info_inner = shop_info_div.find_element(By.XPATH, 'a')
        shop_name = shop_info_inner.find_element(By.XPATH, 'div/div/span').text
        shop_link = shop_info_inner.get_attribute('href')
        # parse product sale
        display_sale = self.parse_sale_in_detail(display_sale_div.text) if display_sale_div is not None else -1
        # parse product offer items
        offer_details, price_unit, lowest_price = self.craw_taobao_detail_offer_details(offer_items_divs_wrapper,
                                                                                        price_div)
        # parse title images
        title_images = self.crawl_taobao_detail_title_images(title_image_div)
        # parse main images
        main_images = self.crawl_taobao_detail_main_images(page_image_v8_div, page_image_v6_div)
        # update product info in DB
        self.save_taobao_detail_result(product_id, sku_id, product_title, product_link,
                                       shop_name, shop_link,
                                       price_unit, lowest_price, display_sale,
                                       title_images, main_images, offer_details,
                                       update_id)

    def craw_taobao_detail_offer_details(self, offer_items_divs_wrapper, price_div):
        offer_items_divs = []
        offer_items = []
        for offer_items_div in offer_items_divs_wrapper:
            content_div = None
            inner_divs = offer_items_div.find_elements(By.XPATH, 'div')
            for inner_div in inner_divs:
                cls_name = inner_div.get_attribute('class')
                if cls_name is None:
                    continue
                elif re.match(DETAIL_OFFER_INNER_ITEMS_RE_EXP, cls_name):
                    content_div = inner_div
                    break
            assert (content_div is not None)
            offer_item_divs_inner = content_div.find_elements(By.XPATH, 'div')
            offer_items_divs.append(offer_item_divs_inner)
            offer_items.append([self.craw_taobao_detail_offer_items(v) for v in offer_item_divs_inner])
        self.logger.info(f'get offer items: {offer_items}')
        # parse all offers
        offers, price_unit, lowest_price = self.craw_taobao_detail_offers(offer_items_divs, price_div)
        offer_details = {
            "offer_items": offer_items,
            "valid_offers": offers
        }
        self.logger.info(f'get offer details: {offer_details}')
        return offer_details, price_unit, lowest_price

    def crawl_taobao_detail_title_images(self, title_image_div):
        title_imgs = title_image_div.find_elements(By.XPATH, 'ul/li/img')
        title_images = [title_img.get_attribute('src') for title_img in title_imgs]
        self.logger.info(f'get title image list: {title_images}')
        return title_images

    def crawl_taobao_detail_main_images(self, page_image_v8_div, page_image_v6_div):
        main_images = []
        if page_image_v8_div is not None:
            main_images = self.crawl_taobao_detail_main_images_v8(page_image_v8_div)
        elif page_image_v6_div is not None:
            main_images = self.crawl_taobao_detail_main_images_v6(page_image_v6_div)
        return main_images

    def crawl_taobao_detail_main_images_v8(self, page_image_v8_div):
        main_images = []
        main_imgs = page_image_v8_div.find_elements(By.XPATH, './/div')
        for main_img in main_imgs:
            cls_name = main_img.get_attribute('class')
            if cls_name is None:
                continue
            elif re.match(DETAIL_MAIN_IMGS_SINGLE_IMG_V8_RE_EXP, cls_name):
                # we only get pic links and ignore other format
                try:
                    data_src = main_img.find_element(By.XPATH, 'img').get_attribute('data-src')
                    if data_src is not None and self.is_valid_image_link(data_src):
                        main_images.append(data_src)
                    else:
                        src = main_img.find_element(By.XPATH, 'img').get_attribute('src')
                        if self.is_valid_image_link(src):
                            main_images.append(src)
                except NoSuchElementException:
                    self.logger.info('detail page material is not an image, ignore')
            elif re.match(DETAIL_MAIN_IMGS_RICHTEXT_V8_RE_EXP, cls_name):
                # we only get pic links and ignore other format
                try:
                    for img_element in main_img.find_elements(By.XPATH, 'p/img'):
                        self.scroll_window_to_element(img_element)  # the resource is lazy loaded
                    img_elements = main_img.find_elements(By.XPATH, 'p/img')
                    for img_element in img_elements:
                        src = img_element.get_attribute('src')
                        if self.is_valid_image_link(src):
                            main_images.append(src)
                except NoSuchElementException:
                    self.logger.info('detail page material is not an image, ignore')
        self.logger.info(f'get main image list: {main_images}')
        return main_images

    def crawl_taobao_detail_main_images_v6(self, page_image_v6_div):
        main_images = []
        for img_element in page_image_v6_div.find_elements(By.XPATH, 'div/div/img'):
            self.scroll_window_to_element(img_element)  # the resource is lazy loaded
        for img_element in page_image_v6_div.find_elements(By.XPATH, 'div/div/img'):
            src = img_element.get_attribute('src')
            if self.is_valid_image_link(src):
                main_images.append(src)
        self.logger.info(f'get main image list: {main_images}')
        return main_images

    def craw_taobao_detail_offers(self, value_items_divs, sku_price_div):
        combos = self.get_value_item_combos(value_items_divs)
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
                    self.element_click(value_item)
                except ElementClickInterceptedException:
                    self.scroll_window_to_element(value_item)
                    self.element_click(value_item)
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
            price_unit = self.parse_price_unit(price_unit_span.text)
            offer.append(price_unit)
            price_val = self.parse_price(price_val_span.text)
            if price_val < lowest_price:
                lowest_price = price_val
            offer.append(price_val)
            offers.append(offer)
        self.logger.info(f'get offers={offers}, price_unit={price_unit}, lowest_price={lowest_price}')
        return offers, price_unit, lowest_price

    def get_value_item_combos(self, value_items_divs):
        combos, combo = [], []
        self.inner_get_value_item_combos(value_items_divs, 0, combo, combos)
        return combos

    def inner_get_value_item_combos(self, value_items_divs, cur, combo, combos):
        if len(combo) == len(value_items_divs):
            combos.append(combo.copy())
            return
        for value_item in value_items_divs[cur]:
            combo.append(value_item)
            self.inner_get_value_item_combos(value_items_divs, cur + 1, combo, combos)
            combo.pop()

    def craw_taobao_detail_offer_items(self, offer_item_div):
        offer_item = {}
        try:
            span = offer_item_div.find_element(By.XPATH, 'span')
            offer_item['name'] = span.text
        except Exception:
            self.logger.error(f'get exception while parsing offer_item span {offer_item_div.accessible_name}')
            traceback.print_exc()
            return None
        try:
            img = offer_item_div.find_element(By.XPATH, 'img')
            offer_item['img'] = img.get_attribute('src')
        except Exception:
            self.logger.error('some sku_item do not have img, just ignore')
        return offer_item

    def save_taobao_detail_result(self, product_id, sku_id, product_title, product_link,
                                  shop_name, shop_link,
                                  price_unit, display_price, display_sale,
                                  title_images, main_images, offer_details,
                                  update_id):
        self.logger.info(f'save_taobao_detail_result parsed record:\n'
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
        update_role = self.save_taobao_detail_result.__name__
        update_product_info(product_id, update_id, update_role,
                            sku_id, product_title, product_link, '',
                            shop_name, shop_link,
                            price_unit, display_price, display_sale,
                            title_images, main_images, offer_details, None)
        add_product_sale(product_id, shop_name, price_unit, display_price, display_sale, None,
                         update_id, update_role)
        update_shop_info(shop_name, update_id, update_role, shop_link, SHOP_COVER_DEFAULT_LINK, None)

    def download_product_resources(self, product_id, update_id, ts=None, force_download=False):
        try:
            exist_pi = ProductInfo.get(ProductInfo.product_id == product_id)
        except DoesNotExist:
            self.logger.error(f'No product info found for product_id={product_id}, just return')
            return
        # create download folder
        product_root_dir = f'{PRODUCT_DIR}/{product_id}/{int(time.time()) if ts is None else ts}'
        product_path = Path(product_root_dir)
        if product_path.exists():
            if force_download:
                self.logger.info(
                    f'product path already exist with root_dir={product_root_dir}, will force clean it and redownload')
                shutil.rmtree(product_root_dir, ignore_errors=True)
            else:
                self.logger.info(
                    f'product path already exist with root_dir={product_root_dir}, just ignore')
                return
        self.logger.info(f'create product_root_dir={product_root_dir}')
        product_path.mkdir(parents=True, exist_ok=True)
        # download title images
        self.logger.info(
            f'download product title images with product_id={exist_pi.product_id} and title_imgs={exist_pi.title_imgs}')
        title_imgs = json_loads(exist_pi.title_imgs)
        if len(title_imgs) > 0:
            Path(f'{product_root_dir}/title_images').mkdir()
        idx = 0
        for title_img in title_imgs:
            try:
                idx += 1
                file_path = f'{product_root_dir}/title_images/{idx}.png'
                self.download_product_image(title_img, file_path)
                resize_image(file_path)
            except Exception:
                self.logger.error(f'get unhandled exception while get page image link={title_img}, arise the exception')
                traceback.print_exc()
                raise
        # download page images
        self.logger.info(
            f'download product title images with product_id={exist_pi.product_id} and title_imgs={exist_pi.page_imgs}')
        page_imgs = json_loads(exist_pi.page_imgs)
        if len(page_imgs) > 0:
            Path(f'{product_root_dir}/page_images').mkdir()
        idx = 0
        for page_img in page_imgs:
            try:
                idx += 1
                file_path = f'{product_root_dir}/page_images/{idx}.png'
                self.download_product_image(page_img, file_path)
                resize_image(file_path)
            except Exception:
                self.logger.error(f'get unhandled exception while get page image link={page_img}, arise the exception')
                traceback.print_exc()
                raise
        additional_properties = json_loads(exist_pi.additional_properties)
        additional_properties[RESOURCE_ROOT_KEY] = product_root_dir[product_root_dir.find(PRODUCT_DIR_KEY):]
        update_product_info(exist_pi.product_id, update_id, self.download_product_resources.__name__,
                            additional_properties=additional_properties)

    def download_product_image(self, image_url, file_path):
        self.driver.get(image_url)
        time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
        img = self.driver.find_element(By.XPATH, '//img')
        assert (img is not None)
        self.logger.info(f'download product title_image={image_url}')
        self.element_screenshot(img, file_path)

    def product_manage_ready(self, product_id, shop_name, platform, update_id):
        shadow_product = ShadowProductInfo.get(ShadowProductInfo.product_id == product_id)
        if shadow_product.status == SHADOW_PRODUCT_STATUS_NEW:
            product = ProductInfo.get(ProductInfo.product_id == product_id)
            additional_properties = json_loads(product.additional_properties)
            if RESOURCE_ROOT_KEY in additional_properties and LLM_ANALYSIS_KEY in additional_properties:
                title_imgs = [f'{idx + 1}.png' for idx in range(0, len(json_loads(product.title_imgs)))]
                page_imgs = [f'{idx + 1}.png' for idx in range(0, len(json_loads(product.page_imgs)))]
                offer_details = json_loads(product.offer_details)
                status = SHADOW_PRODUCT_STATUS_READY
            else:
                title_imgs = []
                page_imgs = []
                offer_details = {}
                status = SHADOW_PRODUCT_STATUS_NEW
            # 我们总是将shadow_product更新到最新，只要它还是NEW状态
            update_shadow_product_info(product.product_id, status, update_id,
                                       self.product_manage_ready.__name__,
                                       SHADOW_PRODUCT_DEFAULT_ID, REDNOTE_PRODUCT_DEFAULT_ID,
                                       product.product_title, product.shop_name,
                                       product.price_unit, product.display_price, SHADOW_PRODUCT_DEFAULT_INVENTORY_SIZE,
                                       title_imgs, page_imgs, offer_details, additional_properties)
            return True if status == SHADOW_PRODUCT_STATUS_READY else False
        else:
            self.logger.info(f'shadow product_id={product_id}, shop_name={shop_name} is not in NEW status, just ignore')
            return True

    def handle_taobao_resource_upload(self, product):
        self.driver.get(TB_IMAGE_SPACE_PAGE)
        time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
        upload_btn1 = self.driver.find_element(By.XPATH, '//*[@id="microapp-sucai-tu-container"]/div/div/div/div[1]/div[2]/div/div[1]/div[2]/button[2]')
        self.element_click(upload_btn1)
        form_controls = self.driver.find_elements(By.CLASS_NAME, 'next-form-item-control')
        new_folder_btn = None
        for form in form_controls:
            spans = form.find_elements(By.XPATH, 'span/span[1]/span[1]')
            if len(spans) == 1:
                self.element_click(spans[0])
            btns = form.find_elements(By.XPATH, 'button')
            btn_spans = form.find_elements(By.XPATH, 'button/span')
            if len(btns) == 1 and len(btn_spans) == 1 and btn_spans[0].text == '新建文件夹':
                new_folder_btn = btns[0]
        assert (new_folder_btn is not None)
        # click products
        menu_wrappers = self.driver.find_elements(By.CLASS_NAME, 'next-cascader-menu-wrapper')
        found = False
        for menu in menu_wrappers:
            spans = menu.find_elements(By.XPATH, './/span')
            for span in spans:
                if span.text == 'products':
                    self.element_click(span)
                    found = True
                    break
        if not found:
            self.logger.info('can not find products root path, raise exception')
            raise RuntimeError('products root path not found')
        menu_wrappers = self.driver.find_elements(By.CLASS_NAME, 'next-cascader-menu-wrapper')
        product_found = False
        for menu in menu_wrappers:
            spans = menu.find_elements(By.XPATH, './/span')
            for span in spans:
                if span.text == product.product_id:
                    self.element_click(span)
                    product_found = True
                    break
        # if product_found:
        #     self.logger.info(f'product_id={product.product_id} resource already uploaded to taobao image space, just return')
        #     return
        additional_properties = json_loads(product.additional_properties)
        resource_root = additional_properties[RESOURCE_ROOT_KEY][1:]
        # handle new folder creation
        self.create_taobao_subfolders(new_folder_btn, f'{resource_root}/title_images')
        self.create_taobao_subfolders(new_folder_btn, f'{resource_root}/page_images')
        # handle product resource upload
        upload_btn2 = self.driver.find_element(By.ID, 'sucai-tu-upload')
        self.element_click(upload_btn2)
        return

    def create_taobao_subfolders(self, new_folder_btn, path):
        path_list = path.split('/')
        while True:
            self.element_click(new_folder_btn)
            dialog_wrappers = self.driver.find_elements(By.CLASS_NAME, 'next-dialog-inner-wrapper')
            root_section = None
            new_folder_section = None
            confirm_btn = None
            cancel_btn = None
            for dialog_wrapper in dialog_wrappers:
                sections = dialog_wrapper.find_elements(By.XPATH, './/section')
                if len(sections) == 0:
                    continue
                assert (len(sections)) == 2
                root_section, new_folder_section = sections
                confirm_btn = dialog_wrapper.find_element(By.XPATH, 'div/div[3]/button[1]')
                cancel_btn = dialog_wrapper.find_element(By.XPATH, 'div/div[3]/button[2]')
            path_span = root_section.find_element(By.XPATH, 'span[2]/span[1]')
            self.element_click(path_span)
            dropdown_divs = self.driver.find_elements(By.CLASS_NAME, 'next-tree-select-dropdown')
            assert (len(dropdown_divs)) == 1
            parent = dropdown_divs[0].find_element(By.XPATH, 'ul')
            idx = 0
            last_div = None
            while True:
                found = False
                for li in parent.find_elements(By.XPATH, 'li'):
                    if li.get_attribute('name') == path_list[idx]:
                        last_div = li.find_element(By.XPATH, 'div/div/div')
                        span = li.find_element(By.XPATH, 'div/span')
                        self.element_click(span)
                        children = li.find_elements(By.XPATH, 'ul')
                        if len(children) == 0:
                            found = False
                        else:
                            assert (len(children) == 1)
                            child = children[0]
                            found = True
                        idx += 1
                        break
                if found:
                    parent = child
                else:
                    self.element_click(last_div)
                    break
            if idx >= len(path_list):
                self.element_click(cancel_btn)
                break
            new_folder_input = new_folder_section.find_element(By.XPATH, 'span/input')
            new_folder_input.clear()
            new_folder_input.send_keys(path_list[idx])
            self.element_click(confirm_btn)

    def handle_rednote_resource_upload(self, product):
        pass

    def handle_taobao_on_shelf(self, product, shop_name, update_id):
        self.driver.get(TB_ONSHELF_PAGE)
        time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
        # product title
        title_span = self.driver.find_element(By.XPATH,
                                              '//*[@id="sell-field-title"]/div[2]/div[1]/div/div/span/span/span')
        assert (title_span.get_attribute('class') == 'input-wrap')
        title_input = title_span.find_element(By.XPATH, 'span/input')
        title_input.send_keys(product.product_title)
        # delivery promise
        self.scroll_window_to_element(self.driver.find_element(By.ID, 'sale-card'))
        delivery_div = self.driver.find_element(By.CLASS_NAME, 'sell-component-delivery-time')
        delivery_span = delivery_div.find_element(By.XPATH, 'span/span[1]/label/span')
        self.element_click(delivery_span)
        # price
        price_span = self.driver.find_element(By.XPATH, '//*[@id="sell-field-price"]/div[2]/div/div/span/span[1]')
        assert (price_span.get_attribute('class') == 'input-wrap')
        price_input = price_span.find_element(By.XPATH, 'span/input')
        price_input.send_keys(product.price / 100)
        # inventory
        inventory_span = self.driver.find_element(By.XPATH,
                                                  '//*[@id="sell-field-quantity"]/div[2]/div/div/span/span[1]')
        assert (inventory_span.get_attribute('class') == 'input-wrap')
        inventory_input = inventory_span.find_element(By.XPATH, 'span/input')
        for _ in range(CRAWL_OPERATION_TRY_COUNT):
            inventory_input.send_keys(Keys.BACK_SPACE)
            time.sleep(DRIVER_SIMPLE_OPS_WAIT_IN_SECONDS)
        inventory_input.send_keys(product.inventory)
        # transport
        self.scroll_window_to_element(self.driver.find_element(By.ID, 'struct-multiDiscountPromotion'))
        transport_label = self.driver.find_element(By.XPATH,
                                                   '//*[@id="sell-field-tbExtractWay"]/div[2]/div/div/div/span/div[1]/div[1]/div[1]/label')
        if transport_label.get_attribute('class').find('checked') == -1:
            self.element_click(transport_label)
            transport_template_span = self.driver.find_element(By.XPATH,
                                                               '//*[@id="sell-field-tbExtractWay"]/div[2]/div/div/div/span/div[1]/div[2]/div/div[1]/div[2]/span/span[1]/span[1]/span')
            self.element_click(transport_template_span)
            spans = self.driver.find_elements(By.CLASS_NAME, 'next-menu-item-text')
            for span in spans:
                if span.text == '系统模板-商家默认模板':
                    self.element_click(span)
                    break
        # inventory deduction
        self.scroll_window_to_element(self.driver.find_element(By.ID, 'struct-regionLimitSale'))
        inventory_deduction_span = self.driver.find_element(By.XPATH,
                                                            '//*[@id="sell-field-subStock"]/div[2]/div/div/span/span[2]')
        self.element_click(inventory_deduction_span)
        additional_properties = json_loads(product.additional_properties)
        resource_root = additional_properties[RESOURCE_ROOT_KEY][1:]
        # title images
        self.scroll_window_to_element(self.driver.find_element(By.ID, 'desc-card'))
        title_img_upload_div = self.driver.find_element(By.XPATH,
                                                        '//*[@id="struct-mainImagesGroup"]/div/div[1]/div/div/div/div/div')
        self.element_click(title_img_upload_div, CRAWL_PAGE_WAIT_IN_SECONDS)
        ti_iframe = self.driver.find_element(By.XPATH, '//*[@id="mainImagesGroup"]')
        self.switch_to_frame(ti_iframe)
        self.handle_taobao_select_images(f'{resource_root}/title_images')
        self.switch_to_default()
        # page images
        self.scroll_window_to_element(self.driver.find_element(By.ID, 'struct-guideMaterial'))
        page_img_upload_div = self.driver.find_element(By.XPATH, '//*[@id="panel_edit"]/div[1]/div[1]/div[1]')
        self.element_click(page_img_upload_div, CRAWL_PAGE_WAIT_IN_SECONDS)
        frame_div = self.driver.find_element(By.CLASS_NAME, 'media-img-plug')
        pi_iframe = frame_div.find_element(By.XPATH, 'iframe')
        self.switch_to_frame(pi_iframe)
        self.handle_taobao_select_images(f'{resource_root}/page_images', True)
        self.switch_to_default()
        # onshelf time
        self.scroll_window_to_element(self.driver.find_element(By.ID, 'post-sale-service-card'))
        onshelf_span = self.driver.find_element(By.XPATH,
                                                '//*[@id="sell-field-startTime"]/div[2]/div[2]/div/div/span/span[1]')
        self.element_click(onshelf_span)
        # submit onshelf
        submit_btn = self.driver.find_element(By.XPATH, '//*[@id="struct-buttons"]/button')
        self.element_click(submit_btn)
        self.logger.info(f'onshelf product_id={product.product_id} to taobao successfully')
        time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
        # 获取上架后的product_id
        shadow_id = self.parse_product_id_from_post_onshelf_link(self.driver.current_url)
        assert (shadow_id is not None)
        update_shadow_product_info(product.product_id, SHADOW_PRODUCT_STATUS_ONSHELF, update_id,
                                   self.handle_taobao_on_shelf.__name__, shadow_id=shadow_id)
        return True

    def handle_taobao_select_images(self, path, confirm=False):
        navbar_root = None
        divs = self.driver.find_elements(By.XPATH, '//div')
        for div in divs:
            cls_name = div.get_attribute('class')
            if cls_name is None:
                continue
            elif re.match(ONSHELF_TAOBAO_NAV_BAR_RE_EXP, cls_name):
                navbar_root = div
                break
        assert (navbar_root is not None)
        sort_span = self.driver.find_element(By.XPATH,
                                             '//*[@id="sucai-tu-selector-container"]/div[3]/div[2]/div[3]/div/div[1]/span[3]/span[1]/span[1]/span')
        self.element_click(sort_span)
        spans = self.driver.find_elements(By.CLASS_NAME, 'next-menu-item-text')
        for span in spans:
            if span.text == '文件名升序':
                self.element_click(span)
                break
        path_list = path.split('/')
        parent_li = navbar_root
        for token in path_list:
            child_li = None
            for child in parent_li.find_elements(By.XPATH, 'ul/li'):
                name_span = child.find_element(By.XPATH, 'div/div/div/div/span')
                if name_span.get_attribute('title') == token:
                    child_li = child
                    break
            assert (child_li is not None)
            token_div = child_li.find_element(By.XPATH, 'div')
            self.element_click(token_div)
            parent_li = child_li
        image_divs = self.driver.find_element(By.XPATH, '//*[@id="sucai_tu_selector_scrollMain"]').find_elements(
            By.XPATH, 'div')
        [self.element_click(image_div) for image_div in image_divs]
        if confirm:
            confirm_btn = self.driver.find_element(By.XPATH,
                                                   '//*[@id="sucai-tu-selector-container"]/div[4]/div[3]/button')
            self.element_click(confirm_btn)

    def handle_rednote_on_shelf(self, product, shop_name, update_id):
        self.driver.get(REDNOTE_ONSHELF_PAGE)
        time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
        # product title
        title_input = self.driver.find_element(By.XPATH, '//*[@id="anchor-cell-itemName"]/div[2]/div[1]/div/div/input')
        title_input.clear()
        title_input.send_keys(product.product_title)
        # title images
        additional_properties = json_loads(product.additional_properties)
        resource_root = additional_properties[RESOURCE_ROOT_KEY][1:]
        title_img_div = self.driver.find_element(By.CLASS_NAME, 'upload-list')
        self.element_click(title_img_div)
        self.handle_rednote_select_images(f'{resource_root}/title_images')
        # category
        recent_cat = self.driver.find_element(By.CLASS_NAME, 'recent')
        cat_spans = recent_cat.find_elements(By.XPATH, 'span')
        assert (len(cat_spans) >= 2)
        cat_spans[1].click()
        # next page
        action_div = self.driver.find_element(By.CLASS_NAME, 'action-bar')
        action_divs = action_div.find_elements(By.XPATH, 'div')
        assert (len(action_divs) == 2)
        next_btn = action_divs[1].find_element(By.XPATH, 'span/button')
        self.element_click(next_btn, sleep=CRAWL_PAGE_WAIT_IN_SECONDS)
        # main images
        main_img_div = self.driver.find_element(By.XPATH,
                                                '//*[@id="anchor-图文信息"]/div[2]/div[3]/div[1]/div[2]/div/div/div')
        self.element_click(main_img_div)
        self.handle_rednote_select_images(f'{resource_root}/page_images')
        # transport option
        transport_template_div = self.driver.find_element(By.XPATH,
                                                          '//*[@id="anchor-cell-物流模板"]/div[2]/div/div[2]/div[1]/div/div/div[1]/div[1]')
        assert (transport_template_div.text.find('虚拟商品无需发货') != -1)
        # delivery
        delivery_mode = self.driver.find_element(By.XPATH, '//*[@id="anchor-cell-发货时间"]/div[2]/div[1]/span/div[1]')
        self.element_click(delivery_mode)
        delivery_option = self.driver.find_element(By.XPATH,
                                                   '//*[@id="anchor-cell-发货时间"]/div[2]/div[2]/div[2]/span/div[2]/div')
        self.element_click(delivery_option)
        # price & inventory
        dtable_body = self.driver.find_elements(By.CLASS_NAME, 'd-table__body')
        assert (len(dtable_body) == 1)
        tds = dtable_body[0].find_elements(By.XPATH, 'tr/td')
        assert (len(tds) == 7)
        price_input = tds[2].find_element(By.XPATH, 'div/div/div/div[1]/input')
        price_input.clear()
        price_input.send_keys(product.price / 100)
        inventory_input = tds[4].find_element(By.XPATH, 'div/div/div/div[1]/input')
        inventory_input.clear()
        inventory_input.send_keys(product.inventory)
        # logistic template
        logistic_template = self.driver.find_element(By.XPATH,
                                                     '//*[@id="anchor-cell-shippingTemplateId"]/div[2]/div/div/div/div/div[1]/div[1]')
        assert (logistic_template.text.find('系统默认-非偏远地区包邮模版') != -1)
        # submit product
        submit_btn = self.driver.find_element(By.XPATH,
                                              '//*[@id="ark-app-itemark-mount-container"]/div[2]/div[2]/div/button[2]')
        time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)  # 不等待下面一行有概率执行不成功
        self.element_click(submit_btn)
        self.logger.info(f'onshelf product_id={product.product_id} to rednote successfully')
        time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
        # 后续通过任务更新rednote_id
        update_shadow_product_info(product.product_id, SHADOW_PRODUCT_STATUS_ONSHELF, update_id,
                                   self.handle_rednote_on_shelf.__name__)
        return True

    def handle_rednote_select_images(self, path):
        navbar_roots = self.driver.find_elements(By.CLASS_NAME, 'd-tree')
        assert (len(navbar_roots) == 1)
        divs = navbar_roots[0].find_elements(By.XPATH, 'div/div/div')
        assert (len(divs) == 2)
        navbar_root = divs[1]
        # sort by file name asc
        drawer_main_right_div = self.driver.find_element(By.CLASS_NAME, 'drawer-main-right')
        sort_div = drawer_main_right_div.find_element(By.XPATH, 'div[1]/div[1]/div[2]/div')
        self.element_click(sort_div)
        sort_options = self.driver.find_elements(By.CLASS_NAME, 'd-option-name')
        for sort_option in sort_options:
            span = sort_option.find_element(By.XPATH, 'span')
            if span.text.find('按文件名称升序') != -1:
                self.element_click(span)
        # locate image folder and find images
        path_list = path.split('/')
        parent_div = navbar_root
        for token in path_list:
            child_div = None
            for child in parent_div.find_elements(By.XPATH, 'div'):
                child_divs = child.find_elements(By.XPATH, 'div')
                assert (len(child_divs) == 2)
                spans = child_divs[0].find_elements(By.XPATH, 'span')
                assert (len(spans) == 2 or len(spans) == 3)
                name_span = spans[len(spans) - 1].find_element(By.XPATH, 'span/span')
                if name_span.text.find(token) != -1:
                    node = child_divs[1]
                    style = node.get_attribute('style')
                    if style.find('display: none;') != -1:
                        self.element_click(name_span)
                    child_div = node
                    break
            assert (child_div is not None)
            parent_div = child_div
        image_divs = self.driver.find_elements(By.CLASS_NAME, 'material-image-card')
        [self.element_click(image_div) for image_div in image_divs]
        # confirm button
        drawer_footers = self.driver.find_elements(By.CLASS_NAME, 'd-drawer-footer')
        assert (len(drawer_footers) == 1)
        footer_btns = drawer_footers[0].find_elements(By.XPATH, './/button')
        for btn in footer_btns:
            if btn.find_element(By.XPATH, 'div/span').text.find('确认') != -1:
                self.element_click(btn)
                break

    def handle_taobao_sync(self, product, shop_name, update_id):
        return True

    def handle_rednote_sync(self, product, shop_name, update_id):
        # 我们目前只同步rednote_id到shadow_product
        self.driver.get(REDNOTE_LIST_SHELF_PAGE)
        time.sleep(CRAWL_PAGE_WAIT_IN_SECONDS)
        header_wrapper_div = self.driver.find_element(By.CLASS_NAME, 'd-tabs-headers-wrapper')
        all_cat = header_wrapper_div.find_element(By.XPATH, 'div/div[1]/div/div[1]')
        self.element_click(all_cat)
        product_title_divs = self.driver.find_elements(By.CLASS_NAME, 'product-main')
        rednote_id = None
        for div in product_title_divs:
            title_span = div.find_element(By.XPATH, 'span')
            if title_span.text.find(product.product_title) != -1:
                id_wrapper_div = div.find_element(By.CLASS_NAME, 'ids-wrapper')
                id_span = id_wrapper_div.find_element(By.XPATH, 'div/span')
                idx = id_span.text.find('商品ID: ')
                if idx != -1:
                    rednote_id = id_span.text[idx + 6:]
                    break
        if rednote_id is not None:
            update_shadow_product_info(product.product_id, product.status, update_id, self.handle_rednote_sync.__name__,
                                       rednote_id=rednote_id)
            return True
        else:
            return False

    def product_manage_on_shelf(self, product_id, shop_name, platform, update_id):
        exist_sp = ShadowProductInfo.get(ShadowProductInfo.product_id == product_id)
        if platform == PRODUCT_MANAGE_PLATFORM_TAOBAO:
            self.handle_taobao_resource_upload(exist_sp)
            return self.handle_taobao_on_shelf(exist_sp, shop_name, update_id)
        elif platform == PRODUCT_MANAGE_PLATFORM_REDNOTE:
            self.handle_rednote_resource_upload(exist_sp)
            return self.handle_rednote_on_shelf(exist_sp, shop_name, update_id)

    def product_manage_online(self, ref_id, shop_name, platform, update_id):
        pass

    def product_manage_offline(self, ref_id, shop_name, platform, update_id):
        pass

    def product_manage_off_shelf(self, ref_id, shop_name, platform, update_id):
        pass

    def product_manage_sync(self, product_id, shop_name, platform, update_id):
        product = ShadowProductInfo.get(ShadowProductInfo.product_id == product_id)
        if platform == PRODUCT_MANAGE_PLATFORM_TAOBAO:
            return self.handle_taobao_sync(product, shop_name, update_id)
        elif platform == PRODUCT_MANAGE_PLATFORM_REDNOTE:
            return self.handle_rednote_sync(product, shop_name, update_id)

    def parse_product_id_from_post_onshelf_link(self, link):
        result = urlparse(link)
        qs = parse_qs(result.query)
        if 'primaryId' in qs and len(qs['primaryId']) == 1:
            return qs['primaryId'][0]
        else:
            return None

    def parse_product_id_from_product_link(self, link):
        result = urlparse(link)
        qs = parse_qs(result.query)
        if 'id' in qs and len(qs['id']) == 1:
            return qs['id'][0]
        else:
            return None

    def parse_product_id_from_item(self, item_id):
        assert (item_id is not None and item_id.rfind('_') != -1)
        product_id = item_id[item_id.rfind('_') + 1:]
        assert (len(product_id) > 0)
        return product_id

    def parse_sku_id_from_product_link(self, link):
        result = urlparse(link)
        qs = parse_qs(result.query)
        if 'skuId' in qs and len(qs['skuId']) == 1:
            return qs['skuId'][0]
        else:
            return None

    def parse_product_title(self, title):
        return title.replace('̷', '')

    def parse_sale_in_search(self, sale):
        assert (len(sale) > 3)
        desc = sale[-3:]
        if desc != '人付款' and desc != '人收货':
            self.logger.info(
                f'parse_sale_in_search get unexpected description, sale={sale}, desc={desc}, just return -1')
            return -1
        sale_num = sale[:-3]
        if sale_num[-1] == '+':
            sale_num = sale_num[:-1]
        if sale_num[-1] == '万':
            sale_num = sale_num[:-1] + '0000'
        return int(sale_num)

    def parse_sale_in_detail(self, sale):
        idx = sale.rfind('已售')
        if idx == -1:
            self.logger.info(f'parse_sale_in_detail get unexpected sale={sale}, return -1')
            return -1
        sale = sale[idx:]
        assert (len(sale) > 2)
        sale_num = sale[2:].strip()
        if sale_num[-1] == '+':
            sale_num = sale_num[:-1]
        if sale_num[-1] == '万':
            sale_num = sale_num[:-1] + '0000'
        return int(sale_num)

    def is_valid_image_link(self, link):
        if link[link.rfind('/') + 1:] == 's.gif':
            return False
        elif re.match(DETAIL_IMG_LINK_VALIDATE_RE_EXP, link):
            return True

    def parse_price_unit(self, unit):
        if unit == '¥':
            return 'CNY'
        return unit

    def parse_price(self, price):
        return int(float(price) * 100)
