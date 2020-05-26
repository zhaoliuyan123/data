from django.conf.urls import url
from .views import *

app_name = '[userAdmin]'

urlpatterns = [
    url(r'^financial/$', financial),  # 积分兑换统计
    url(r'^examine/$', examine),  # 查看所有用户
    url(r'^locating/$', locating),  # 根据名条件查找用户
    url(r'^amend/$', amend_password),  # 修改密码
    url(r'^check/$', check, ),  # 审核目录提交
    url(r'^create/$', create),  # 生成卡密
    url(r'^activated/$', activated),  # 查看已激活卡密
    url(r'^inactive/$', inactive),  # 查看未激活卡密
    url(r'^announcement/$', announcement),  # 管理公告
    url(r'^announcement_del/$', announcement_del),  # 删除公告
    url(r'^login/$', login),  # 后台登陆
    # url(r'^alter_price/$', alter_price)  # 价格修改
]
