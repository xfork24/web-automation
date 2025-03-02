# coding: utf-8
# !./bin/python

import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json

DING_AUTOMATION_BOT_WEBHOOK = 'https://oapi.dingtalk.com/robot/send?access_token=9e8fabbebf505b7f53cc0d2bd9bb54305d72d8be7ba6eff58a6d57b9433b26cc'
DING_AUTOMATION_BOT_SIGN = 'SEC5a9263ddaedfb9609b078c0b6dfef5bc9f86abad1096279ffc2f14067b4e2696'
DING_ALARM_BOT_WEBHOOK = 'https://oapi.dingtalk.com/robot/send?access_token=d64fa59a2a0ebe5385ac6df134100e951ca579a67ec38becb149ef81838432cb'
DING_ALARM_BOT_SIGN = 'SEC0e99e945359e334c2c21b7a6c7ce50ddc4401b533e2521c0a4f6702393e456c4'


def generate_sign(timestamp, secret):
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return sign


def download_image(url, folder_path, filename):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    image_path = os.path.join(folder_path, filename)

    response = requests.get(url)
    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"图片下载成功: {image_path}")
        return image_path
    else:
        print(f"图片下载失败: {url}")
        return None


def send_image_to_dingtalk(image_url, robot_webhook, secret):
    timestamp = str(round(time.time() * 1000))
    sign = generate_sign(timestamp, secret)
    webhook_url = f"{robot_webhook}&timestamp={timestamp}&sign={sign}"

    # 构建消息内容
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "60s图片",
            "text": f"![image]({image_url})"
        }
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200 and response.json().get('errcode') == 0:
        print("图片发送成功")
    else:
        print("图片发送失败")
        print(response.text)


# 主函数
def main():
    local_server_image_url = 'https://g-search3.alicdn.com/img/bao/uploaded/i4/i2/2218539584188/O1CN01GEcBDZ1go9l6iD1b6_!!2218539584188.png_580x580q90.jpg'  # 提供一个支持https的稳定网站，要网站能访问到图片地址

    robot_webhook = 'https://oapi.dingtalk.com/robot/send?access_token=d64fa59a2a0ebe5385ac6df134100e951ca579a67ec38becb149ef81838432cb'
    secret = 'SEC0e99e945359e334c2c21b7a6c7ce50ddc4401b533e2521c0a4f6702393e456c4'

    # webhook里是机器人地址，secret是加签
    send_image_to_dingtalk(local_server_image_url, robot_webhook, secret)


if __name__ == '__main__':
    main()
