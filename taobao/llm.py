# coding: utf-8
# !./bin/python

from pydantic import constr, conlist, BaseModel
from json import dumps
from typing import List
from groq import Groq

from taobao.utils import get_logger

LLM_MODEL = 'deepseek-r1-distill-llama-70b'
GROQ_KEY = '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'
KEYWORD_NAME_MAX_LENGTH = 10
CATEGORY_NAME_MAX_LENGTH = 10

GroqClient = Groq(api_key=GROQ_KEY)


# Data model for LLM to generate
class ProductInfo(BaseModel):
    id: str
    keyword: constr(max_length=KEYWORD_NAME_MAX_LENGTH)
    category: constr(max_length=CATEGORY_NAME_MAX_LENGTH)
    digital: bool


class ProductInfoList(BaseModel):
    infos: List[ProductInfo]


# Data model for LLM to parse
class Product(BaseModel):
    id: str
    title: str


def parse_product_by_dsr1_70b(product: Product) -> ProductInfo:
    logger = get_logger()
    request = [
        {
            "role": "system",
            "content": f"分析按行分隔的商品信息，输出为{dumps(ProductInfo.model_json_schema())}格式的JSON\n",
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
    return ProductInfo.model_validate_json(response)


def parse_product_list_by_dsr1_70b(products: List[Product]) -> ProductInfoList:
    logger = get_logger()
    request = [
        {
            "role": "system",
            "content": f"分析按行分隔的商品信息，输出为{dumps(ProductInfoList.model_json_schema())}格式的JSON\n",
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
    return ProductInfoList.model_validate_json(response)
