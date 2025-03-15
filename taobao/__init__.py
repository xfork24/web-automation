# coding: utf-8
# #!./bin/python

from taobao.config import *
from taobao.exceptions import *
from taobao.utils import *
from taobao.models import *
from taobao.notify import *
from taobao.llm import *
from taobao.crawler import *
from taobao.analysis import *


def cleanup():
    logger = get_logger()
    logger.info('close webdriver ...')
    Driver.close()
    logger.info('close DB instance ...')
    DB.close()
    logger.info('close LLM client ...')
    GroqClient.close()
