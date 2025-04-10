# coding: utf-8
# !./bin/python
# 测试程序

from core import *
from api import *
from flask_cors import CORS
import signal

LOG_FILE_NAME = './logs/api_server.log'


def signal_handler(sig, frame):
    logger = get_logger()
    logger.info(f'signal={sig} captured with frame={frame}, will clean up resources and quit.')
    close_db()
    sys.exit(0)


def add_cors_headers(response: Flask.response_class) -> Flask.response_class:
    response.headers.set("Access-Control-Allow-Origin", "*")
    response.headers.set("Access-Control-Allow-Headers", "*")
    response.headers.set("Access-Control-Allow-Methods", "*")
    return response


if __name__ == '__main__':
    init_logger(LOGGING_FORMAT, LOG_FILE_NAME, logging.INFO, DEBUG)
    signal.signal(signal.SIGINT, signal_handler)
    api.after_request(add_cors_headers)
    CORS(api, resources=r'/*')
    api.run(port=8000, debug=True, use_reloader=False)
