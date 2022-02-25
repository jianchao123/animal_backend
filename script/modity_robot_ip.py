# coding:utf-8


import db
from db import transaction
import requests
import random
from bs4 import BeautifulSoup
from gevent import monkey; monkey.patch_all()
import gevent

# l = ["电信", "长城", "联通", "移动", "鹏博士", "铁通", "教育网"]

operator = ["联通", "铁通", "电信", "移动", "鹏博士", "教育网"]


def get_city_by_ip(ip):
    """根据Ip获取城市"""
    url = "http://www.ip138.com/ips1388.asp?ip={}&action=2"
    res = requests.get(url.format(ip))
    soup = BeautifulSoup(res.content, "html.parser")
    table = soup.find_all('table')[2]
    tr = table.find_all('tr')[2]
    li_s = tr.find_all('li')
    address = li_s[0].text.split(u"：")[-1]
    return address


def get_city_by_ip_1(s, ip):
    """根据Ip获取城市"""
    url = "http://www.ip138.com/ips1388.asp?ip={}&action=2"
    try:
        res = requests.get(url.format(ip))
    except:
        return
    soup = BeautifulSoup(res.content, "html.parser")
    table = soup.find_all('table')[2]
    tr = table.find_all('tr')[2]
    li_s = tr.find_all('li')
    address = li_s[0].text.split(u"：")[-1]
    array = address.split(" ")
    array = [x.strip() for x in array if x.strip() != '']

    if len(array) == 2 and len(array[1]) < 6:
        print s + " " + address

def rinse():
    """1.清洗"""
    d = []
    i = 0
    with open('./ip_address', 'r') as fd:
        ip = fd.readline()
        while ip:
            i += 1
            ip_address = ip.split("/")[0]
            city_address = get_city_by_ip(ip_address)
            arr = city_address.split(" ")
            arr = [x.strip() for x in arr if x.strip() != '']
            if len(arr) == 2 and "/" not in arr[1]:
                k = arr[1].encode("utf-8")
                if k in operator:
                    d.append(ip_address)
            print i
            if i % 100 == 0:
                print d
            ip = fd.readline()


def ip_generator():
    """2.IP生成器"""
    index = 0
    url = []
    with open('./ip_address', 'r') as fd:
        ip = fd.readline()
        while ip:
            ip = ip.strip('\n')
            arr = ip.split(".")
            s = arr[0] + "." + arr[1] + "."
            if arr[2] == '0':
                s += str(random.randint(1, 255)) + "."
            else:
                s += arr[2] + "."
            if arr[3] == '0':
                s += str(random.randint(1, 255))
            else:
                s += arr[3]
            try:
                url.append(gevent.spawn(get_city_by_ip_1, s, ip))
            except:
                ip = fd.readline()
                continue

            ip = fd.readline()
    gevent.joinall(url)


def sql_generator():
    """3.生成sql"""

    with open('./ip_address', 'r') as fd:
        ip = fd.readline()
        while ip:
            sql = "INSERT INTO `robot_ip` (`ip`, `address`) VALUES ('{}', '{}');"
            array = ip.split(" ")
            array = [x.strip() for x in array if x.strip() != '']
            ip = array[0]
            address = array[1] + " " + array[2]
            sql = sql.format(ip, address)
            print sql
            ip = fd.readline()


@transaction(is_commit=True)
def modify_robot_ip_and_address(mysql_cursor):
    mysql_db = db.MysqlDbUtil(mysql_cursor)
    result = mysql_db.query("SELECT `userprofilebasic_ptr_id` "
                            "FROM `game_player` WHERE `is_robot`=1")
    index = 4
    for row in result:
        r = mysql_db.get("SELECT `ip`,`address` FROM "
                         "`robot_ip` WHERE `id`={}".format(index))
        data = {
            "userprofilebasic_ptr_id": row[0],
            "ip": r[0],
            "ip_address": r[1]
        }
        print data
        mysql_db.update(data, table_name="game_player")
        index += 1


if __name__ == "__main__":
    modify_robot_ip_and_address()