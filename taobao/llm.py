# coding: utf-8
# !./bin/python

from pydantic import constr, conlist, BaseModel
from json import dumps
from typing import List
from groq import Groq

from taobao.utils import get_logger

LLM_MODEL = 'deepseek-r1-distill-llama-70b'
GROQ_KEY = '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'

GroqClient = Groq(api_key=GROQ_KEY)


# Data model for LLM to generate
class ProductInfo(BaseModel):
    id: str
    keywords: conlist(constr(min_length=1, max_length=5), min_length=1, max_length=3)
    categories: conlist(constr(min_length=1, max_length=7), min_length=1, max_length=2)
    virtual_product: bool


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
            "content": "You are an e-commerce manager that process product id and title and output product information in JSON\n"
                       f"The JSON object must use this schema: {dumps(ProductInfo.model_json_schema())}"
                       "Number of keywords must be between 1 and 3, with each no more than 5 characters"
                       "Number of categories must be between 1 and 2, with each no more than 7 characters"
                       "Both keyword and category should be sorted by importance from high to low",
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
            "content": "You are an e-commerce manager that process product id and title and output product information in JSON\n"
                       "Each input line contains one product with its id and title"
                       f" The returned JSON object must use the schema: {dumps(ProductInfoList.model_json_schema())}"
                       "Number of keywords must be between 1 and 3, with each no more than 5 characters"
                       "Number of categories must be between 1 and 2, with each no more than 7 characters"
                       "Both keyword and category should be sorted by importance from high to low",
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
