# coding:utf-8
import copy
import os
import logging
from datetime import datetime, timedelta
from django.conf import settings
# 全局字典
LOGGERS = {}

# LOG 等级
LOG_LEVEL_INFO = 0
LOG_LEVEL_WARNING = 1
LOG_LEVEL_ERROR = 2

# LOG状态
LOG_STATUS_BEGIN = 1
LOG_STATUS_END = 2
LOG_STATUS_SUCCESS = 3
LOG_STATUS_FAIL = 4


def close_log_fs(logger_name):
    # 先移出全局字典
    log = LOGGERS.pop(logger_name, None)
    if log:
        for handler in log.handlers:
            handler.close()


def close_all_log_fs():
    for key in LOGGERS.keys():
        close_log_fs(key)


class Loggers(object):
    """ 格式化log """

    status_ls = {
        1: "begin",
        2: "end",
        3: "success",
        4: "fail"
    }

    def __init__(self, log_name):
        """ log_name : logger名
        """
        self.log_name = log_name
        self.base_log_dir = settings.BASE_LOG_PATH
        self.logger = self._loginit()

    def _loginit(self):

        _date = datetime.now().strftime("%Y%m%d")
        _month = datetime.now().strftime("%Y%m")

        # 创建年月的目录
        log_dir = os.path.join(self.base_log_dir, _month)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        key = "%s_log_%s" % (self.log_name, _date)

        if key in LOGGERS:
            return LOGGERS[key]
        else:
            _logger = logging.getLogger(key)
            _logger.setLevel(logging.INFO)
            _logger.propagate = False
            log_path = os.path.join(log_dir, key)
            if not _logger.handlers:
                fh = logging.FileHandler(log_path)
                fh.setLevel(logging.INFO)
                formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
                fh.setFormatter(formatter)
                _logger.addHandler(fh)
                LOGGERS[key] = _logger

            # 删除昨日在LOGGERS 中的对象
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            _key = "%s_log_%s" % (self.log_name, yesterday)
            if _key in LOGGERS:
                close_log_fs(_key)

            return _logger

    def write(self, cmd, data_dict=None, status=0, level=0, exc_info=None):
        """
        这里不会修改data的内容
        cmd : log行为标识
        data_dict : 记录的数据,以dict方式
        status : 行为状态类型(例如 3 => 成功)
        level : log级别(例如 1 => warning)
        """
        # 深复制
        data = data_dict
        data_ls = []
        if not data:
            return

        for k, v in data.iteritems():
            key_value = "%s=%s" % (k, v)
            data_ls.append(key_value)

        if status > 0:
            info = "%s:%s | %s" % (cmd, self.status_ls[status], "&".join(data_ls))
        else:
            info = "%s | %s" % (cmd, "&".join(data_ls))

        if level == 1:
            self.logger.warning(info)
        elif level == 2:
            self.logger.error(info, exc_info=exc_info)
        else:
            self.logger.info(info)
