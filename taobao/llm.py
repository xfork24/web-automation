# coding: utf-8
# !./bin/python

import time
from pydantic import constr, BaseModel
from json import dumps
from typing import List
from groq import Groq

from taobao.utils import get_logger
from taobao.models import ProductInfo

LLM_MODEL = 'deepseek-r1-distill-llama-70b'
GROQ_KEY = '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'
GROQ_TIMEOUT_IN_SECONDS = 60
MAX_KEYWORD_SIZE = 1
MAX_CATEGORY_SIZE = 1
KEYWORD_NAME_MAX_LENGTH = 32  # 这里给出足够的长度，因为有可能有长英文，大模型并不总会强制应用字符限制
CATEGORY_NAME_MAX_LENGTH = 10  # 这里强迫大模型缩短长度，虽然有时候并不会超常但大模型仍把keyword当category给出，就是这么怪

GroqClient = Groq(api_key=GROQ_KEY, timeout=GROQ_TIMEOUT_IN_SECONDS)


# Data model for LLM to generate
# 这里有几个问题：
# 1. 如果写keywords、categories，大模型会认不出来导致格式错误
# 2. 如果写 keyword_list: conlist(constr(min_length=1, max_length=KEYWORD_NAME_MAX_LENGTH), min_length=1,
#                           max_length=MAX_KEYWORD_SIZE)
#          category_list: conlist(constr(min_length=1, max_length=CATEGORY_NAME_MAX_LENGTH), min_length=1,
#                           max_length=MAX_CATEGORY_SIZE)
#    是可以的，但不能限制数组最大长度为1，大模型同样会导致格式错误
# 3. 如果写 keyword: constr(min_length=1, max_length=KEYWORD_NAME_MAX_LENGTH)
#          category: constr(min_length=1, max_length=CATEGORY_NAME_MAX_LENGTH)
#    也是可以的，但只能提供一个关键字和一个类别。
#
# 综合考虑，我们选择 #3 的写法
class ProductLLMInfo(BaseModel):
    id: str
    keyword: constr(min_length=1, max_length=KEYWORD_NAME_MAX_LENGTH)
    category: constr(min_length=1, max_length=CATEGORY_NAME_MAX_LENGTH)
    digital: bool


class ProductLLMInfos(BaseModel):
    infos: List[ProductLLMInfo]


# Data model for LLM to parse
class Product(BaseModel):
    id: str
    title: str


def parse_product_by_dsr1_70b(product: Product) -> ProductLLMInfo:
    logger = get_logger()
    request = [
        {
            "role": "system",
            "content": "You are an e-commerce manager that outputs product in JSON.\n"
            # Pass the json schema to the model. Pretty printing improves results. We will fill if remove indent=2.
                       f" The JSON object must use the schema: {dumps(ProductLLMInfo.model_json_schema(), indent=2)}.\n"
                       f" Keyword should be one word and its length should be less than {KEYWORD_NAME_MAX_LENGTH} characters.\n"
                       f" Category should be one word and its length should be less than {CATEGORY_NAME_MAX_LENGTH} characters.\n"
                       " Set digital to true if the product is a digital product and is not a physical product.\n"
                       " Both keyword and category should be in Chinese.\n",
        },
        {
            "role": "user",
            "content": f"id={product.id},title={product.title}\n",
        },
    ]
    logger.info(f'send request to LLM: \n{request}')
    chat_completion = GroqClient.chat.completions.create(
        # The prompt send to LLM.
        messages=request,

        # The language model which will generate the completion.
        model=LLM_MODEL,

        # Controls randomness: lowering results in less random completions.
        # As the temperature approaches zero, the model will become deterministic
        # and repetitive.
        temperature=0,

        # The maximum number of tokens to generate. Requests can use up to
        # 32,768 tokens shared between prompt and completion.
        max_completion_tokens=1024,

        # Streaming is not supported in JSON mode
        stream=False,

        # Enable JSON mode by setting the response format
        response_format={"type": "json_object"},
    )
    response = chat_completion.choices[0].message.content
    logger.info(f'get response from LLM: \n{response}')
    return ProductLLMInfo.model_validate_json(response)


def parse_product_list_by_dsr1_70b(products: List[Product]) -> ProductLLMInfos:
    logger = get_logger()
    request = [
        {
            "role": "system",
            "content": "You are an e-commerce manager that outputs products in JSON.\n"
            # Pass the json schema to the model. Pretty printing improves results. We will fill if remove indent=2.
                       f" The JSON object must use the schema: {dumps(ProductLLMInfos.model_json_schema(), indent=2)}.\n"
                       f" Keyword should be one word and its length should be less than {KEYWORD_NAME_MAX_LENGTH} characters.\n"
                       f" Category should be one word and its length should be less than {CATEGORY_NAME_MAX_LENGTH} characters.\n"
                       " Set digital to true if the product is a digital product and is not a physical product.\n"
                       " Both keyword and category should be in Chinese.\n",
        },
        {
            "role": "user",
            "content": ''.join([f'id=\"{product.id}\",title=\"{product.title}\"\n' for product in products]),
        },
    ]
    logger.info(f'send request to LLM: \n{request}')
    chat_completion = GroqClient.chat.completions.create(
        # The prompt send to LLM.
        messages=request,

        # The language model which will generate the completion.
        model=LLM_MODEL,

        # Controls randomness: lowering results in less random completions.
        # As the temperature approaches zero, the model will become deterministic
        # and repetitive.
        temperature=0,

        # The maximum number of tokens to generate. Requests can use up to
        # 32,768 tokens shared between prompt and completion.
        max_completion_tokens=32768,

        # Streaming is not supported in JSON mode
        stream=False,

        # Enable JSON mode by setting the response format
        response_format={"type": "json_object"},
    )
    response = chat_completion.choices[0].message.content
    logger.info(f'get response from LLM: \n{response}')
    return ProductLLMInfos.model_validate_json(response)


def update_product_llm_analysis_batch(products, update_id):
    logger = get_logger()
    response = parse_product_list_by_dsr1_70b(products)
    ts = int(time.time())
    for record in response.infos:
        llm_analysis = {
            'keyword': record.keyword,
            'category': record.category,
            'digital': record.digital,
        }
        logger.info(f'update product [{record.id}] with llm_analysis = {llm_analysis}')
        exist_ci = ProductInfo.get(ProductInfo.product_id == record.id)
        exist_ci.llm_analysis = llm_analysis
        exist_ci.update_id = update_id
        exist_ci.update_role = update_product_llm_analysis_batch.__name__
        exist_ci.update_ts = ts
        exist_ci.save()
