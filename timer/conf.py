# coding:utf-8
import os
env_dist = os.environ
if env_dist.get('SHOPPING_ENV') == "DEV":
    log_path = "log/logger"
    mysql_passwd = "qv8KnAwraUnla10e"
    url = ""
if env_dist.get('SHOPPING_ENV') == "TEST":
    log_path = "data/logs/shopping/timer.log"
    mysql_passwd = "qv8KnAwraUnla10e"
    url = "http://animal.xhty.site/"
if env_dist.get('SHOPPING_ENV') == "PRO":
    log_path = "data/logs/shopping/timer.log"
    mysql_passwd = "qv8KnAwraUnla10e"
    url = "http://139.196.113.98/"

redis_conf = dict(host="127.0.0.1", port=6379, db=0, decode_responses=True)
mysql_conf = dict(host="127.0.0.1",
                  db="shopping", port=3306, user="root",
                  passwd=mysql_passwd, charset="utf8")

# 极光推送
NOTIFY_APP_KEY = "58af5b3e94e5207901182af8"
NOTIFY_SCRECT_KEY = "c6325c4516cd82f6f7bc60b0"

# 爱亿网API
AIYI_KEY = "te86252e6badf4b17k"