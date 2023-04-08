import os.path
from datetime import datetime

from django.http import FileResponse, HttpResponse

from pay.key import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from alipay import AliPay
from rest_framework.response import Response


# 构造支付接口
class PayView(APIView):
    def get(self, request):
        alipay = AliPay(
            appid=settings.ALIPAY_APP_ID,
            app_notify_url=None,
            app_private_key_string=open(settings.APP_PRIVATE_KEY_PATH).read(),
            alipay_public_key_string=open(settings.ALIPAY_PUBLIC_KEY_PATH).read(),
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG
        )
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=1,
            total_amount="0.01",
            subject="支付",
            return_url=settings.ALIPAY_RETURN_URL
        )
        alp_url = settings.APIPAY_GATEWAY + "?" + order_string
        return Response({
            "alp_url": alp_url
        }, status=status.HTTP_200_OK)


# 支付回调
# class Pay_successView(APIView):

# 返回图片
class Get_Images(APIView):
    def get(self, request):
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), r"static\images\秋水.jpg"), 'rb') as f:
            data = f.read()
        print(type(data))
        return HttpResponse(data)
