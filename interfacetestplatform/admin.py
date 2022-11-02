from django.contrib import admin

from . import models


class ProjectClass(admin.ModelAdmin):
    list_display = ["id", "name", "proj_owner", "test_owner", "dev_owner", "desc", "create_time", "update_time"]


admin.site.register(models.Project, ProjectClass)


class ModuleAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "belong_project", "test_owner", "desc", "create_time", "update_time"]


admin.site.register(models.Module, ModuleAdmin)


class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'case_name', "belong_project", 'request_data', "url", 'assert_key', 'maintainer', 'extract',
                    'request_method', 'status', 'create_time', 'update_time', 'user']


admin.site.register(models.TestCase, TestCaseAdmin)


class CaseSuiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'suite_desc', 'if_execute', 'test_case_model', 'creator', 'create_time']


admin.site.register(models.CaseSuite, CaseSuiteAdmin)
