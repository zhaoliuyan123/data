from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r"^user", UserAdmin.as_view()),  # 后台管理
    url(r"^", Index.as_view()),  # 用户页面
]
