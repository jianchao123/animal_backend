# coding:utf-8

import requests
import json
index = 35088
end = 63296
while index < end:
    params = {"period_id": index}
    try:
        r = requests.post("http://animal.xhty.site/user/deleterobotperiod/",
                          data=json.dumps(params), headers=
                          {"Content-Type": "application/json"}, timeout=10)
    except:
        pass
    print index
    index += 1