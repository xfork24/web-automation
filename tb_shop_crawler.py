# coding: utf-8
# !./bin/python
# 给定店铺链接，抓取店铺所有在售的商品，并更新如下表：commodity_info, commodity_sales, shop_info

from taobao import *

SHOP_LINK = 'https://1xzmdx4773dyohbj1ffdf4rhw6ucg6o.taobao.com/?ali_refid=a3_430620_1006:2355581875:H:FcjqB4KyR7kQZIEQJJbNXA%3D%3D:7331b94aae88bcc9013bedd6207b9050&ali_trackid=282_7331b94aae88bcc9013bedd6207b9050&spm=a21n57.1.1.1&mm_sceneid=1_0_7384168593_0'
LOG_FILE_NAME = './logs/tb_shop_crawler.log'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    craw_taobao_shop_page(SHOP_LINK)
