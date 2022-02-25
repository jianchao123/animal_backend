# coding:utf-8
import redis, time, json
import datetime as datetime_m
from datetime import datetime
from django.conf import settings
from utils import DecimalEncoder
import AppError
import logging
logger = logging.getLogger(__name__)


pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT,
                            db=settings.REDIS_DB,
                            decode_responses=True)

rds = redis.Redis(connection_pool=pool)


class CacheUtil(object):
    SIGN_UP_CODE = "user:signup:code:{}"
    SIGN_IN_CODE = "user:signin:code:{}"
    PERIOD_TARGET_AMOUNTS_KEY = "period:target:amounts:{}"
    # 传递给celery的数据key(分配token,增加/更新订单记录,增加参与记录,增加消费记录,更新周期)
    PERIOD_QUEUE = "period:queue:{}"
    PERIOD_COUNTDOWN = "period:countdown:milli:{}"
    CACHE_PERIOD_DATA = "cache:period:data:{}"
    DIALOG_KEY = "dialog:{}"
    USER_MSG_LIMIT = "user:msg:limit:{}:{}"
    PWD_ERR_COUNT = "pwd:err:count:{}"
    SMS_INTERVAL = "sms:interval:{}"
    USER_CHOICE_PAY_CHANNEL = "user:choice:pay_channel:{}"
    CALCULATE_RESULT = "calculate:result:milli:{}"
    FIFTY_LEN_KEY = "fifty:participate:time"
    HEADLINE = "HEADLINE"
    ROBOT_PHONE_SET = "robot_phone_set"

    # 手动晾单使用
    @staticmethod
    def push_robot_phone_to_set(pk):
        rds.sadd(CacheUtil.ROBOT_PHONE_SET, pk)

    # 登陆注册
    @staticmethod
    def set_signup_code(phone, code):
        """设置注册验证码"""
        today = datetime_m.date.today().strftime('%Y%m%d')
        msg_limit_key = CacheUtil.USER_MSG_LIMIT.format(today, phone)
        count = rds.get(msg_limit_key)
        if count and int(count) > 10:
            return False
        rds.set(CacheUtil.SIGN_UP_CODE.format(phone), code)
        rds.expire(CacheUtil.SIGN_UP_CODE.format(phone), 300)

        rds.incr(msg_limit_key)
        rds.expire(msg_limit_key, 86400)
        return True

    @staticmethod
    def get_signup_code(phone):
        """获取注册验证码"""
        return rds.get(CacheUtil.SIGN_UP_CODE.format(phone))

    @staticmethod
    def set_signin_code(phone, code):
        """设置登陆码"""
        now = datetime.now()
        hours = now.hour
        minutes = now.minute
        seconds = now.second

        today = datetime_m.date.today().strftime('%Y%m%d')
        msg_limit_key = CacheUtil.USER_MSG_LIMIT.format(today, phone)
        count = rds.get(msg_limit_key)
        print count
        if count:
            if int(count) > 10:
                return False
        else:
            rds.set(msg_limit_key)
            rds.expire(msg_limit_key, (24-hours-1)*3600 + (60-minutes-1)*60 + seconds)
        sign_in_code_key = CacheUtil.SIGN_IN_CODE.format(phone)
        rds.set(sign_in_code_key, code)
        rds.expire(sign_in_code_key, 300)

        rds.incr(msg_limit_key)
        return True

    @staticmethod
    def get_signin_code(phone):
        """获取登陆码"""
        return rds.get(CacheUtil.SIGN_IN_CODE.format(phone))

    @staticmethod
    def push_period_queue(period_id, data):
        rds.rpush(CacheUtil.PERIOD_QUEUE.format(period_id), json.dumps(data))

    @staticmethod
    def pop_period_queue(period_id):
        return json.loads(rds.lpop(CacheUtil.PERIOD_QUEUE.format(period_id)))

    @staticmethod
    def set_period_amounts(period_id, amounts):
        rds.set(CacheUtil.PERIOD_TARGET_AMOUNTS_KEY.format(period_id), amounts)

    @staticmethod
    def get_period_amounts(period_id):
        return rds.get(CacheUtil.PERIOD_TARGET_AMOUNTS_KEY.format(period_id))

    @staticmethod
    def decr_period_amounts(period_id, amounts):
        return rds.decr(CacheUtil.PERIOD_TARGET_AMOUNTS_KEY.format(period_id),
                        amounts)

    @staticmethod
    def incr_period_amounts(period_id, amounts):
        return rds.incr(CacheUtil.PERIOD_TARGET_AMOUNTS_KEY.format(period_id),
                        amounts)

    @staticmethod
    def del_period_key(period_id):
        return rds.delete(
            CacheUtil.PERIOD_TARGET_AMOUNTS_KEY.format(period_id))

    @staticmethod
    def get_pttl_expire(period_id):
        return rds.pttl(CacheUtil.PERIOD_COUNTDOWN.format(period_id))

    @staticmethod
    def set_pttl_expire(period_id, millisecond):
        """设置周期开奖倒计时毫秒数"""
        rds.set(CacheUtil.PERIOD_COUNTDOWN.format(period_id), 1)
        rds.pexpire(CacheUtil.PERIOD_COUNTDOWN.format(period_id), millisecond)

    @staticmethod
    def set_calculate_result(period_id, millisecond):
        """设置周期计算结果倒计时毫秒数"""
        rds.set(CacheUtil.CALCULATE_RESULT.format(period_id), 1)
        rds.pexpire(CacheUtil.CALCULATE_RESULT.format(period_id), millisecond)

    @staticmethod
    def get_countdown_keys():
        return rds.keys("period:countdown:milli:*")

    @staticmethod
    def set_period_data(period_pk, data):
        """设置周期数据"""
        rds.set(CacheUtil.CACHE_PERIOD_DATA.format(period_pk),
                json.dumps(data))
        rds.pexpire(CacheUtil.CACHE_PERIOD_DATA.format(period_pk), 15000)

    @staticmethod
    def get_period_data(period_pk):
        """获取周期数据"""
        return rds.get(CacheUtil.CACHE_PERIOD_DATA.format(period_pk))

    @staticmethod
    def dialog_pop(player_pk):
        """pop一个弹窗"""
        result = rds.lpop(CacheUtil.DIALOG_KEY.format(player_pk))
        if result:
            return json.loads(result)
        else:
            return {}

    @staticmethod
    def get_headline():
        return rds.get(CacheUtil.HEADLINE)

    @staticmethod
    def get_pwd_err_count(phone):
        return rds.get(CacheUtil.PWD_ERR_COUNT.format(phone))

    @staticmethod
    def set_pwd_err_count(phone):
        rds.set(CacheUtil.PWD_ERR_COUNT.format(phone), 1)
        rds.pexpire(CacheUtil.PWD_ERR_COUNT.format(phone), 300000)

    @staticmethod
    def incr_pwd_err_count(phone):
        rds.incr(CacheUtil.PWD_ERR_COUNT.format(phone))

    @staticmethod
    def set_sms_interval(phone):
        rds.set(CacheUtil.SMS_INTERVAL.format(phone), 1)
        rds.pexpire(CacheUtil.SMS_INTERVAL.format(phone), 60000)

    @staticmethod
    def get_sms_interval(phone):
        return rds.get(CacheUtil.SMS_INTERVAL.format(phone))

    @staticmethod
    def set_user_choice_pay_channel(player_id, pay_channel_id):
        rds.set(CacheUtil.USER_CHOICE_PAY_CHANNEL.format(
            player_id), pay_channel_id)
        rds.pexpire(CacheUtil.USER_CHOICE_PAY_CHANNEL.format(
            player_id), 300000)

    @staticmethod
    def get_user_choice_pay_channel(player_id):
        return rds.get(CacheUtil.USER_CHOICE_PAY_CHANNEL.format(player_id))

    @staticmethod
    def get_pttl_calculate_result(period_id):
        """获取周期计算结果倒计时毫秒数"""
        return rds.pttl(CacheUtil.CALCULATE_RESULT.format(period_id))

    @staticmethod
    def get_fifty_len():
        """获取50条时间key的长度"""
        return rds.llen(CacheUtil.FIFTY_LEN_KEY)

    @staticmethod
    def right_push_fifty(l):
        """"""
        rds.lpush(CacheUtil.FIFTY_LEN_KEY, json.dumps(l))
        rds.ltrim(CacheUtil.FIFTY_LEN_KEY, 0, 49)

    @staticmethod
    def get_fifty_time():
        return rds.lrange(CacheUtil.FIFTY_LEN_KEY, 0, 49)

    @staticmethod
    def set_control_flag(key):
        rds.set(key, 1)

    @staticmethod
    def get_control_flag(key):
        return rds.get(key)

    @staticmethod
    def delete_control_flag(key):
        rds.delete(key)


class RedisLock(object):
    PRE_REDIS_KEY = "shopping:lock:process"

    def __init__(self, key):
        self.rdcon = rds
        self._lock = 0
        self.lock_key = key

    def get_lock(self, timeout=20):
        while self._lock != 1:
            timestamp = time.time() + timeout + 1
            self._lock = self.rdcon.setnx(self.lock_key, timestamp)
            if self._lock == 1 or (time.time() > self.rdcon.get(self.lock_key)
                                   and time.time() > self.rdcon.getset(
                    self.lock_key, timestamp)):
                break
            else:
                time.sleep(0.3)

    def release(self):
        if time.time() < self.rdcon.get(self.lock_key):
            self.rdcon.delete(self.lock_key)


def lock_nonblock(func):
    def __deco(*args, **kwargs):
        lock_key = "shopping:lock:nonblock:{}".format(func.__name__)
        s = ''
        for k, v in kwargs.items():
            s += (str(k) + "=" + str(v))
        lock_key += ":{}".format(s)
        instance = RedisLock(lock_key)

        instance.get_lock()
        try:
            return func(*args, **kwargs)
        finally:
            instance.release()

    return __deco


def lock_instance(func):
    def __deco(self, *args, **kwargs):
        lock_key = "shopping:lock:instance:{}".format(func.__name__)
        s = ''
        for k, v in kwargs.items():
            s += (str(k) + "=" + str(v))
        lock_key += ":{}".format(s)
        instance = RedisLock(lock_key)

        instance.get_lock()
        try:
            return func(self, *args, **kwargs)
        finally:
            instance.release()
    return __deco


def lock_pay_func(func):
    def __deco(*args, **kwargs):
        lock_key = "pay:lock:nonblock:{}".format(func.__name__)
        s = ''
        for k, v in kwargs.items():
            s += (str(k) + "=" + str(v))
        lock_key += ":{}".format(s)
        instance = RedisLock(lock_key)

        instance.get_lock()
        try:
            return func(*args, **kwargs)
        except AppError.AppErrorBase as ex:
            raise ex
        except Exception as ex:
            raise ex
        finally:
            instance.release()

    return __deco


class Cache(object):
    """缓存"""

    HOME_PAGE = "CACHE:HOMEPAGE:{}"
    HONOR_LIST = "CACHE:HONOR:LIST:{}"
    TREND_MAP = "CACHE:TREND:MAP:{}"
    BANNER = "CACHE:BANNER"
    PERIOD_UNDERWAY_ID = "PERIOD:UNDERWAY:ID"

    @staticmethod
    def get_cache_underway_period_id():
        """保存进行中的周期id"""
        return Cache.get(Cache.PERIOD_UNDERWAY_ID)

    @staticmethod
    def set(key, value, expire=5):
        rds.set(key, value)
        rds.expire(key, expire)

    @staticmethod
    def get(key):
        return rds.get(key)

    @staticmethod
    def cache_homepage(key, data):
        """缓存主页"""

        Cache.set(Cache.HOME_PAGE.format(key),
                  json.dumps(data, cls=DecimalEncoder), expire=30)

    @staticmethod
    def get_cache_homepage(key):
        d = Cache.get(Cache.HOME_PAGE.format(key))
        return json.loads(d) if d else None

    @staticmethod
    def cache_honor_list(period_id, data):
        """缓存荣誉榜"""
        Cache.set(Cache.HONOR_LIST.format(period_id),
                  json.dumps(data), expire=30)

    @staticmethod
    def get_cache_honor_list(period_id):
        """获取缓存-荣誉榜"""
        d = Cache.get(Cache.HONOR_LIST.format(period_id))
        return json.loads(d) if d else None

    @staticmethod
    def cache_trend_map(commodity_id, data):
        """缓存某个商品的走势图"""
        Cache.set(Cache.TREND_MAP.format(commodity_id),
                  json.dumps(data), expire=300)

    @staticmethod
    def get_cache_trend_map(commodity_id):
        """获取缓存-走势图"""
        d = Cache.get(Cache.TREND_MAP.format(commodity_id))
        return json.loads(d) if d else None

    @staticmethod
    def get_cache_banner():
        d = Cache.get(Cache.BANNER)
        return json.loads(d) if d else None

    @staticmethod
    def cache_banner(data):
        Cache.set(Cache.BANNER, json.dumps(data), expire=60*60)