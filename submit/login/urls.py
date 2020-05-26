from django.conf.urls import url
from .views import *
from login.views import *

app_name = '[login]'
urlpatterns = [
    url(r'^register/$', Register.as_view()),  # 注册
    url(r'^get_verify_img/$', get_verify_img.as_view()),  # 图片验证码
    url(r'^login/$', Login.as_view()),  # 登陆
    url(r'^outLogin/$', OutLogin.as_view()),  # 退出登录
    url(r'^amount/$', Amount.as_view()),  # 今日分类提交数量
    url(r'^record/$', Record.as_view()),  # 后台首页 分类目录站点公示
    url(r'^submits/$', Submits.as_view()),  # 后台首页 今日分类提交数量
    url(r'^directory/$', Directory.as_view()),  # 分类目录站列表
    url(r'^seek/$', Seek.as_view()),  # 分类目录站列表 搜索框
    url(r'^price/$', Price.as_view()),  # 分类目录价格请求
    url(r'^submitClassify/$', SubmitClassify.as_view()),  # 分类目录提交
    url(r'^resubmit/$', Resubmit.as_view()),  # 分类目录重新提交
    url(r'^catalogue/$', Catalogue.as_view()),  # 分类目录网站公示
    url(r'^consumption/$', Consumption.as_view()),  # 消费明细
    url(r'^information/$', Information.as_view()),  # 个人信息
    url(r'^amend/$', Amend.as_view()),  # 修改密码

]
