import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_jwt.settings import api_settings
# from .models import UserInfo
from django.contrib.auth.models import User
from django.core.cache import cache
from django_redis import get_redis_connection
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


class MyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        jwt_value = request.META.get("HTTP_AUTHORIZATION")

        if not jwt_value:
            raise AuthenticationFailed("未携带token")
        try:
            tokens = jwt_value.split(" ", 1)
            token = tokens[1].encode()
            print(tokens)
            payload = jwt_decode_handler(token)
            print(payload)
        except jwt.ExpiredSignature:
            raise AuthenticationFailed("token已过期")
        user = User.objects.filter(pk=payload['user_id']).first()
        conn = get_redis_connection('default')
        redis_token = conn.get(user.username)
        if token == redis_token:
            return user, token
        else:
            print("redis : {}".format(tokens))
            print(user.username)
            raise AuthenticationFailed("token已失效")
