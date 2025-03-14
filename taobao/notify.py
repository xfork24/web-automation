# coding: utf-8
# !./bin/python

import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
from json import dumps
from pydantic import BaseModel
from pydantic.json import pydantic_encoder
from typing import List
from taobao.utils import get_logger

DING_AUTOMATION_BOT_WEBHOOK = 'https://oapi.dingtalk.com/robot/send?access_token=9e8fabbebf505b7f53cc0d2bd9bb54305d72d8be7ba6eff58a6d57b9433b26cc'
DING_AUTOMATION_BOT_SIGN = 'SEC5a9263ddaedfb9609b078c0b6dfef5bc9f86abad1096279ffc2f14067b4e2696'
DING_ALARM_BOT_WEBHOOK = 'https://oapi.dingtalk.com/robot/send?access_token=d64fa59a2a0ebe5385ac6df134100e951ca579a67ec38becb149ef81838432cb'
DING_ALARM_BOT_SIGN = 'SEC0e99e945359e334c2c21b7a6c7ce50ddc4401b533e2521c0a4f6702393e456c4'

ACTION_CARD_BTN_VERTICAL = 0
ACTION_CARD_BTN_HORIZONTAL = 1


class ActionCardButton(BaseModel):
    title: str
    actionURL: str


class FreeCardLink(BaseModel):
    title: str
    messageURL: str
    picURL: str


def generate_sign(timestamp, secret):
    secret_enc = secret.encode('utf-8')
    string_to_sign = f'{timestamp}\n{secret}'.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return sign


def get_webhook_url(webhook, sign):
    timestamp = round(time.time() * 1000)
    return f"{webhook}&timestamp={timestamp}&sign={generate_sign(timestamp, sign)}"


class DingBot:
    def __init__(self, webhook, sign):
        self.webhook = webhook
        self.sign = sign

    def send_text(self, content, at_all=True, at_uids=None, at_mobiles=None):
        logger = get_logger()
        webhook_url = get_webhook_url(self.webhook, self.sign)
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            },
            "at": {
                "isAtAll": at_all,
                "atUserIds": [] if at_uids is None else at_uids,
                "atMobiles": [] if at_mobiles is None else at_mobiles
            },
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(webhook_url, headers=headers, data=dumps(data))
        logger.info(f'DingBot send_text request to {webhook_url} with headers={headers} and data={data}')
        assert (response.status_code == 200 and response.json().get('errcode') == 0)

    def send_link(self, title, text, image_url, message_url):
        logger = get_logger()
        webhook_url = get_webhook_url(self.webhook, self.sign)
        data = {
            "msgtype": "link",
            "link": {
                "title": title,
                "text": text,
                "picUrl": image_url,
                "messageUrl": message_url
            },
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(webhook_url, headers=headers, data=dumps(data))
        logger.info(f'DingBot send_link request to {webhook_url} with headers={headers} and data={data}')
        assert (response.status_code == 200 and response.json().get('errcode') == 0)

    def send_markdown(self, title, markdown, at_all=True, at_uids=None, at_mobiles=None):
        logger = get_logger()
        webhook_url = get_webhook_url(self.webhook, self.sign)
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": markdown
            },
            "at": {
                "isAtAll": at_all,
                "atUserIds": [] if at_uids is None else at_uids,
                "atMobiles": [] if at_mobiles is None else at_mobiles
            },
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(webhook_url, headers=headers, data=dumps(data))
        logger.info(f'DingBot send_markdown request to {webhook_url} with headers={headers} and data={data}')
        assert (response.status_code == 200 and response.json().get('errcode') == 0)

    def send_action_card_single(self, title, text_markdown, single_title, single_url,
                                btn_orientation=ACTION_CARD_BTN_HORIZONTAL):
        logger = get_logger()
        webhook_url = get_webhook_url(self.webhook, self.sign)
        data = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": text_markdown,
                "singleTitle": single_title,
                "singleURL": single_url,
                "btnOrientation": btn_orientation,
            },
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(webhook_url, headers=headers, data=dumps(data))
        logger.info(f'DingBot send_action_card_single request to {webhook_url} with headers={headers} and data={data}')
        assert (response.status_code == 200 and response.json().get('errcode') == 0)

    def send_action_card_separate(self, title, text_markdown, buttons: List[ActionCardButton],
                                  btn_orientation=ACTION_CARD_BTN_HORIZONTAL):
        logger = get_logger()
        webhook_url = get_webhook_url(self.webhook, self.sign)
        data = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": text_markdown,
                "btns": dumps(buttons, default=pydantic_encoder),
                "btnOrientation": btn_orientation,
            },
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(webhook_url, headers=headers, data=dumps(data))
        logger.info(f'DingBot send_action_card_separate request to {webhook_url} with headers={headers} and data={data}')
        assert (response.status_code == 200 and response.json().get('errcode') == 0)

    def send_free_card(self, links: List[FreeCardLink]):
        logger = get_logger()
        webhook_url = get_webhook_url(self.webhook, self.sign)
        data = {
            "msgtype": "feedCard",
            "feedCard": {
                "links": dumps(links, default=pydantic_encoder)
            }
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(webhook_url, headers=headers, data=dumps(data))
        logger.info(f'DingBot send_free_card request to {webhook_url} with headers={headers} and data={data}')
        assert (response.status_code == 200 and response.json().get('errcode') == 0)


AutomationDingBot = DingBot(DING_AUTOMATION_BOT_WEBHOOK, DING_AUTOMATION_BOT_SIGN)
AlarmDingBot = DingBot(DING_ALARM_BOT_WEBHOOK, DING_ALARM_BOT_SIGN)
