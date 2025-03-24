# coding: utf-8
# !./bin/python

class PriceOCRError(RuntimeError):
    pass


class NotStandardShop(RuntimeError):
    pass


class ShopSkuNumExceeded(RuntimeError):
    pass
