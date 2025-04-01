# coding: utf-8
# !./bin/python

class PriceOCRError(RuntimeError):
    pass


class NotStandardShop(RuntimeError):
    pass


class ShopLinkNotFound(RuntimeError):
    pass


class ShopNotFoundInSearch(RuntimeError):
    pass
