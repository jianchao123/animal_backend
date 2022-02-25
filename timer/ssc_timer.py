# coding:utf-8
import requests
from bs4 import BeautifulSoup
import datetime
import json
import db
import conf


class SscTimer(object):

    def __init__(self, logger):
        self.logger = logger

    @db.transaction(is_commit=True)
    def cq_ssc_number(self):
        """新浪开彩网的数据 (5s执行一次)"""
        mysql_db = db.MysqlDbUtil(self.mysql_cur)
        from datetime import datetime
        from datetime import timedelta
        cur_time = datetime.now()
        sql = "SELECT `ssc_period_no`,`open_time` FROM `shi_shi_cai` " \
              "ORDER BY `ssc_period_no` DESC LIMIT 1"
        ssc_data = mysql_db.get(sql)
        open_time = ssc_data[1]
        if open_time + timedelta(minutes=20) < cur_time:

            url = "https://kjh.55128.cn/history_chongqingssc.aspx"
            res = requests.get(url)
            soup = BeautifulSoup(res.content, "html.parser")
            kaij_title = soup.find_all("span", class_="kaij-qs")
            kaij_cartoon = soup.find_all("div", class_="kaij-cartoon")
            if kaij_title and kaij_cartoon:
                self.logger.error(kaij_title)
                current_period_no = "20" + kaij_title[0].string
                spans = kaij_cartoon[0].find_all("span")
                number = ""
                for row in spans:
                    number += row.string

                result = mysql_db.get(sql.format(current_period_no))
                if not result:
                    insert_ssc_data = {
                        "number": number,
                        "ssc_period_no": current_period_no,
                        "open_time": 'now()',
                        "next_open_time": "null"
                    }
                    mysql_db.insert(insert_ssc_data, table_name='shi_shi_cai')
