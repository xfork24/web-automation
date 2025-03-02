# coding: utf-8
# !./bin/python

import time
from enum import Enum

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeDriverService
from selenium.common.exceptions import NoSuchElementException

from taobao.utils import *

TAOBAO_LOGIN_PAGE = 'https://login.taobao.com/member/login.jhtml'
TB_PERSONAL_HOMEPAGE_TITLE_NAME = '我的淘宝'
TB_HOMEPAGE_TITLE_NAME = '淘宝'
LOGIN_CHECK_INTERVAL_IN_SECONDS = 10


class WebDriverType(Enum):
    ChromDriver = 1
    SafariDriver = 2


def init_webdriver(webdriver_type: WebDriverType):
    logger = get_logger()
    logger.info('start init %s webdriver ...' % webdriver_type)
    driver = None
    if webdriver_type == WebDriverType.ChromDriver:
        driver_service = ChromeDriverService('/Users/hengliu/Path/chromedriver')
        driver = webdriver.Chrome(service=driver_service)
    elif webdriver_type == WebDriverType.SafariDriver:
        options = webdriver.SafariOptions()
        driver = webdriver.Safari(options=options)
    logger.info('%s webdriver initialized' % webdriver_type)
    return driver


def login_taobao():
    logger = get_logger()
    logger.info('forward to taobao login page')
    Driver.get(TAOBAO_LOGIN_PAGE)
    while True:
        try:
            logger.info('check taobao login status...')
            Driver.find_element(By.ID, 'login')
            time.sleep(LOGIN_CHECK_INTERVAL_IN_SECONDS)
        except NoSuchElementException:
            logger.info('can not find login form, you should already logged in and in taobao/personal homepage')
            break
    logger.info('check if we are in taobao/personal homepage')
    while True:
        if Driver.title == TB_PERSONAL_HOMEPAGE_TITLE_NAME or Driver.title == TB_HOMEPAGE_TITLE_NAME:
            logger.info('we are already in taobao/personal homepage, now perform following crawling')
            break
        else:
            logger.info(
                'we are not in taobao/personal homepage, finish authentication and navigate to taobao/personal homepage...')
            time.sleep(LOGIN_CHECK_INTERVAL_IN_SECONDS)


Driver = init_webdriver(WebDriverType.ChromDriver)
