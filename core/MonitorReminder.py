import requests
import logging
import json
logger = logging.getLogger()

class MonitorReminder:
    def __init__(self):
        pass
    
    def send_mail(self):
        logger.info("[ Monitor Reminder ] A Email Is To Send...")

    def send_message(self):
        logger.info("[ Monitor Reminder ] A Message Is To Send...")
