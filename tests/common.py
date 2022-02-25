# coding:utf-8
import requests, json, urllib2, urllib


#url = "https://shalilai.cn/"
url = "http://animal.xhty.site/"


def post(params, url_suffix, headers={}):
    r = requests.post(url + url_suffix,
                      data=json.dumps(params), headers=headers, timeout=16, verify=False)
    return r


def get(params, url_suffix, headers={}):
    string = ""
    for k, v in params.items():
        string += k + "=" + str(v) + "&"
    r = requests.get(url + url_suffix + "?" + string[:-1],
                     data=json.dumps(params), headers=headers, timeout=30, verify=False)
    return r


def put(params, url_suffix, headers={}):
    r = requests.put(url + url_suffix, data=json.dumps(params),
                     headers=headers,
                     timeout=16)
    return r


def patch(params, url_suffix, headers={}):
    r = requests.patch(url + url_suffix, data=json.dumps(params),
                       headers=headers,
                       timeout=16)
    return r
