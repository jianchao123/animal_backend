# coding:utf-8
import jpush
from django.conf import settings


class CPushHelper(object):
    def __init__(self):
        self.__jpush = None

    def create(self, app_key, master_secret):
        self.__jpush = jpush.JPush(app_key, master_secret)
        self.__jpush.set_logging("DEBUG")

    def push_to_device(self, msg_data, registration_ids, title=None):
        """
        推送到设备(自定义消息)
        :param msg_data: {"not_read_news_count": 10}
        :param registration_ids:
        :param title:
        :return:
        """
        push = self.__jpush.create_push()
        push.platform = jpush.all_
        push.audience = jpush.audience(
            jpush.registration_id(*registration_ids)
        )
        push.message = jpush.message(msg_content=msg_data,
                                     title=title,
                                     content_type=None,
                                     extras=None)
        try:
            response = push.send()
            return response
        except jpush.common.Unauthorized as e:
            raise e.args
        except jpush.common.APIConnectionException as e:
            raise e.args
        except jpush.common.JPushFailure as e:
            raise e.args
        except jpush.common.APIRequestException as e:
            raise e.args

    def push_to_user(self, msg_data, alert_data='', title=None, *user_list):
        """
        调用方式
        data = {
            "period_no": "1232141",
            "period_id": 101,
            "luck_player_id": 24
        }
        push_obj.push_to_user(json.dumps(data), u'恭喜中奖', commodity_name, uid)
        """

        push = self.__jpush.create_push()
        push.platform = jpush.all_
        push.audience = jpush.audience(
            jpush.alias(*user_list)
        )
        androidmsg = {
            "alert": alert_data,
            "title": title
        }
        iosmsg = {
            "alert": alert_data,
        }
        push.notification = jpush.notification(alert=alert_data,
                                               android=androidmsg, ios=iosmsg)
        push.message = jpush.message(msg_content=msg_data,
                                     title=title,
                                     content_type=None,
                                     extras=None)
        try:
            response = push.send()
            return response
        except jpush.common.Unauthorized as e:
            raise e
        except jpush.common.APIConnectionException as e:
            raise e
        except jpush.common.JPushFailure as e:
            raise e
        except jpush.common.APIRequestException as e:
            raise e

    def push_to_all(self, msg_data, alert_data=''):
        push = self.__jpush.create_push()
        push.platform = jpush.all_
        push.audience = jpush.all_
        push.notification = jpush.notification(alert=alert_data)
        push.message = jpush.message(msg_content=msg_data,
                                     title=None,
                                     content_type=None,
                                     extras=None)
        try:
            response = push.send()
            return response
        except jpush.common.Unauthorized as e:
            raise e
        except jpush.common.APIConnectionException as e:
            raise e
        except jpush.common.JPushFailure as e:
            raise e


jpush_obj = CPushHelper(settings.NOTIFY_APP_KEY, settings.NOTIFY_SCRECT_KEY)
