import json
import requests
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class NotifyScheduler(object):

    def __init__(self, event_consumers):
        self.event_consumers = event_consumers

    def emit(self, level, value):
        for consumer in self.event_consumers:
            consumer.emit(level, value)


class StdoutLogger(object):

    def __init__(self):
        pass

    def emit(self, level, msg):
        if level == "DEBUG":
            logging.debug(msg)
        if level == "INFO":
            logging.info(msg)
        if level == "WARNING":
            logging.warning(msg)
        if level == "ERROR":
            logging.error(msg)


class SlackNotifier(object):

    def __init__(self, url):
        self.url = url

    def emit(self, level, msg):
        slack_data = {'text': msg}
        requests.post(self.url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})

