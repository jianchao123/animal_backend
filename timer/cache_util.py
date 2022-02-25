# coding:utf-8
import redis
import json
import time
from db import rds_conn, rds_pool
from utils import DecimalEncoder

# 自旋锁专用连接
lock_conn = redis.Redis(connection_pool=rds_pool)


class CacheUtil(object):
    PERIOD_STATUS_WAIT_B = "period:status:waitb"
    PERIOD_STATUS_COUNTDOWN = "period:status:countdown"

    PERIOD_TARGET_AMOUNTS_KEY = "period:target:amounts:{}"
    PERIOD_COUNTDOWN = "period:countdown:milli:{}"
    TODAY_COUNT = "today:period:count:{}"
    DIALOG_KEY = "dialog:{}"
    OPEN_PRIZE_COUNT = "open:prize:count"
    CALCULATE_RESULT = "calculate:result:milli:{}"
    PERIOD_MIRRORING = "period:mirroring:{}"
    PERIOD_MIRRORING_COUNTDOWN = "period:mirroring:countdown:{}"
    FIFTY_LEN_KEY = "fifty:participate:time"
    HOME_PAGE = "CACHE:HOMEPAGE:{}"
    BANNER = "CACHE:BANNER"
    TREND_MAP = "CACHE:TREND:MAP:{}"
    HONOR_LIST = "CACHE:HONOR:LIST:{}"
    PERIOD_UNDERWAY_ID = "PERIOD:UNDERWAY:ID"
    CLEAR_PERIOD_KEY = "CLEAR:PERIOD:KEY"
    HEADLINE = "HEADLINE"
    ROBOT_PHONE_SET = "robot_phone_set"

    @staticmethod
    def set_clear_period_key(period_pk):
        rds_conn.set(CacheUtil.CLEAR_PERIOD_KEY, period_pk)

    @staticmethod
    def get_clear_period_key():
        return rds_conn.get(CacheUtil.CLEAR_PERIOD_KEY)

    @staticmethod
    def cache_underway_period_id(data):
        """保存进行中的周期id"""
        rds_conn.set(CacheUtil.PERIOD_UNDERWAY_ID, data)

    @staticmethod
    def cache_honor_list(period_id, data):
        """缓存荣誉榜"""
        rds_conn.set(CacheUtil.HONOR_LIST.format(period_id),
                     json.dumps(data))

    @staticmethod
    def get_cache_honor_list(period_id):
        """获取缓存-荣誉榜"""
        d = rds_conn.get(CacheUtil.HONOR_LIST.format(period_id))
        return json.loads(d) if d else None

    @staticmethod
    def cache_trend_map(commodity_id, data):
        """缓存某个商品的走势图"""
        rds_conn.set(CacheUtil.TREND_MAP.format(commodity_id),
                     json.dumps(data))

    @staticmethod
    def get_cache_trend_map(commodity_id):
        """获取缓存-走势图"""
        d = rds_conn.get(CacheUtil.TREND_MAP.format(commodity_id))
        return json.loads(d) if d else None

    @staticmethod
    def cache_banner(data):
        rds_conn.set(CacheUtil.BANNER,
                     json.dumps(data, cls=DecimalEncoder))

    @staticmethod
    def get_cache_homepage(key):
        d = rds_conn.get(CacheUtil.HOME_PAGE.format(key))
        return json.loads(d) if d else None

    @staticmethod
    def today_count(today_str):
        """每日周期计数"""
        return rds_conn.incr(CacheUtil.TODAY_COUNT.format(today_str))

    @staticmethod
    def get_period_amounts(period_id):
        """获取周期目标量"""
        return rds_conn.get(
            CacheUtil.PERIOD_TARGET_AMOUNTS_KEY.format(period_id))

    @staticmethod
    def add_period_to_set(key, period_id):
        """添加周期到集合"""
        rds_conn.sadd(key, period_id)

    @staticmethod
    def get_period_set_by(key):
        """根据key获取周期集合"""
        return rds_conn.smembers(key)

    @staticmethod
    def rem_period_from_set(key, period_id):
        """从集合移除周期id"""
        rds_conn.srem(key, period_id)

    @staticmethod
    def set_period_amounts(period_id, amounts):
        """设置周期目标量"""
        rds_conn.set(
            CacheUtil.PERIOD_TARGET_AMOUNTS_KEY.format(period_id), amounts)

    @staticmethod
    def get_pttl_expire(period_id):
        """获取周期倒计时毫秒数"""
        return rds_conn.pttl(CacheUtil.PERIOD_COUNTDOWN.format(period_id))

    @staticmethod
    def dialog_push(player_pk, data):
        """push一个弹窗"""
        rds_conn.lpush(CacheUtil.DIALOG_KEY.format(player_pk),
                       json.dumps(data))

    @staticmethod
    def get_headline():
        """get一组头条"""
        return rds_conn.get(CacheUtil.HEADLINE)

    @staticmethod
    def set_headline(msg):
        """set一个头条"""
        rds_conn.set(CacheUtil.HEADLINE, msg)

    @staticmethod
    def incr_open_prize_count():
        """递增开奖计数"""
        rds_conn.incr(CacheUtil.OPEN_PRIZE_COUNT)

    @staticmethod
    def get_open_prize_count():
        """获取开奖计数"""
        return rds_conn.get(CacheUtil.OPEN_PRIZE_COUNT)

    @staticmethod
    def set_period_mirroring(period_pk, data):
        """保存周期镜像"""
        rds_conn.set(CacheUtil.PERIOD_MIRRORING.format(period_pk),
                     json.dumps(data, cls=DecimalEncoder))

        name = CacheUtil.PERIOD_MIRRORING_COUNTDOWN.format(period_pk)
        rds_conn.set(name, 1)
        rds_conn.pexpire(name, 3000)

    @staticmethod
    def get_pttl_mirroring(period_pk):
        """获取镜像可以开奖的倒计时毫秒"""
        return rds_conn.pttl(
            CacheUtil.PERIOD_MIRRORING_COUNTDOWN.format(period_pk))

    @staticmethod
    def get_period_mirroring(period_pk):
        """获取周期镜像数据"""
        d = rds_conn.get(CacheUtil.PERIOD_MIRRORING.format(period_pk))
        return json.loads(d) if d else None

    @staticmethod
    def delete_period_mirroring(period_pk):
        """删除镜像key"""
        rds_conn.delete(CacheUtil.PERIOD_MIRRORING.format(period_pk))

    @staticmethod
    def get_pttl_calculate_result(period_id):
        """获取周期计算结果倒计时毫秒数"""
        return rds_conn.pttl(CacheUtil.CALCULATE_RESULT.format(period_id))

    @staticmethod
    def keys_by(key):
        return rds_conn.keys(key)

    @staticmethod
    def set_nx(key, v):
        return rds_conn.setnx(key, v)

    @staticmethod
    def del_key(key):
        rds_conn.delete(key)

    @staticmethod
    def set_calculate_result(period_id, millisecond):
        """设置周期计算结果倒计时毫秒数"""
        rds_conn.set(CacheUtil.CALCULATE_RESULT.format(period_id), 1)
        rds_conn.pexpire(CacheUtil.CALCULATE_RESULT.format(period_id),
                         millisecond)

    @staticmethod
    def set_pttl_expire(period_id, millisecond):
        """设置周期开奖倒计时毫秒数"""
        rds_conn.set(CacheUtil.PERIOD_COUNTDOWN.format(period_id), 1)
        rds_conn.pexpire(CacheUtil.PERIOD_COUNTDOWN.format(period_id),
                         millisecond)

    @staticmethod
    def del_period_key(period_id):
        return rds_conn.delete(
            CacheUtil.PERIOD_TARGET_AMOUNTS_KEY.format(period_id))

    @staticmethod
    def get_fifty_time():
        return rds_conn.lrange(CacheUtil.FIFTY_LEN_KEY, 0, 49)

    # 手动晾单
    @staticmethod
    def robot_phone_is_member(pk):
        return rds_conn.sismember(CacheUtil.ROBOT_PHONE_SET, pk)

    @staticmethod
    def del_robot_phone_set():
        rds_conn.delete(CacheUtil.ROBOT_PHONE_SET)


class RedisLock(object):
    PRE_REDIS_KEY = "shopping:lock:process"

    def __init__(self, key):
        self.rdcon = lock_conn
        self._lock = 0
        self.lock_key = key

    def get_lock(self, timeout=10):
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
        lock_key += ":{}".format(kwargs)
        instance = RedisLock(lock_key)

        instance.get_lock()
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            raise ex
        finally:
            instance.release()

    return __deco


def lock_funclock(func):
    def __deco(*args, **kwargs):
        lock_key = "shopping:lock:nonblock:{}".format(func.__name__)
        instance = RedisLock(lock_key)

        instance.get_lock()
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            raise ex
        finally:
            instance.release()

    return __deco
