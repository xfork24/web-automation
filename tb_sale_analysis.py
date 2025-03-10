# coding: utf-8
# !./bin/python
# 定期以一定规则生成抓取任务，参考README.md

from taobao import *

LOG_FILE_NAME = './logs/tb_sales_analysis.log'
UPDATE_ID = 'tb_sale_analysis'
DEFAULT_SEARCH_KEYS = ['教程', '影视', '音乐', '素材', '自动发货']
DEFAULT_SEARCH_NUM_OF_PAGES = 10

if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    for search_key in DEFAULT_SEARCH_KEYS:
        analyze_and_add_search_crawl_tasks(search_key, DEFAULT_SEARCH_NUM_OF_PAGES, UPDATE_ID)
    # 暂时不执行店铺的统计抓取任务，因为最主要的，用户是通过搜索页面进入
    # analyze_and_add_shop_crawl_tasks(UPDATE_ID)
    analyze_and_add_detail_crawl_tasks(UPDATE_ID)
