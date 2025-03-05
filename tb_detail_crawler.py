# coding: utf-8
# #!./bin/python
# 抓取某个单一商品（提供商品链接和可选ID）的Detail页面信息，更新commodity_info表里的对应商品的如下字段：title_imgs, page_imgs, details
# 若商品不存在，则创建新的commodity_info表记录，并写入商品信息

from taobao import *

LOG_FILE_NAME = './logs/tb_detail_crawler.log'

TAOBAO_COMMODITY_LINK = 'https://detail.tmall.com/item.htm?abbucket=9&id=723766500159&ns=1&pisk=gikjeCsi-VHy708iZqxzVtbl_w2su3JFlGZtxcBVX-eYWbin5r-Mi-l75437kt-Di5Uso-FigPz45RiiR38eLpommR2v8eJULgjmRJXOMlQNezE0CopXUQ-xmR295gW9TpimJ9ZqUsET23Zab1CxW5nJek48XsetWzF8vk5TBVe9V8EQDiEY65CRylzRklUAH_C8YlUTDoCvV0UuXRUtWShTttZyczmXDBfOi_1yxLZNBOH7c7OryzhZGhraGribPN9oFvVbJmU5CecYdbU8AYLGuPDS2xEiyLWbC0EsR-hWytgsDX0gvqp5koGxADPSIeB_qb30aoGWX_UxvreYPAxGIrhqXAPsHeIakx0qFWDGlUzZT0kYN2LPFVVsMXexCe9R4OXURnQ51gNhCuaeV31Gs6dnDdze89Y3Muqba3t5kfbhBOwvV31MLSEu4YtWV6kR.&priceTId=2147836e17409929448704382e19d8&skuId=5833307459166&spm=a21n57.1.hoverItem.12&utparam=%7B%22aplus_abtest%22%3A%22798fdaa0ce6cba74fc7b357536a4068d%22%7D&xxc=taobaoSearch'

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    craw_taobao_detail_page(TAOBAO_COMMODITY_LINK)
