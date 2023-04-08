import json
import os

from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from .form import UserForm, MusicTest
import traceback
from django.http import HttpResponse, FileResponse, Http404
from django.contrib.auth.models import User
from .models import Project, Module, TestCase, CaseSuite, SuiteCase, Card
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage


@login_required
def index(request):
    return render(request, "index.html")


# 新增用户
def reg(request):
    username = "test"
    password = "test"
    User.objects.create_user(username=username, password=password)  # 创建普通用户，密码加密(推荐使用)
    # User.objects.create_superuser(username=username, password=password, email='123@qq.com')  # 创建超级用户，但是必须填写邮箱事项，要不报错
    return HttpResponse('Congratulation！注册成功！')


# 登录
def login(request):
    print("request.session.items():{}".format(request.session.items()))
    if request.session.get('is_login'):
        return redirect('/')
    if request.method == "POST":
        login_form = UserForm(request.POST)
        massage = "检查填写的内容"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = auth.authenticate(username=username, password=password)
                if user is not None:
                    print("用户{}登陆成功".format(username))
                    auth.login(request, user)
                    request.session["is_login"] = True
                    return redirect('/')
                else:
                    massage = "用户名不存在或者密码不正确"
                    return render(request, 'login.html', locals())
            except:
                traceback.print_exc()
                massage = "程序异常"
        else:
            return render(request, 'login.html', locals())
    else:
        login_form = UserForm()
        return render(request, 'login.html', locals())


def register(request):
    return render(request, "register.html")


@login_required
def logout(request):
    auth.logout(request)
    request.session.flush()
    return redirect('/login')


# 项目
@login_required
def project(request):
    print("request.session.items():{}".format(request.session.items()))
    projects = Project.objects.filter().order_by("-id")
    count = get_paginator(request, projects).paginator
    print("projects:", projects)
    return render(request, "project.html", {"projects": get_paginator(request, projects), "count": count})


# 分页
@login_required
def get_paginator(request, data):
    paginator = Paginator(data, 3)
    page = request.GET.get('page')
    try:
        paginator_pages = paginator.page(page)
    except PageNotAnInteger:
        paginator_pages = paginator.page(1)
    except InvalidPage:
        # return HttpResponse("找不到页面内容")
        paginator_pages = paginator.page(1)
    return paginator_pages


# 模块
@login_required
def module(request):
    if request.method == "GET":
        modules = Module.objects.filter().order_by("-id")
        count = get_paginator(request, modules).paginator
        return render(request, "module.html", {"modules": get_paginator(request, modules), "count": count})
    # else:
    #     # 根据项目(Project)名查询对应模块
    #     proj_name = request.POST["proj_name"]
    #     projects = Project.objects.filter(name__contains=proj_name.strip())
    #     # 提取项目名称id列表
    #     projs = [proj.id for proj in projects]
    #     modules = Module.objects.filter(belong_project__in=pro\
    #
    #
    #     js)
    #     return render(request, "module.html", {"modules": get_paginator(request, modules), "proj_name": proj_name})


@login_required
def module_select(request):
    # 根据项目(Project)名查询对应模块
    proj_name = request.GET.get("proj_name")
    projects = Project.objects.filter(name__contains=proj_name.strip())
    # 提取项目名称id列表
    projs = [proj.id for proj in projects]
    modules = Module.objects.filter(belong_project__in=projs)
    count = get_paginator(request, modules).paginator
    return render(request, "module.html", {"modules": get_paginator(request, modules), "proj_name": proj_name,
                                           "count": count})


# 测试用例
@login_required
def test_case(request):
    # print("request.session['is_login']: {}".format(request.session['is_login']))
    test_cases = ''
    if request.method == "GET":
        test_cases = TestCase.objects.filter().order_by("id")
        print('testcases in testcase: {}'.format(test_cases))
        count = get_paginator(request, test_cases).paginator
    elif request.method == "POST":
        print("request.POST: {}".format(request.POST))
        test_case_id_list = request.POST.getlist("testcase_list")
        if test_case_id_list:
            print("test_case_id_list: {}".format(test_case_id_list))
        test_cases = TestCase.objects.filter().order_by('id')
        count = get_paginator(request, test_cases).paginator
    return render(request, 'test_case.html', {"test_cases": get_paginator(request, test_cases), "count": count})


# 测试用例详情
@login_required
def test_case_detail(request, test_case_id):
    test_case_id = int(test_case_id)
    test_case = TestCase.objects.get(id=test_case_id)
    print("test_case:{}".format(test_case))
    print("test_case_id:{}".format(test_case.id))
    print("test_case.belong_project:{}".format(test_case.belong_project))
    return render(request, "test_case_detail.html", {"test_case": test_case})


# 模块下测试用例
@login_required
def module_test_case(request, module_id):
    module = ""
    if module_id:
        module = Module.objects.filter(id=int(module_id))
    test_cases = TestCase.objects.filter(belong_module__in=module)
    print("test_case in module_test_case：{}".format(test_cases))
    return render(request, "test_case.html", {"test_cases": get_paginator(request, test_cases)})


# 测试集合
@login_required
def case_suite(request):
    case_suites = CaseSuite.objects.exclude(if_execute=1)
    print(type(case_suites))
    return render(request, 'case_suite.html', {"case_suites": get_paginator(request, case_suites)})


# 用例集合-新增测试用例
@login_required
def add_case_in_suite(request, suite_id):
    case_suite = CaseSuite.objects.get(id=suite_id)
    test_cases = TestCase.objects.filter().order_by('id')
    count = get_paginator(request, test_cases).paginator
    if request.method == 'GET':
        print("test cases:", test_cases)
    elif request.method == 'POST':
        test_cases_list = request.POST.getlist('testcases_list')
        if test_cases_list:
            print('勾选用例id：', test_cases_list)
            for test_case in test_cases_list:
                test_case = TestCase.objects.get(id=test_case)
                SuiteCase.objects.create(case_suite=case_suite, test_case=test_case)
        else:
            print("添加用例失败")
            return HttpResponse("添加的测试用例为空，请选择测试用例")
    return render(request, "add_case_in_suite.html", {'test_cases': get_paginator(request, test_cases),
                                                      'case_suite': case_suite, "count": count})


# ajax提交数据测试
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers


@csrf_exempt
def ajax_test(request):
    a = int(request.POST.get("name"))
    b = int(request.POST.get("age"))
    return HttpResponse(a + b)


@csrf_exempt
def apiTest(request):
    forms = MusicTest(request.POST)
    print(request.POST)
    if forms.is_valid():
        card_user = serializers.serialize("json", Card.objects.filter(pk=1))
        card_time = Card.objects.filter(pk=3).first().card_time
        datas = {"success": "true", "card_user": card_user, "card_time": card_time}
        # data = json.dumps(datas, ensure_ascii=False)
        return JsonResponse(datas, safe=False, json_dumps_params={"ensure_ascii": False})
    else:
        error = forms.errors
        print(error)
        datas = {"success": "false", "error": error}
        return JsonResponse(datas, safe=False, json_dumps_params={"ensure_ascii": False})


# 删除集合用例
@login_required
def show_and_delete_case_in_suite(request, suite_id):
    case_suite = CaseSuite.objects.get(id=suite_id)
    print(case_suite.suite_desc)
    test_cases = SuiteCase.objects.filter(case_suite=case_suite)
    if request.method == "POST":
        tests_case_list = request.POST.getlist("test_cases_list")
        if tests_case_list:
            print("勾选用例: ", tests_case_list)
            for test_case in tests_case_list:
                test_case = TestCase.objects.get(id=int(test_case))
                SuiteCase.objects.filter(case_suite=case_suite, test_case=test_case).first().delete()
        else:
            print("测试用例删除失败")
            return HttpResponse("未选中测试用例，重新选择")
    case_suite = CaseSuite.objects.filter(id=suite_id)
    return render(request, "show_and_delete_case_in_suite.html", {"test_cases": get_paginator(request, test_cases),
                                                                  "case_suite": case_suite})


@login_required
def download(request):
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "avatar", "log.txt")
    try:
        f = open(file_path, 'rb')
        r = FileResponse(f, as_attachment=True, filename="log.txt")
        return r
    except Exception as e:
        print("错误")
        raise e
        # raise Http404("Download error")
