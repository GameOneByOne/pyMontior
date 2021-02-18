import requests
import logging
import json
logger = logging.getLogger("error")

class MonitorReminder:
    def __init__(self):
        pass
    
    def send_mail(self):
        pass

    def send_message(self, template):
        try:
            # request_body = json.dumps(param, ensure_ascii=False).encode('utf-8')
            # request_header = {'content-type': 'application/json;charset=utf8'}
            logger.info("[ Monitor Reminder ] A Message Is To Send... {}".format(template))
            # r = requests.post'http://127.0.0.1:7021/messagecare/create', request_body, headers=request_header)
            # r.raise_for_status()
        except:
            pass
