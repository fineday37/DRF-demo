import datetime
import os.path
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
from .models import UserInfo, Role, UpFile
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from .MybaseView import creare_token
from demo.pagination import MyPaginator
from django.core.cache import cache
from .Myauthenticate import MyAuthentication
from django_redis import get_redis_connection
# 文件解析器
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
# 下载文件
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import BaseFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django.http import HttpResponse, Http404


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

    def validate(self, attrs):
        name = attrs.get('username')
        self.context["please"] = name
        print(name)
        return attrs

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
        fields = ["id", "username", "age", "email", "email4", "level_text", "depart", "roles", "extra"]
        extra_kwargs = {
            "username": {"min_length": 1, "max_length": 6},
            "email": {"validators": [EmailValidator, ]}
        }


class Filter1(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        id = request.query_params.get('id')
        if not id:
            return queryset
        return queryset.filter(id=id)


class Filter2(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        card_id = request.query_params.get('card_id')
        if not card_id:
            return queryset
        return queryset.filter(card_id=card_id)


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
        print("打印出来的值是: {}".format(ls))
        print("设置：{}".format(ser.context["please"]))
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


# 新增card
class GenericAPISerializar(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'

    def create(self, validated_data):
        print("刀片超车啊")
        user_object = Card.objects.create(**validated_data)
        # print(user_object)
        return user_object


class ModelViewSetPafination(PageNumberPagination):
    page_size = 2
    page_query_param = "page"
    page_size_query_param = "size"
    max_page_size = 100


from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework.viewsets import ModelViewSet


class DigCreateModelMixin(mixins.CreateModelMixin, GenericViewSet):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        print(serializer)
        headers = self.get_success_headers(serializer.data)
        data = {"name": "测试返回", "res": serializer.data}
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()


class DigListModelMixin(mixins.ListModelMixin, GenericViewSet):
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response("指定返回内容")


# 过滤搜索条件
class CollectFilterSet(filters.FilterSet):
    id_gt = filters.NumberFilter(field_name='id', lookup_expr='gt')
    user = filters.CharFilter(field_name='card_user', lookup_expr='contains')
    card_time = filters.CharFilter(field_name='card_time', lookup_expr='year__gt')

    class Meta:
        model = Card
        fields = ["card_id", "card_user", "card_time"]


class GenericList(DigCreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, DigListModelMixin,
                  GenericViewSet):
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = CollectFilterSet
    # filterset_fields = ["card_id"]
    pagination_class = ModelViewSetPafination
    queryset = Card.objects.all()
    serializer_class = GenericAPISerializar

    def perform_create(self, serializer):
        print(serializer.validated_data['card_id'])
        print(self.action)
        serializer.save()
        # return Response({"active": serializer.validated_data})

    def perform_update(self, serializer):
        serializer.save()


# 新建用户序列化
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
        conn.set(user.username, token.encode(), 600)
        # cache.set(user, token)
        user.token = token
        return user


# 创建用户获取token
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
            # print(user.errors)
            user.save()
            return Response({'code': 200, 'msg': '创建用户成功', 'data': user.data})
        except Exception as e:
            print(e)
            return Response({'code': 201, 'msg': '创建失败，请重试'})


# 登录token
def jwt_response_payload_handler(token, user=None, request=None):
    conn = get_redis_connection('default')
    conn.set(user.username, token)
    # cache.set(token, user.username)
    return {
        'userid': user.id,
        'user': user.username,
        'token': token,
        "code": 20000
    }


from rest_framework_jwt.settings import api_settings
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER


# 自定义登录

class UserAPIView(ViewSet):
    @action(methods=['POST', ], detail=False)
    def login(self, request):
        back_dic = {'code': 20000}
        username = request.data.get('username')
        password = request.data.get('password')
        passwd = User.objects.filter(username=username)[0].password
        encryption = check_password(password, passwd)
        print(passwd)
        if encryption:
            user = User.objects.filter(username=username).first()
        else:
            user = False
        if user:
            # 获取荷载  直接用jwt模块提供的，缺什么导什么
            payload = jwt_payload_handler(user)
            # 获取token串  直接用jwt模块提供的，缺什么导什么
            token = jwt_encode_handler(payload)
            back_dic['token'] = token
            back_dic['username'] = username
        else:
            back_dic['code'] = 101
            back_dic['message'] = '用户名或密码错误'
        return Response(back_dic)


# 上传文件序列化
class FileSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = UpFile
        fields = ["file", "title", "timestamp"]


# 上传文件
class UpFileAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file_serializers = FileSerializer(data=request.data)
        if file_serializers.is_valid():
            file_serializers.save()
            return Response({
                "code": 0,
                "msg": "success!",
                "data": file_serializers.data,
                "setting": UpFile.get_setting(self)
            },
                status=status.HTTP_200_OK
            )
        else:
            return Response({
                "code": 400,
                "msg": "bad request",
                "data": file_serializers.errors
            },
                status=status.HTTP_400_BAD_REQUEST)


# 下载文件
class DownLoad(APIView):
    def get(self, request):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "avatar", request.query_params['name'])
        try:
            f = open(file_path, 'rb')
            r = FileResponse(f, as_attachment=True, filename=request.query_params['name'])
            return r
        except Exception as e:
            print(e)
            return Response({
                "error": "找不到该文件"
            })


from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job
from django_apscheduler.models import DjangoJob
import smtplib
from email.mime.text import MIMEText
import traceback
from script.snowflake import IdWorker


# 发送邮件
def send_excel(timing):
    try:
        session = smtplib.SMTP_SSL('smtp.qq.com', 465, 30)
        message = MIMEText(timing, 'plain', 'utf-8')
        message['subject'] = '响应内容'  # 标题
        message['from'] = '1250953976@qq.com'  # 发送人
        message['to'] = 'zhenguo_kong@126.com'  # 接收人
        session.login('1250953976@qq.com', 'gdvurwhwmxvmgdha')
        # 发送
        session.sendmail('1250953976@qq.com', 'zhenguo_kong@126.com', str(message))
        print('发送成功')
    except Exception as e:
        print(traceback.print_exc(), e)  # 打印错误信息


# 定时发送
class Send_Excel(APIView):
    def get(self, request):
        scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        scheduler.add_jobstore(DjangoJobStore(), 'default')
        input_date = str(request.query_params['datetimes']).split("-")
        text = request.query_params["text"]
        # task_id = request.query_params['task_id']
        task_id = IdWorker(1, 2, 0).get_id()
        print(type(task_id))
        scheduler.add_job(send_excel, 'date', id=str(task_id), run_date=datetime.datetime
        (int(input_date[0]), int(input_date[1]), int(input_date[2]),
         int(input_date[3]), int(input_date[4])), args=(text,))
        scheduler.start()
        return Response('定时完成')


from rest_framework.exceptions import AuthenticationFailed


class Test_Get(APIView):
    def get(self, requests, pk):
        # raise AuthenticationFailed("登陆失败")
        return Response(pk)


class Test_Url(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    @action(methods=['get', 'post', 'put'], detail=False)
    def latest(self, requests):
        name = requests.data["name"]
        data = {"success": name}
        return Response(data)
