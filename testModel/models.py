from django.db import models
import json
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list

# 测试结果选项
RESULT_CHOICE = (
    ('passwd', "成功"),
    ('failed', "失败"),
    ('skipped', '跳过'),
    ('error', '故障'),
    ('', "未执行")
)

# 接口变更处理进度选项
API_UPDATE_STATUS_CHOICE = (
    (0, '待处理'),
    (1, '待验证'),
    (2, '已处理')
)

# 测试构建类型选项
BUILD_TYPE_CHOICE = (
    ("环境验证", '环境验证'),
    ("冒烟测试", "冒烟测试"),
    ("业务巡查", "业务巡查"),
    ("其他", "其他")
)


# 逻辑删除
class SoftDelTableQuerySet(models.QuerySet):
    """
    覆盖Django QuerySet默认的delete()方法，更新两个字段，标记查询对象的软删除
    ，通常用于不想永久删除数据库中的对象，逻辑删除，必须定义is_delete和delete_time当前时间
    """

    def delete(self):
        self.update(is_delete=True, delete_time=timezone.now())


# 自定义objects，默认排除已删除的记录
class BaseManager(models.Manager):
    # 指定用于管理器的查询集类
    _queryset_class = SoftDelTableQuerySet

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)


# 基础表：公共字段列-创建时间/更新时间/状态/描述
class BaseModel(models.Model):
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="修改时间", null=True, auto_now=True)
    delete_time = models.DateTimeField(verbose_name="删除时间", null=True, default=None)
    is_delete = models.BooleanField(verbose_name="是否已删除", default=None)
    status = models.BooleanField(verbose_name="状态(1正常 0停用)", default=True)
    description = models.CharField(max_length=4096, blank=True, null=True, verbose_name="描述")  # 允许不填

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.delete_time = timezone.now()
        self.save()

    objects = BaseManager()

    class Meta:
        abstract = True  # 抽象基类
        verbose_name = "公共字段表"
        db_table = 'base_table'


# 字典类型表
class DictType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default='', verbose_name="字典名称")
    type = models.CharField(max_length=100, default='', verbose_name="字典类型")
    remark = models.CharField(max_length=500, default='', verbose_name="备注")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=20,
                                verbose_name="创建人", related_name="dict_type_creator")
    updater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=20,
                                verbose_name="更新人", related_name="dict_type_updater")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '字典类型表'
        verbose_name_plural = '字典类型表'  # admin复数形式名称
        db_table = 'dict_type_table'


# 字典数据表
class DictData(models.Model):
    id = models.AutoField(ptimary_key=True)
    dict_type = models.ForeignKey(DictType, on_delete=models.SET_NULL, null=True, max_length=50,
                                  verbose_name='字典名称', related_name='data_dict')
    dict_sort = models.CharField(max_length=100, default='', verbose_name="字典排序")
    dict_label = models.CharField(max_length=100, default='', verbose_name='字典标签')
    dict_value = models.CharField(max_length=100, default='', verbose_name='字典键值')
    list_class = models.CharField(max_length=100, default='', verbose_name='表格回显样式（success/info/warning/danger）')
    is_default = models.BooleanField(default=False, verbose_name='是否默认(1是 0否)')
    remark = models.CharField(max_length=100, default='', verbose_name="备注")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=20,
                                verbose_name="创建人", related_name="dict_type_creator")
    updater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=20,
                                verbose_name="更新人", related_name="dict_type_updater")

    def __str__(self):
        return self.dict_type

    class Meta:
        verbose_name = '字典数据表'
        verbose_name_plural = '字典数据表'
        db_table = 'dict_tata_table'


# 部门表
class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="部门名称")
    safe_name = models.CharField(default='', blank=True, null=True, max_length=50, verbose_name='部门标识')
    leader = models.CharField(default='', blank=True, null=True, max_length=50, verbose_name='负责人')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '部门表'
        verbose_name_plural = '部门表'
        db_table = 'department_table'


# 项目表
class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='项目名称')
    version = models.CharField(max_length=50, null=True, verbose_name='版本')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name='部门',
                                   related_name='project')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=20,
                                verbose_name="创建人", related_name="dict_type_creator")
    updater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=20,
                                verbose_name="更新人", related_name="dict_type_updater")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '项目表'
        verbose_name_plural = '项目表'
        db_table = 'project_table'


# 项目动态
class ProjectDynamic(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, verbose_name="项目动态",
                                related_name="project_dynamic")
    time = models.DateTimeField(verbose_name="操作时间", max_length=128)
    type = models.CharField(verbose_name="操作类型", max_length=50)
    operationObject = models.CharField(verbose_name='操作对象', max_length=50)
    user = models.ForeignKey(User, blank=True, null=True, verbose_name="操作人", on_delete=models.SET_NULL,
                             related_name='username_dynamic')
    description = models.CharField(max_length="1024", blank=True, null=True, verbose_name="描述")

    def __str__(self):
        return self.project

    class Meta:
        verbose_name = '项目动态表'
        verbose_name_plural = '项目动态表'
        db_table = 'project_dynamic'


# 项目成员
class ProjectMember(models.Model):
    CHOICES = (
        ("超级管理员", "超级管理员"),
        ("开发人员", "开发人员"),
        ("测试人员", "测试人员"),
        ("游客", "游客")
    )
    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=50, verbose_name="角色", choices=CHOICES)
    status = models.BooleanField(default=True, verbose_name="状态")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, verbose_name='项目名称',
                                related_name='project_member')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='名称',
                             related_name='user_member')

    def __str__(self):
        return self.role

    class Meta:
        verbose_name = '项目成员表'
        verbose_name_plural = '项目成员表'
        db_table = 'project_member'


# app系统配置
def default_app_setting():
    setting = {
        "debug": {"value": True, "description": "Debug模式"},
        "file_log_level": {"value": 'DEBUG', "description": "日志等级(文件)"},
        "console_log_level": {"value": 'INFO', "description": "日志等级(控制台)"},
        "testcase_max_rotation": {"value": 50, "description": "保留历史构建数据的最大个数"}
    }
    return setting


class AppSetting(models.Model):
    id = models.AutoField(primary_keky=True)
    name = models.CharField(max_length=50, null=True, default="app系统配置", verbose_name="Name")
    data = models.JSONField(default=default_app_setting, verbose_name='app配置数据')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name="描述")
    status = models.BooleanField(default=True, verbose_name="状态")

    def get_default(self):
        return default_app_setting()

    def delete(self, using=None, keep_parents=False):
        return "禁止删除"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'app配置'
        verbose_name_plural = 'app配置'
        db_table = 'app_setting'


# 全局环境配置
def default_env_config():
    config = {
        "company_id": {"value": '', "description": "公司ID"},
        "base_url_mk": {"value": '', "description": "服务商后台地址"},
        "base_url_qw": {"value": '', "description": "企微端地址"},
        "base_url_oss_bill": {"value": '', "description": "运营计费地址"},
        "base_url_oss_official": {"value": '', "description": "运营官方地址"},
        "base_url_qyapi": {"value": 'https://qyapi.weixin.qq.com', "description": "企业微信地址"},
        "corp_id": {"value": '', "description": "企微企业标识corp_id"}
    }
    return config


def default_qw_external_contact_config():
    cf = {
        "external_contact_token": {"value": '', "description": "企微客户联系Token"},
        "external_contact_aes_key": {"value": '', "description": "企微客户联系AESKey"},
        "external_contact_corp_secret": {"value": '', "description": "企微客户联系Secret"}
    }
    return cf


class GlobalEnv(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="名称")
    config = models.JSONField(default=default_env_config, verbose_name="环境基础配置")
    qw_config = models.JSONField(default=default_qw_external_contact_config, verbose_name="企微客户联系方式配置")
    data = models.JSONField(default=dict, verbose_name="环境数据")
    mock = models.JSONField(default=dict, verbose_name="mock数据")
    mock_dynamic = models.BooleanField(default=True, verbose_name="动态更新mock")
    description = models.CharField(blank=True, null=True, verbose_name="描述", max_length=1024)
    status = models.BooleanField(default=True, verbose_name="状态")
    is_default = models.BooleanField(verbose_name="默认配置", default=False)

    def __str__(self):
        return self.name

    def get_env_config(self):
        return default_env_config()

    def get_qw_config(self):
        return default_qw_external_contact_config()

    class Meta:
        verbose_name = '测试环境配置'
        verbose_name_plural = '测试环境配置'
        db_table = 'global_env'


# 全局const
class GlobalConst(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="const名称")
    value = models.TextField(blank=True, null=True, verbose_name="值")
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name="描述")
    status = models.BooleanField(default=True, verbose_name="状态")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '全局常量'
        verbose_name_plural = '全局常量'
        db_table = 'global_const'


# 全局header
class GlobalHeader(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="header名称")
    value = models.TextField(blank=True, null=True, verbose_name="内容")
    description = models.CharField(max_length=50, blank=True, null=True, verbose_name="描述")
    status = models.BooleanField(default=True, verbose_name="状态")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '全局请求头'
        verbose_name_plural = '全局请求头'
        db_table = 'global_header'


# 通用校验规则
class GlobalResponseValidate(models.Model):
    objects = models.Manager
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1024, default="默认校验", verbose_name="校验名称")
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name="描述")
    check_status_code = models.BooleanField(default=True, verbose_name="检查状态码")
    check_json_schema = models.BooleanField(default=True, verbose_name="检查json-schema")
    check_response_data = models.BooleanField(default=True, verbose_name="检查响应数据")
    status_code = models.CharField(default='200', max_length=100, verbose_name="期待状态码",
                                   validators=[validate_comma_separated_integer_list])  # 验证一个整数列表，逗号分割
    status = models.BooleanField(default=True, verbose_name="状态")
    is_default = models.BooleanField(verbose_name="默认配置", default=False)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.is_default:
            try:
                GlobalResponseValidate.objects.filter(is_default=True).update(is_default=False)
            except EncodingWarning as e:
                pass
        super(GlobalResponseValidate, self).save()

    class Meta:
        verbose_name = '校验规则'
        verbose_name_plural = '校验规则'
        db_table = 'global_validate'


# 全局标签
class GlobalLabel(models.Model):
    LABEL_TYPE_CHOICE = (
        ("priority", "优先级"),
        ("severity", "严重等级"),
        ("function", '业务功能'),
        ("testsuite_type", '测试集类型'),
        ('other', '其他')
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='标签名')
    type = models.CharField(verbose_name="标签类型", choices=LABEL_TYPE_CHOICE, default='priority', max_length=30)
    status = models.BooleanField(default=True, verbose_name="状态")
    description = models.CharField(verbose_name='描述', max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '全局标签'
        verbose_name_plural = '全局标签'
        db_table = 'global_label'


# 自定义方法
class CustomMethod(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="项目")
    name = models.CharField(max_length=50, verbose_name="方法名")
    description = models.CharField(max_length=50, blank=True, null=True, verbose_name="备注")
    type = models.BooleanField(max_length=50, verbose_name="类型")
    dataCode = models.TextField(verbose_name="代码")
    status = models.BooleanField(verbose_name="状态", default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '自定义方法'
        verbose_name_plural = '自定义方法'
        db_table = 'custom_method'


# 接口分组
class ApiGroup(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="接口分组名称")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="项目")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '接口分组'
        verbose_name_plural = '接口分组'
        db_table = 'apo_group'


# 接口信息
class ApiInfo(BaseModel):
    HTTP_CHOICE = (
        ("HTTP", "HTTP"),
        ("HTTPS", "HTTPS")
    )
    REQUEST_TYPE_CHOICE = (
        ("POST", "POST"),
        ("GET", "GET"),
        ("PUT", "PUT"),
        ("DELETE", "DELETE")
    )
    HOST_TAG_CHOICE = (
        ("mk", "服务商后台地址"),
        ("qw", "企微端地址"),
        ("oss_bill", "运营计费地址"),
        ("oss_official", "运营官方地址"),
        ("qyapi", "企业微信API")
    )
    ORIGIN_CHOICE = (
        ("yapi", "yapi"),
        ('xmind', "xmind"),
        ('excel', "excel"),
        ('manual', 'manual')
    )
    id = models.AutoField(primary_key=True)
    yapi_id = models.IntegerField(default=0, verbose_name="YAPI接口ID")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="api_project", verbose_name="项目")
    api_group = models.ForeignKey(ApiGroup, on_delete=models.CASCADE, related_name="api_group", verbose_name="分组")
    origin = models.CharField(max_length=50, default="manual", choices=ORIGIN_CHOICE, verbose_name="接口数据来源")
    name = models.CharField(max_length=50, verbose_name="接口名称")
    http_type = models.CharField(max_length=50, default='HTTP', verbose_name="接口协议", choices=HTTP_CHOICE)
    host_tag = models.CharField(max_length=50, verbose_name="指定host", default="mk", choices=HOST_TAG_CHOICE)
    method = models.CharField(max_length=50, verbose_name="请求方式", choices=REQUEST_TYPE_CHOICE)
    path = models.CharField(max_length=1024, verbose_name="接口地址")
    yapi_req_headers = models.TextField(blank=True, null=True, verbose_name='yapi定义-请求头')
    yapi_req_params = models.TextField(blank=True, null=True, verbose_name='yapi定义-请求参数-params')
    yapi_req_query = models.TextField(blank=True, null=True, verbose_name='yapi定义-请求参数-query')
    yapi_req_body_form = models.TextField(blank=True, null=True, verbose_name='yapi定义-请求参数-body_form')
    yapi_req_body_other = models.TextField(blank=True, null=True, verbose_name='yapi定义-请求参数-body_other')
    yapi_res_body = models.TextField(blank=True, null=True, verbose_name='yapi定义-响应body')
    req_headers = models.TextField(blank=True, null=True, verbose_name='请求头')
    req_params = models.TextField(blank=True, null=True, verbose_name='请求参数-params')
    req_data = models.TextField(blank=True, null=True, verbose_name='请求参数-data')
    req_json = models.TextField(blank=True, null=True, verbose_name='请求参数-json')
    validator = models.TextField(blank=True, null=True, verbose_name='响应数据验证')
    update_status = models.IntegerField(default=1, choices=API_UPDATE_STATUS_CHOICE, verbose_name="更新状态")
    labels = models.ManyToManyField(GlobalLabel, blank=True, default=[], verbose_name="标签", related_name="api_label")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=20, verbose_name="创建人",
                                related_name="api_info_creator")
    updater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=20, verbose_name="更新人",
                                related_name="api_info_updater")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "接口信息"
        verbose_name_plural = '接口信息'
        db_table = 'apo_info'


# 接口变更历史
class ApiUpdateHistory(models.Model):
    id = models.AutoField(primary_key=True)
    api = models.ForeignKey(ApiInfo, on_delete=models.CASCADE, related_name="update_api", verbose_name="所属接口")
    event = models.CharField(blank=True, null=True, max_length=100, verbose_name="变更事件")
    content = models.TextField(blank=True, null=True, verbose_name="变更内容")
    updater = models.CharField(blank=True, null=True, max_length=20, verbose_name='更新人')
    update_time = models.DateTimeField(verbose_name="变更时间", auto_now=True)
    update_status = models.IntegerField(default=0, verbose_name='变更处理状态', choices=API_UPDATE_STATUS_CHOICE)

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = "接口变更"
        verbose_name_plural = '接口变更'
        db_table = 'api_update'


# yapi接口变更事件
class YapiEvent(models.Model):
    id = models.AutoField(primary_key=True)
    yapi_id = models.IntegerField(default=0, verbose_name="yapi接口id")
    event = models.CharField(blank=True, null=True, max_length=100, verbose_name="变更事件")
    content = models.TextField(blank=True, null=True, verbose_name="变更内容")
    updater = models.CharField(blank=True, null=True, max_length=20, verbose_name='更新人')
    update_time = models.DateTimeField(verbose_name="变更时间", auto_now=True)

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = "yapi接口变更"
        verbose_name_plural = 'yapi接口变更'
        db_table = 'yapiapi_update'


# 测试用例集
class TestSuite(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="用例集名称")
    safe_name = models.SlugField(max_length=50, verbose_name="用例集标识(用作文件夹名)")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, verbose_name="部门")
    header = models.TextField(verbose_name="请求头", blank=True, null=True)
    labels = models.ManyToManyField(GlobalLabel, blank=True, default=[], related_name="suite_table",
                                    verbose_name="标签")
    setup = models.JSONField(blank=True, null=True, default=list, verbose_name='setup')
    setup_class = models.JSONField(blank=True, null=True, default=list, verbose_name='setup_class')
    teardown = models.JSONField(blank=True, null=True, default=list, verbose_name='teardown')
    teardown_class = models.JSONField(blank=True, null=True, default=list, verbose_name='teardown_class')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=20,
                                verbose_name="创建人", related_name="suite_creator")
    updater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=20,
                                verbose_name="更新人", related_name="suite_updater")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "测试用例集"
        verbose_name_plural = '测试用例集'
        db_table = 'test_suite'


# 测试用例
class TestCase(BaseModel):
    TEST_TYPE_CHOICE = (
        ("单接口测试", "单接口测试"),
        ("场景测试", "场景测试"),
        ("setup", "setup"),
        ("teardown", "teardown")
    )
    SEVERITY_CHOICE = (
        ("blocker", "阻塞缺陷"),
        ("critical", "严重缺陷"),
        ("normal", '一般缺陷'),
        ("minor", "次要缺陷"),
        ("trivial", "轻微缺陷")
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="用例名称")
    safe_name = models.SlugField(max_length=50, verbose_name="用例标识(用作py类名)")
    test_suite = models.ForeignKey(TestSuite, on_delete=models.CASCADE, related_name="case_suite", verbose_name="用例集")
    labels = models.ManyToManyField(GlobalLabel, related_name="case_label", verbose_name="标签", blank=True,
                                    default=[])
    type = models.CharField(verbose_name="测试类型", choices=TEST_TYPE_CHOICE, default="单接口测试", max_length=50)
    variable = models.TextField(verbose_name="用例变量", null=True, blank=True)
    depends = models.TextField(null=True, blank=True, verbose_name="依赖项")
    severity = models.CharField(choices=SEVERITY_CHOICE, max_length=20, default="normal", verbose_name="用例等级")
    result = models.CharField(max_length=30, verbose_name="测试结果", choices=RESULT_CHOICE, default='null')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='case_creator', verbose_name="创建人",
                                blank=True, null=True)
    updater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=20, verbose_name="更新人",
                                related_name="case_updater")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "测试用例"
        verbose_name_plural = '测试用例'
        db_table = 'test_case'


# 测试步骤
class TestStep(BaseModel):
    id = models.AutoField(primary_keky=True)
    sid = models.IntegerField(default=0, verbose_name="测试步骤执行id")
    name = models.CharField(max_length=100, verbose_name="步骤名称")
    test_case = models.ForeignKey(TestCase, related_name="step_case", on_delete=models.CASCADE, verbose_name="测试用例")
    apiInfo = models.ForeignKey(ApiInfo, related_name="step_api", on_delete=models.CASCADE, verbose_name="所属接口")
    labels = models.ManyToManyField(GlobalLabel, related_name="step_label", blank=True, default=[],
                                    verbose_name="标签")
    depends = models.ManyToManyField('self', blank=True, default=[], verbose_name='依赖项（步骤）',
                                     related_name='step_depends')  # 关联同一模型
    skipif = models.TextField(blank=True, null=True, default='', verbose_name='skipif')
    setup_hooks = models.JSONField(blank=True, null=True, default=list, verbose_name='setup_hooks')
    teardown_hooks = models.JSONField(blank=True, null=True, default=list, verbose_name='teardown_hooks')
    req_path = models.CharField(blank=True, null=True, max_length=1024, default='', verbose_name="请求路径")
    req_headers = models.TextField(blank=True, null=True, verbose_name="请求头")
    req_params = models.TextField(blank=True, null=True, verbose_name='请求参数-params')
    req_json = models.TextField(blank=True, null=True, verbose_name='请求参数-json')
    req_data = models.TextField(blank=True, null=True, verbose_name='请求参数-data')
    validator = models.TextField(blank=True, null=True, verbose_name='响应数据验证')
    extractor = models.TextField(blank=True, null=True, verbose_name='响应数据变量提取')
    result = models.CharField(max_length=30, verbose_name="测试结果", choices=RESULT_CHOICE, default='null')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=20, verbose_name="创建人",
                                related_name="case_creator")
    updater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, max_length=20,
                                verbose_name="更新人", related_name="case_updater")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "测试步骤"
        verbose_name_plural = '测试步骤'
        db_table = 'test_step'


# 测试报告
class TestReport(BaseModel):
    BUILD_STATUS_CHOICE = (
        ("build-status-static", "构建完成"),
        ("build-status-in-progress", "构建正在进行中")
    )

    id = models.AutoField(primary_key=True)
    build_type = models.CharField(verbose_name="创建类型", choices=BUILD_TYPE_CHOICE, default='其他', max_length=20)
    build_status = models.BooleanField(verbose_name="构建状态", choices=BUILD_STATUS_CHOICE,
                                       default='build-status-in-progress', max_length=30)
    env = models.ForeignKey(GlobalEnv, on_delete=models.CASCADE, blank=True, null=True, related_name='report_env',
                            verbose_name="报告关联测试环境")
    status = models.BooleanField(default=True, verbose_name="状态")
    duration = models.IntegerField(default=0, verbose_name="耗时(秒)")
    case_total = models.IntegerField(default=0, verbose_name='用例总数')
    case_passed = models.IntegerField(default=0, verbose_name='用例成功数量')
    case_failed = models.IntegerField(default=0, verbose_name='用例失败数量')
    case_skipped = models.IntegerField(default=0, verbose_name='用例跳过数量')
    case_error = models.IntegerField(default=0, verbose_name='用例故障数量')
    case_pass_rate = models.FloatField(default=0, verbose_name='用例通过率')
    step_total = models.IntegerField(default=0, verbose_name="步骤总数")
    step_passed = models.IntegerField(default=0, verbose_name="步骤成功数量")
    step_failed = models.IntegerField(default=0, verbose_name="步骤失败数量")
    step_skipped = models.IntegerField(default=0, verbose_name="步骤跳过数量")
    step_error = models.IntegerField(default=0, verbose_name="步骤故障数量")
    step_passed_rate = models.FloatField(default=0, verbose_name="步骤成功率")
    client = models.CharField(default='localhost', max_length=50, blank=True, null=True, verbose_name='测试机器Client端')
    log_path = models.TextField(max_length=500, blank=True, null=True, verbose_name='日志文件地址')
    html_report_path = models.TextField(max_length=500, blank=True, null=True, verbose_name='pytest-html报告地址')
    allure_xml_path = models.TextField(max_length=500, blank=True, null=True, verbose_name='allure xml数据地址')
    allure_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='allure 报告地址')
    jenkins_job_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='jenkins job name')
    jenkins_build_number = models.IntegerField(default=0, blank=True, null=True, verbose_name='jenkins build number')

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = "测试报告"
        verbose_name_plural = '测试报告'
        db_table = 'test_report'

