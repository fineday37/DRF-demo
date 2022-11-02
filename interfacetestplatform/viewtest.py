import re

from django.core.validators import EmailValidator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import Card, Department, Role
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin,
    DestroyModelMixin, ListModelMixin
)
from .models import UserInfo, Role
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .MybaseView import creare_token
from demo.pagination import MyPaginator
from django.core.cache import cache
from .Myauthenticate import MyAuthentication
from django_redis import get_redis_connection

class CartAPISerializar(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'


class RegexValidator:
    def __init__(self, base):
        self.base = base

    def __call__(self, value):
        match_object = re.match(self.base, value)
        if not match_object:
            raise serializers.ValidationError("格式错误")


class DepartModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "title"]
        extra_kwargs = {
            "id": {"read_only": False},
            "title": {"read_only": True}
        }


class RoleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "title"]
        extra_kwargs = {
            "id": {"read_only": False},
            "title": {"read_only": True}
        }


class UserSerializar(serializers.ModelSerializer):
    level_text = serializers.CharField(source="get_leave_display", read_only=True)
    print(level_text)
    depart = DepartModelSerializer(many=False)
    roles = RoleModelSerializer(many=True)
    extra = serializers.SerializerMethodField(read_only=True)
    # email2 = serializers.EmailField(label="邮箱2")
    # email3 = serializers.CharField(label="邮箱3", validators=[RegexValidator(r"^\w+@\w+\.\w+$"), ])
    email4 = serializers.CharField(label="邮箱4", write_only=True)

    def validate_email4(self, value):
        if re.match(r"^\w+@\w+\.\w+$", value):
            return value
        raise serializers.ValidationError("邮箱格式错误")

    def get_extra(self, validated_data):
        return "达摩克里斯之剑"

    def create(self, validated_data):
        # print(validated_data)
        depart_id = validated_data.pop('depart')["id"]
        role_id_list = [ele["id"] for ele in validated_data.pop("roles")]
        validated_data["depart_id"] = depart_id
        user_object = UserInfo.objects.create(**validated_data)
        user_object.roles.add(*role_id_list)
        return user_object

    class Meta:
        model = UserInfo
        fields = ["username", "age", "email", "email4", "level_text", "depart", "roles", "extra"]
        extra_kwargs = {
            "username": {"min_length": 1, "max_length": 6},
            "email": {"validators": [EmailValidator, ]}
        }


class UserView(APIView):
    # permission_classes = [IsAuthenticated, ]
    # authentication_classes = [JSONWebTokenAuthentication, ]
    authentication_classes = [MyAuthentication, ]

    def post(self, request):
        ser = UserSerializar(data=request.data, )
        if not ser.is_valid():
            return Response({"code": 400, "data": ser.errors})
        ser.validated_data.pop("email4")
        ls = ser.save(leave=1, password="123")
        print("打印出来的值是: {}".format(ser))
        return Response({"code": 200, "data": ser.data})

    def get(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        print("打印出：{}".format(token))
        queryset = UserInfo.objects.all()
        page_obj = MyPaginator()
        page_data = page_obj.paginate_queryset(queryset, request)
        ser = UserSerializar(instance=page_data, many=True)
        return page_obj.get_paginated_response({"code": 200, "data": ser.data})


class CardListAPIVIew(APIView):
    def get(self, format=None):
        cards = Card.objects.all()
        serializer = CartAPISerializar(cards, many=True)
        return Response({
            "code": 0,
            "msg": "查询成功",
            "data": serializer.data
        })

    def post(self, request, format=None):
        verify_data = CartAPISerializar(data=request.data)
        if verify_data.is_valid():
            verify_data.save()
            return Response({
                "code": 0,
                "msg": "创建成功",
                "data": request.data
            })
        else:
            return Response({
                "code": 0,
                "msg": "创建失败",
                "data": "request data invaild %s" % verify_data.errors
            })


class GenericAPISerializar(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'


class GenericList(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin,
                  GenericViewSet):
    queryset = Card.objects.all()
    serializer_class = GenericAPISerializar

    def perform_create(self, serializer):
        serializer.save()


class CreateUserSerializers(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        # 密码加密
        password = make_password(validated_data.get('password'))
        user.password = password
        user.save()
        token = creare_token(user)
        conn = get_redis_connection('default')
        conn.set(user.username, token.encode(), 60)
        # cache.set(user, token)
        user.token = token
        return user


class UserViews(APIView):
    def post(self, request):
        data = request.data
        # print(data)

        if not all(['username', 'password', 'password2']):
            return Response({'code': 202, 'msg': '参数不全'})

        if data['password'] != data['password2']:
            return Response({'code': 204, 'msg': '两次密码不一致'})

        try:
            user = CreateUserSerializers(data=data)
            user.is_valid()
            print(user.errors)
            user.save()
            return Response({'code': 200, 'msg': '创建用户成功', 'data': user.data})
        except Exception as e:
            print(e)
            return Response({'code': 201, 'msg': '创建失败，请重试'})


def jwt_response_payload_handler(token, user=None, request=None):
    conn = get_redis_connection('default')
    conn.set(user.username, token, 60)
    # cache.set(token, user.username)
    return {
        'userid': user.id,
        'user': user.username,
        'token': token
    }
