# coding:utf-8
import logging
import jpush
import json
import decimal


def get_logger(log_path):
    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


class PushHelper(object):

    def __init__(self, app_key, master_secret):
        self.__jpush = jpush.JPush(app_key, master_secret)
        self.__jpush.set_logging("DEBUG")

    def push_to_user(self, msg_data, android_alert_data,
                     ios_alert_data, title, *user_list):

        push = self.__jpush.create_push()
        push.platform = jpush.all_
        push.audience = jpush.audience(
            jpush.alias(*user_list)
        )
        androidmsg = {
            "alert": android_alert_data,
            "title": title
        }
        iosmsg = {
            "alert": ios_alert_data,
        }

        push.notification = jpush.notification(alert=ios_alert_data,
                                               android=androidmsg, ios=iosmsg)
        push.message = jpush.message(msg_content=msg_data,
                                     title=title,
                                     content_type=None,
                                     extras=None)
        # push.options = {"apns_production": False}
        response = push.send()
        return response
        # try:
        #     response = push.send()
        #     return response
        # except jpush.common.Unauthorized as e:
        #     raise e
        # except jpush.common.APIConnectionException as e:
        #     raise e
        # except jpush.common.JPushFailure as e:
        #     raise e
        # except jpush.common.APIRequestException as e:
        #     raise e


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)