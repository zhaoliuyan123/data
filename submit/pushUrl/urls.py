from django.conf.urls import url
from .views import *

app_name = '[pushUrl]'
urlpatterns = [
    url(r'^budget/$', budget),  # 预算
    url(r'^recharge/$', recharge),  # 充值
    url(r'^js_reception/$', js_reception),  # 百度JS文本提交
    url(r'^js_receptions/$', js_receptions),  # 百度JS手动提交
    url(r'^js_check/$', js_check),  # js查看提交记录
    url(r'^js_up/$', js_up),  # js重新提交
    url(r'^paw_reception/$', paw_reception),  # paw文本提交
    url(r'^paw_api/$', paw_api),  # paw的api管理和查看
    url(r'^paw_check/$', paw_check),  # paw的推送记录
    url(r'^paw_day/$', paw_day),  # paw管理 天级
    url(r'^paw_day_delete/$', paw_day_delete),  # pawpaw管理 天级删除
    url(r'^paw_day_add/$', paw_day_add),  # pawpaw管理 天级数据添加
    url(r'^paw_week/$', paw_week),  # paw管理 周级
    url(r'^paw_week_add/$', paw_week_add),  # paw管理周级数据添加
    # url(r'^paw_gather/$', paw_gather),  # paw自动采集地址修改
    url(r'^paw_alter/$', paw_alter),  # paw api信息修改
    url(r'^upload_record/$', upload_record),  # 上传记录
    url(r'^proclamation/$', proclamation),  # 公告

]
