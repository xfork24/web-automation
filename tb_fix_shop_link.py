# coding: utf-8
# !./bin/python
# 通过搜索页抓到的商铺链接有些格式为非法，我们通过搜索店铺功能手动fix这些商铺的链接

from taobao import *

LOG_FILE_NAME = './logs/tb_fix_shop_link.log'
UPDATE_TIME_PERIOD_IN_SECONDS = 86400
UPDATE_ID = 'tb_fix_shop_link'

if __name__ == '__main__':
    # scan commodity_info table in update_ts order and update commodities within time period
    # only commodities with empty llm_analysis be updated
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    logger = get_logger()
    start_ts = int(time.time()) - UPDATE_TIME_PERIOD_IN_SECONDS
    shops = ShopInfo.select().where(ShopInfo.update_ts > start_ts).order_by(ShopInfo.update_ts)
    login_taobao()
    logger.info('navigate to taobao shop search page')
    Driver.get(TAOBAO_SEARCH_PAGE)
    shop_tab_div = None
    divs = Driver.find_elements(By.XPATH, '//div')
    for div in divs:
        title = div.text.strip()
        if title == '店铺':
            shop_tab_div = div
            break
    assert (shop_tab_div is not None)
    shop_tab_div.click()
    for shop in shops:
        if not re.match(SHOP_LINK_RE_EXP, shop.link):
            qbox = Driver.find_element(By.ID, 'q')
            qbox.clear()
            qbox.send_keys(shop.name)
            qbox.send_keys(Keys.RETURN)
            logger.info('wait for shop search result for seconds')
            time.sleep(SEARCH_WAIT_IN_SECONDS)
            shop_wrapper_div = Driver.find_element(By.ID, 'srp_shopLayout_shopContentWrapper')
            assert (shop_wrapper_div is not None)
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
                shop_name = title_div.text.strip()
                if shop_name == shop.name:
                    shop_link = shop_a.get_attribute('href')
                    logger.info(f'update shop [{shop_name}] link to {shop_link}')
                    shop.link = shop_link
                    shop.save()
                    break
