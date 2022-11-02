import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse

timestamp = str(round(time.time() * 1000))
secret = 'this is secret'
secret_enc = secret.encode('utf-8')
string_to_sign = '{}\n{}'.format(timestamp, secret)
string_to_sign_enc = string_to_sign.encode('utf-8')
hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
url = 'https://oapi.dingtalk.com/robot/send?' \
      'access_token=b42708a3a0019ff3ee9be9ed4a531514b4a4ace966a02b82c8a292b41a3a37fc'

headers = {'Content-Type': 'application/json;charset=utf-8'}

data = {
    "msgtype": "markdown",
    "markdown": {
        "title": "通知",
        "text": "#### 济南 @17852170964 \n"
                "> <font color='Blue' >**下方链接**</font>\n" +
                "> ![screenshot]"
                "(https://img2.baidu.com/it/u=1322269692,187770437&fm=253&fmt=auto&app=138&f=JPEG?w=667&h=500)\n" +
                "> ###### 10月1号发布 [BMP测试后台链接](http://10.168.20.188:9000/) \n"
    },
    "at": {
        "atMobiles": [
            "17852170964"
        ],
        "isAtAll": False
    }
}
r = requests.post(url=url, headers=headers, data=json.dumps(data))
print(r.json())
print(sign)
