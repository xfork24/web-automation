# encoding: utf-8
# !./bin/python

import logging
import sys
import time
from enum import Enum
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeDriverService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

LOGGING_FORMAT = '%(asctime)s %(message)s'
LOG_FILE_NAME = './logs/dh_crawler.log'
DH_SCRIPTS_WEBSITE = 'https://subslikescript.com/series/Desperate_Housewives-410975'
OUTPUT_DIR = './projects/output'


class WebDriverType(Enum):
    ChromDriver = 1
    SafariDriver = 2


def init_logger(log_format, level):
    logging.basicConfig(format=log_format, stream=sys.stdout, level=level)
    logging.info(
        f'logger inited with format={log_format}, file=sys.stdout, level={level}')


def get_logger(module_name=__name__):
    logger = logging.getLogger(module_name)
    return logger


class DHCrawler:
    def __init__(self, webdriver_type=WebDriverType.ChromDriver, headless=True):
        self.logger = get_logger()
        self.headless = headless
        self.driver = self.init_webdriver(webdriver_type, headless)

    def __del__(self):
        self.close_driver()

    def init_webdriver(self, webdriver_type, headless):
        driver = None
        if webdriver_type == WebDriverType.ChromDriver:
            # TBD: handle hiding selenium from chrome, remove 'chrome is controlled by automated test software'
            if sys.platform == 'win32':
                driver_service = ChromeDriverService('./chromedriver.exe')
            elif sys.platform == 'darwin':
                driver_service = ChromeDriverService('./chromedriver')
            else:
                raise RuntimeError('Unsupported platform')
            options = webdriver.ChromeOptions()
            options.add_experimental_option('excludeSwitches', ['load-extension', 'enable-automation'])
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--ignore-certificate-errors')
            if headless:
                options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(options=options, service=driver_service)
        elif webdriver_type == WebDriverType.SafariDriver:
            options = webdriver.SafariOptions()
            driver = webdriver.Safari(options=options)
        assert (driver is not None)
        self.logger.info(f'{webdriver_type.name} is initialized')
        return driver

    def close_driver(self):
        self.logger.info('quit webdriver ...')
        self.driver.quit()

    def crawl_dh_scripts(self):
        seasons = []
        self.driver.get(DH_SCRIPTS_WEBSITE)
        time.sleep(5)
        season_series_div = self.driver.find_element(By.CLASS_NAME, 'series_seasons')
        season_divs = season_series_div.find_elements(By.XPATH, 'div')
        for season_div in season_divs:
            episode_as = season_div.find_elements(By.XPATH, 'ul/li/a')
            episode_links = [{e.text: e.get_attribute('href')} for e in episode_as]
            seasons.append(episode_links)
        for i in range(len(seasons)):
            for j in range(len(seasons[i])):
                episode = seasons[i][j]
                self.logger.info(f'crawling season {i+1} episode {j+1}')
                for k, v in episode.items():
                    self.driver.get(v)
                    time.sleep(5)
                    full_script_div = self.driver.find_element(By.CLASS_NAME, 'full-script')
                    with open(f'{OUTPUT_DIR}/s{i+1:02}e{j+1:02}_{k}.txt', 'w') as f:
                        f.write(full_script_div.text)


def main():
    init_logger(LOGGING_FORMAT, logging.INFO)
    crawler = DHCrawler(headless=False)
    crawler.crawl_dh_scripts()


if __name__ == '__main__':
    main()
