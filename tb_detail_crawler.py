# coding: utf-8
# #!./bin/python

import re
import traceback
from json import dumps

from taobao import *

LOG_FILE_NAME = './logs/tb_detail_crawler.log'

TAOBAO_COMMODITY_LINK = 'https://item.taobao.com/item.htm?abbucket=9&id=858551205874&ns=1&pisk=gGUseeO0E-UefGB0xRfEOFvH0L0jC67yCIGYZSLwMV3tHkNuhA5cjVrIhJeIBF5GjmHbIVn0bxkZhqN0F6WPzaPgsq0OUT7rzBAgF4YvkjpqpBhjlfQ18M5Tsq0AhB8A4aNgeU3qghhx96GqghLYHcndJjHKMh3YHvnKwb-xk-3AO2hS6ChtDmKppjkpHhLx6e3KGjK9HFHAOWHnMqHYHcLu9FGF1vV16gxvjH_xM5HBkEU1ocM7un8Xllhtf4NtdWPURfisFDl991a7w5UoGrfJcxN4XRl3ha6IJPw_WDgfle0aNkesAl6XRDqLZrnQxTtuZ5e_20UOR6ebp7qoWPBD7AqY9rHUWs8jeuPoRX4VKFHbvoUZjqvOCXa_NrZf498rF1pBcBiklXMPO6tDm3Iu6ZkPUUXoXXcF361B4SmttXGhO6tDmchnTy1CO3zd.&priceTId=2150498517409260645331720e1a90&skuId=5838180867013&spm=a21n57.1.hoverItem.2&utparam=%7B%22aplus_abtest%22%3A%22a290208925248e6d2b601a269d3b98b2%22%7D&xxc=taobaoSearch'
COMMODITY_ID = '858551205874'
DETAIL_PAGE_WAIT_IN_SECONDS = 10
MAX_SKU_ITEMS_NUM = 5
SKU_ITEMS_RE_EXP = re.compile('^skuItem--')
INNER_SKU_ITEMS_RE_EXP = re.compile('^content--')
SKU_PRICE_RE_EXP = re.compile('^highlightPrice--')
SKU_TITLE_IMGS_RE_EXP = re.compile('^thumbnailsWrap--')
SKU_MAIN_IMGS_RE_EXP = re.compile('^descV8-container')


def craw_taobao_detail_page(commodity_link, commodity_id=None):
    logger = get_logger()
    login_taobao()
    logger.info('navigate to commodity link')
    Driver.get(commodity_link)
    time.sleep(DETAIL_PAGE_WAIT_IN_SECONDS)
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
        "offers": offers
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
        for value_item in combo:
            span = value_item.find_element(By.XPATH, 'span')
            offer.append(span.text)
            value_item.click()
        price_spans = sku_price_div.find_elements(By.XPATH, 'span')
        assert (len(price_spans) >= 2)
        offer.append(parse_price_unit(price_spans[0].text))
        offer.append(parse_price(price_spans[1].text))
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


if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    craw_taobao_detail_page(TAOBAO_COMMODITY_LINK, COMMODITY_ID)
