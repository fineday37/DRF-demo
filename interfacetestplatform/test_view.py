import json
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class LittleTestCase(TestCase):
    def setUp(self):
        self.click = APIClient()

    def test_users_post(self):
        # /users/ POST
        data = {
            "username": "us",
            "password": "2312323",
            "password2": "2312323"
        }
        response = self.client.post("http://127.0.0.1:8000/users/", data)
        response_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('创建用户成功', response_content["msg"])
        #
        # # /users/:id GET 地址
        # response_content = json.loads(response.content)
        # user_url = response_content["url"]
        #
        # # /users/:id GET 检查新增用户是否符合预期
        # response = self.client.get(user_url)
        # response_content = json.loads(response.content)
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual("tom", response_content["username"])
        # self.assertEqual("tom@example.com", response_content["email"])
