# coding:utf-8
import os
env_dist = os.environ
redis_conf = dict(host="127.0.0.1", port=6379, db=0, decode_responses=True)

if env_dist.get('SHOPPING_ENV') == "DEV":
    log_path = "log/logger"
if env_dist.get('SHOPPING_ENV') == "TEST":
    log_path = "/data/log/shopping/script.log"
    mysql_pwd = "qv8KnAwraUnla10e"
if env_dist.get('SHOPPING_ENV') == "PRO":
    log_path = "/data/log/shopping/script.log"
    mysql_pwd = "qv8KnAwraUnla10e"
mysql_conf = dict(host="127.0.0.1",
                  db="shopping", port=3306, user="root",
                  passwd=mysql_pwd, charset="utf8")
