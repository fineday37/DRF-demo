from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)
ALIPAY_APP_ID = "2021000122606367"  # 应用ID
APLIPAY_APP_NOTIFY_URL = None  # 应用回调地址[支付成功以后,支付宝返回结果到哪一个地址下面]
APP_PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "app_private_key.pem")  # 应用私钥的路径
ALIPAY_PUBLIC_KEY_PATH = os.path.join(BASE_DIR, "alp_public_key.pem")  # 支付宝公钥的路径
ALIPAY_DEBUG = True
# APIPAY_GATEWAY="https://openapi.alipay.com/gateway.do"               #这是上线后，真实的支付路径
APIPAY_GATEWAY = "https://openapi.alipaydev.com/gateway.do"  # 这是沙箱环境的支付宝提供的路径
ALIPAY_RETURN_URL = "http://localhost/pay_success"  # 这是支付成功后，支付宝最后跳转的页面路径
ALIPAY_NOTIFY_URL = "http://api.lufei.cn:8000/pay_success"
