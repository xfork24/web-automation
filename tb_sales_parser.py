# coding: utf-8
# !./bin/python
# 以一定规则扫描commodity_sales表，增加需要抓取的商品到detail_crawl_tasks，增加需要抓取的店铺到shop_crawl_tasks
#
# 目前使用的策略如下（请同步保持更新）：
# 1. 若某商品销售信息的最新更新时间为一周前，增加商品更新任务到detail_craw_tasks
#
#
#
#