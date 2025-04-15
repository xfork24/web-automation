# coding: utf-8
# !./bin/python
# 定期以一定规则生成抓取任务，参考README.md

from core import *

LOG_FILE_NAME = './logs/tb_sales_analysis.log'
UPDATE_ID = 'tb_sale_analysis'
DEFAULT_SEARCH_KEYS = [('教程', 3),
                       ('影视', 3),
                       ('音乐', 3),
                       ('素材', 3),
                       ('电视剧', 3),
                       ('电影', 3),
                       ('自动发货', 3),
                       ('美剧', 3),
                       ('英剧', 3),
                       ('日剧', 3), ]

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)

    for search_key, num_of_pages in DEFAULT_SEARCH_KEYS:
        analyze_and_add_search_crawl_tasks(search_key, num_of_pages, UPDATE_ID)

    # 暂时不执行店铺的统计抓取任务，因为最主要的，用户是通过搜索页面进入
    # analyze_and_add_shop_crawl_tasks(UPDATE_ID)

    # 商品统计最好等所有商品修复任务都做完之后再进行
    # analyze_and_add_detail_crawl_tasks(UPDATE_ID)

    # 分析热门商品
    # analyze_and_add_hot_products(UPDATE_ID)

    # 下载商品素材，应该放到所有任务都执行完毕的最后再执行
    # download_hot_product_resources()

    close_db()
