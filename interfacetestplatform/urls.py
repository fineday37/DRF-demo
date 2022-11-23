from django.urls import path, re_path
from . import views
from . import viewtest
from rest_framework_jwt.views import obtain_jwt_token
urlpatterns = [
    path('', views.index),
    path('login/', views.login),
    path('logout', views.logout),
    path("reg", views.reg),
    path('project/', views.project),
    path('module/', views.module, name="module"),
    path('module_select', views.module_select, name="module_select"),
    path('test_case/', views.test_case, name='test_case'),
    re_path(r'^test_case_detail/([0-9]+)/$', views.test_case_detail, name="test_case_detail"),
    re_path(r'^module_test_case/([0-9]+)/$', views.module_test_case, name='module_test_case'),
    path('case_suite/', views.case_suite, name='case_suite'),
    re_path(r'^add_case_in_suite/([0-9]+)/$', views.add_case_in_suite, name='add_case_in_suite'),
    path(r'ajax_test/', views.ajax_test, name='ajax_test'),
    path(r'apiTest/', views.apiTest, name='apiTest'),
    re_path(r"^show_and_delete_case_in_suite/([0-9]+)/$", views.show_and_delete_case_in_suite, name=
            "show_and_delete_case_in_suite"),
    path("api/book/", viewtest.CardListAPIVIew.as_view()),
    path("api/generic/", viewtest.GenericList.as_view({"get": "list", "post": "create"})),
    path("api/user/", viewtest.UserView.as_view()),
    path("logins/", obtain_jwt_token),
    path('users/', viewtest.UserViews.as_view()),
    path('api/file/', viewtest.UpFileAPIView.as_view()),
    path("download/", views.download, name="download"),
    path("downloads/", views.download, name = "download")
]
