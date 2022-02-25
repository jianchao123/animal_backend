# coding:utf-8
import traceback
from functools import wraps
from decimal import Decimal
import MySQLdb
import redis
from DBUtils.PooledDB import PooledDB
from redis import StrictRedis, ConnectionPool
import conf
import utils

# logger
logger = utils.get_logger(conf.log_path)

# mysql
mysql_pool = PooledDB(MySQLdb, 5, **conf.mysql_conf)

# redis
rds_pool = ConnectionPool(**conf.redis_conf)
rds_conn = redis.Redis(connection_pool=rds_pool)


# 事务装饰器
def transaction(is_commit=False):
    def _transaction(func):
        @wraps(func)
        def __transaction(*args, **kwargs):
            try:
                mysql_conn = mysql_pool.connection()
                mysql_cur = mysql_conn.cursor()
                result = func(mysql_cur, *args, **kwargs)
                if is_commit:
                    mysql_conn.commit()
                return result
            except:
                if is_commit and mysql_conn:
                    mysql_conn.rollback()
                # 记录日志
                logger.error(traceback.format_exc())
            finally:
                if mysql_conn and mysql_cur:
                    mysql_cur.close()
                    mysql_conn.close()

        return __transaction
    return _transaction


class MysqlDbUtil(object):

    def __init__(self, mysql_cur):
        self.mysql_cur = mysql_cur

    def get(self, sql):
        self.mysql_cur.execute(sql)
        result = self.mysql_cur.fetchone()
        return result

    def query(self, sql):
        self.mysql_cur.execute(sql)
        result = self.mysql_cur.fetchall()
        return result

    def insert(self, data, table_name=None):
        keys = ""
        values = ""
        time_list = ["now()", "NOW()", "current_timestamp",
                     "CURRENT_TIMESTAMP", "null"]
        for k, v in data.iteritems():
            keys += k + ","
            if isinstance(v, (int, float, Decimal, long)) or \
                            v in time_list or "str_to_date" in v:
                values += str(v) + ","
            else:
                values += "'" + str(v) + "'" + ","

        keys = keys[:-1]
        values = values[:-1]

        sql = "insert into {}({}) values({})".format(table_name, keys, values)
        self.mysql_cur.execute(sql)

    def update(self, data, table_name=None):
        sql = "UPDATE `{}` SET ".format(table_name)
        pk_field = 'id'
        for k, v in data.iteritems():
            if k != 'id' and '_ptr_id' not in k:
                if isinstance(v, (int, long, float, Decimal)):
                    sql += k + "=" + str(v) + ","
                elif v in ["now()", "NOW()", "current_timestamp",
                           "CURRENT_TIMESTAMP"]:
                    sql += k + "=" + v + ","
                else:
                    sql += k + "=" + "'" + v + "'" + ","
            if '_ptr_id' in k:
                pk_field = k
        sql = sql[:-1] + " WHERE `{}` = {}".format(pk_field, data[pk_field])
        self.mysql_cur.execute(sql)
