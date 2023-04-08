from django.db import models
from smart_selects.db_fields import GroupedForeignKey
from django.contrib.auth.models import User, AbstractUser


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('项目名称', max_length=50, unique=True, null=False)
    proj_owner = models.CharField('项目负责人', max_length=20, null=False)
    test_owner = models.CharField('测试负责人', max_length=20, null=False)
    dev_owner = models.CharField('开发负责人', max_length=20, null=False)
    desc = models.CharField('项目描述', max_length=100, null=True)
    create_time = models.DateTimeField('项目创建时间', auto_now_add=True)
    update_time = models.DateTimeField('项目更新时间', auto_now=True, null=True)

    # 打印对象时返回项目名称
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '项目信息表'
        verbose_name_plural = '项目信息表'


class Module(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('模块名称', max_length=50, null=False)
    belong_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    test_owner = models.CharField('测试负责人', max_length=20, null=False)
    desc = models.CharField("项目描述", max_length=20, null=False)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "模块信息表"
        verbose_name_plural = "模块信息表"


class TestCase(models.Model):
    id = models.AutoField(primary_key=True)
    case_name = models.CharField('用例名称', max_length=50, null=False)
    belong_project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='所属项目')
    belong_module = GroupedForeignKey(Module, "belong_project", on_delete=models.CASCADE, verbose_name='所属模块')
    request_data = models.CharField('请求数据', max_length=1024, null=False, default='')
    url = models.CharField('接口地址', max_length=1024, null=False, default='')
    assert_key = models.CharField('断言内容', max_length=1024, null=True)
    maintainer = models.CharField('编写人员', max_length=1024, null=False, default='')
    extract = models.CharField('提取变量表达式', max_length=1024, null=True)
    request_method = models.CharField('请求类型', max_length=1024, null=False)
    status = models.IntegerField(null=True, help_text='0:表示有效，1:表示无效')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="负责人", null=True)

    def __str__(self):
        return self.case_name

    class Meta:
        verbose_name = "测试用例表"
        verbose_name_plural = '测试用例表'


class CaseSuite(models.Model):
    id = models.AutoField(primary_key=True)
    suite_desc = models.CharField("用例集合描述", max_length=100, blank=True, null=True)
    if_execute = models.IntegerField(verbose_name='是否执行', null=False, default=0, help_text='0:执行,1:不执行')
    test_case_model = models.CharField("测试执行模式", max_length=100, blank=True, null=True, help_text='data/keyword')
    creator = models.CharField(max_length=50, blank=True, null=True)
    create_time = models.DateTimeField('创建时间', auto_now=True)

    class Meta:
        verbose_name = "测试集合表"
        verbose_name_plural = "测试集合表"


class SuiteCase(models.Model):
    id = models.AutoField(primary_key=True)
    case_suite = models.ForeignKey(CaseSuite, on_delete=models.CASCADE, verbose_name='用例集合')
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, verbose_name='测试用例')
    status = models.IntegerField(verbose_name='是否有效', null=False, default=1, help_text="0：有效，1：无效")
    create_time = models.DateTimeField("创建时间", auto_now=True)


# 测试接口模型
class Card(models.Model):
    card_id = models.IntegerField(verbose_name="卡号")
    card_user = models.CharField(verbose_name="姓名", max_length=128)
    card_time = models.DateTimeField(verbose_name="日期", auto_now_add=True)

    class Meta:
        verbose_name = "银行卡账户"
        verbose_name_plural = "银行卡账户信息"

    def __str__(self):
        return self.card_id


# 测试数据校验登录
class UserInfo(models.Model):
    level_choices = (1, "普通会员"), (2, "VIP"), (3, "SVIP")
    leave = models.IntegerField(verbose_name="级别", choices=level_choices, default=1)
    username = models.CharField(verbose_name="用户名", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=64)
    age = models.IntegerField(verbose_name="年龄", default=0)
    email = models.CharField(verbose_name="邮箱", max_length=64)
    token = models.CharField(verbose_name="TOKEN", max_length=64, null=True, blank=True)
    depart = models.ForeignKey(verbose_name="部门", to="Department", on_delete=models.CASCADE, default='')
    roles = models.ManyToManyField(verbose_name="角色", to="Role")

    def __str__(self):
        return self.username


# 数据校验关联角色
class Role(models.Model):
    title = models.CharField(verbose_name="名称", max_length=32)


# 数据校验外键部门
class Department(models.Model):
    title = models.CharField(verbose_name="名称", max_length=32)


def default_setting():
    setting = {
        "name": "返回值"
    }
    return setting


# 上传文件
class UpFile(models.Model):
    file = models.FileField(verbose_name="文件", upload_to='avatar/', blank=True, null=False)
    title = models.CharField(verbose_name="标题", max_length=30)
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_setting(self):
        return default_setting()

    class Meta:
        verbose_name = "上传文件"

    def __str__(self):
        return self.title
