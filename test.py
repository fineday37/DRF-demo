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
url = 'https://oapi.dingtalk.com/robot/send?access_token' \
      '=5fa13c78da92e06bdcdbe1f873c3da49336c89d3f9ac7bc9288dab1c3ba4ba24 '

headers = {'Content-Type': 'application/json;charset=utf-8'}

data = {
    "msgtype": "markdown",
    "markdown": {
        "title": "通知",
        "text": "#### 济南 @17852170964 \n"
                "> <font color='Blue' >**下方链接**</font>\n" +
                "> ![screenshot]"
                "(https://img0.baidu.com/it/u=143067786,"
                "2672561015&fm=253&app=138&size=w931&n=0&f=JPEG&fmt=auto?sec=1681232400&t"
                "=db6e0cbccd8543a6d8ca74c0486a87c9)\n" +
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
