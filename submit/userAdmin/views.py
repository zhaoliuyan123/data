from django.db.models import Sum
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from package.token import user_admin, random_kai, create_token
from package.log import text
from login.models import *
from .models import *
import datetime
import time
import math
import json
import re


# 积分兑换统计
def financial(request):
    if request.method == "GET":
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
        close_sum = ClipClose.objects.filter(status=1).aggregate(integral_sum=Sum('integral'))
        if close_sum['integral_sum'] is None:
            data_sum = 0
        else:
            data_sum = close_sum['integral_sum']
        day_time = time.strftime("%Y-%m-%d")
        week_time = datetime.datetime.now() + datetime.timedelta(days=-7)
        month_time = datetime.datetime.now() + datetime.timedelta(days=-30)
        integral_list = []
        for x in [day_time, week_time, month_time]:
            close_day = ClipClose.objects.filter(status=1, conversion_time__gte=x).aggregate(
                integral_sum=Sum('integral'))
            if close_day['integral_sum'] is None:
                integral_list.append(0)
            else:
                integral_list.append(close_day['integral_sum'])
        return JsonResponse(
            {"state": 200,
             "data": {"sum": data_sum, "day": integral_list[0], "week": integral_list[1], "month": integral_list[2]}})


#  查看用户
def examine(request):
    if request.method == "GET":
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
        pages = request.GET.get('page', 1)
        page = int(pages)
        data_user = User.objects.all().values('id',
                                              'username',
                                              'register_time',
                                              'balance').order_by('-balance')
        try:
            data_count = data_user.count()
            if data_count < 1:
                return JsonResponse({"state": 200, "data": []})
            maximum = math.ceil(data_count / 10)
            if page > maximum:
                page = maximum
            if page < 1:
                page = 1
            p = Paginator(data_user, 10)
            data_list = p.page(page)
            dic_list = []
            for x in list(data_list):
                dic = {
                    'id': x['id'],  # id
                    'username': x['username'],  # 用户名
                    'register_time': x['register_time'],  # 注册时间
                    'balance': x['balance'],  # 积分余额
                }
                dic_list.append(dic)
        except Exception as e:
            text('查看用户', e)
            dic_list = []
        return JsonResponse({"state": 200, "data": dic_list, "count": data_count})


# 根据名条件查找用户
def locating(request):
    if request.method == "GET":
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
        page = int(request.GET.get('page', 1))  # 页数
        user_id = request.GET.get('id', False)
        user_name = request.GET.get('user_name', False)
        start_time = request.GET.get('start_time', False)  # 开始时间
        end_time = request.GET.get('end_time', False)  # 结束时间
        kes = {}
        if user_id:
            kes['id'] = int(user_id)
        if user_name:
            kes['username__icontains'] = user_name
        if start_time and end_time:
            start = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            kes["register_time__range"] = (start, end)
        data_user = User.objects.filter(**kes).values('id',
                                                      'username',
                                                      'register_time',
                                                      'total',
                                                      'balance').order_by('register_time')
        try:
            data_count = data_user.count()
            if data_count < 1:
                return JsonResponse({"state": 200, "data": []})
            maximum = math.ceil(data_count / 10)
            if page > maximum:
                page = maximum
            if page < 1:
                page = 1
            p = Paginator(data_user, 10)
            data_list = p.page(page)
            dic_list = []
            for x in list(data_list):
                dic = {
                    'id': x['id'],  # id
                    'username': x['username'],  # 用户名
                    'register_time': x['register_time'],  # 注册时间
                    'balance': x['balance'],  # 积分余额
                    'total': x['total'],  # 累计充值
                }
                dic_list.append(dic)
        except Exception as e:
            text('根据名条件查找用户', e)
            dic_list = []
        return JsonResponse({"state": 200, "data": dic_list, "count": data_count})


# 修改密码
def amend_password(request):
    if request.method == "POST":
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
        dic = json.loads(request.body)
        user_id = dic['id']
        new_password = dic['new_password']
        if not user_id or not new_password:
            return JsonResponse({"state": 403, "msg": "缺少参数"})
        else:
            user_id = int(user_id)
        user = User.objects.filter(id=user_id)
        if user.count() < 1:
            return JsonResponse({"state": 403, "msg": "没有此用户"})
        else:
            user[0].password = make_password(new_password)
            user[0].save()
            text('ID为：{} 用户名为：{}'.format(user[0].id, user[0].username), '修改密码成功')
            return JsonResponse({"state": 200, "msg": "修改成功"})


# 审核目录提交
def check(request):
    if request.method == "GET":
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
        page = int(request.GET.get('page', 1))
        status = int(request.GET.get('status', 0))
        if status == 0 or status == 1:
            sort = 'add_time'
        else:
            sort = '-accomplish_time'
        data_class = Classify.objects.filter(status=status).values('url',
                                                                   'id',
                                                                   'rates_name',
                                                                   'agentqq',
                                                                   'title',
                                                                   'keyword',
                                                                   'describe',
                                                                   'status',
                                                                   'accomplish_time',
                                                                   'add_time').order_by(sort)
        try:
            data_count = data_class.count()
            if data_count < 1:
                return JsonResponse({"state": 200, "data": []})
            maximum = math.ceil(data_count / 10)
            if page > maximum:
                page = maximum
            if page < 1:
                page = 1
            p = Paginator(data_class, 10)
            data_list = p.page(page)
        except Exception as e:
            text('审核目录提交1', e)
            return JsonResponse({"state": 200, "data": []})
        dic_list = []
        try:
            for x in list(data_list):
                dic = {
                    'id': x['id'],  # id
                    'url': x['url'],  # url
                    'rates_name': x['rates_name'],  # 收费标准
                    'agentqq': x['agentqq'],  # 站长qq
                    'title': x['title'],  # 网站标题
                    'keyword': x['keyword'],  # 关键字
                    'describe': x['describe'],  # 描述
                    'status': x['status'],  # 状态
                    'accomplish_time': re.sub(r'T', '', str(x['accomplish_time'])),  # 审核时间
                    'add_time': re.sub(r'T', '', str(x['add_time'])),  # 添加时间
                }
                dic_list.append(dic)
        except Exception as e:
            text('审核目录提交2', e)
            return JsonResponse({"state": 200, "data": []})
        return JsonResponse({"state": 200, "data": dic_list, "count": data_count})
    else:
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
        dic = json.loads(request.body)
        classify_id = int(dic['classify_id'])
        condition = int(dic['condition'])
        try:
            data_class = Classify.objects.get(id=classify_id)
        except Exception as e:
            text('分类目录post查询失败', e)
            return JsonResponse({"state": 403, "msg": "没有查到该ID"})
        data_class.status = condition
        if condition == 2 or condition == 3:
            data_class.accomplish_time = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            data_class.save()
        except Exception as e:
            text('分类目录数据库保存失败', e)
            return JsonResponse({"state": 403, "msg": "提交失败"})
        return JsonResponse({"state": 200, "msg": "修改成功"})


# 生成卡密
def create(request):
    if request.method == "GET":
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
        integral = int(request.GET.get('integral', 1))
        amount = int(request.GET.get('amount', 1))
        data_time = time.strftime("%Y-%m-%d %H:%M:%S")
        data_list = []
        try:
            for x in range(amount):
                close = random_kai()  # 随机生成卡密
                clip = ClipClose.objects.create(add_time=data_time,
                                                close=close,
                                                integral=integral)
                clip.save()
                dic = {
                    'add_time': re.sub(r'T', '', str(data_time)),  # 生成时间
                    'close': close,  # 卡密
                    'integral': integral,  # 额度
                }
                data_list.append(dic)
        except Exception as e:
            text('生成卡密2', e)
            return JsonResponse({"state": 403, "msg": "自动生成错误"})
        return JsonResponse({"state": 200, "data": data_list})


# 查看已激活卡密
def activated(request):
    if request.method == "GET":
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
        page = int(request.GET.get('page', 1))
        data_clip = ClipClose.objects.filter(status=1).values('conversion_time',
                                                              'close',
                                                              'integral',
                                                              'ago',
                                                              'later',
                                                              'user_id',
                                                              'user_name').order_by('-conversion_time')
        try:
            data_count = data_clip.count()
            if data_count < 1:
                return JsonResponse({"state": 200, "data": []})
            maximum = math.ceil(data_count / 10)
            if page > maximum:
                page = maximum
            if page < 1:
                page = 1
            p = Paginator(data_clip, 10)
            data_list = p.page(page)
        except Exception as e:
            text('查看已激活卡密1', e)
            return JsonResponse({"state": 200, "data": []})
        dic_list = []
        try:
            for x in list(data_list):
                dic = {
                    'conversion_time': re.sub(r'T', '', str(x['conversion_time'])),  # 兑换时间
                    'close': x['close'],  # 兑换卡密
                    'integral': x['integral'],  # 积分额度
                    'ago': x['ago'],  # 兑换之前积分
                    'later': x['later'],  # 兑换之后积分
                    'user_id': x['user_id'],  # 用户id
                    'user_name': x['user_name'],  # 用户名称
                }
                dic_list.append(dic)
        except Exception as e:
            text('查看已激活卡密2', e)
            return JsonResponse({"state": 200, "data": []})
        return JsonResponse({"state": 200, "data": dic_list, "count": data_count})


# 查看未激活卡密
def inactive(request):
    if request.method == "GET":
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
        page = int(request.GET.get('page', 1))
        data_clip = ClipClose.objects.filter(status=0).values('add_time',
                                                              'close',
                                                              'integral').order_by('-add_time')
        try:
            data_count = data_clip.count()
            if data_count < 1:
                return JsonResponse({"state": 200, "data": []})
            maximum = math.ceil(data_count / 10)
            if page > maximum:
                page = maximum
            if page < 1:
                page = 1
            p = Paginator(data_clip, 10)
            data_list = p.page(page)
        except Exception as e:
            text('未激活卡密1', e)
            return JsonResponse({"state": 200, "data": []})
        dic_list = []
        try:
            for x in list(data_list):
                dic = {
                    'add_time': re.sub(r'T', '', str(x['add_time'])),  # 创建时间
                    'close': x['close'],  # 兑换卡密
                    'integral': x['integral'],  # 积分额度
                }
                dic_list.append(dic)
        except Exception as e:
            text('未激活卡密2', e)
            return JsonResponse({"state": 200, "data": []})
        return JsonResponse({"state": 200, "data": dic_list, "count": data_count})


# 管理公告
def announcement(request):
    if request.method == "GET":
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
        notice_id = request.GET.get('notice_id', False)
        txt = request.GET.get('txt', False)
        if notice_id and txt:
            data_notice = Notice.objects.get(id=int(notice_id))
            data_notice.text = txt
            data_notice.save()
            return JsonResponse({"state": 200, "msg": "修改成功"})
        return JsonResponse({"state": 403, "msg": "没有notice_id"})
    else:
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
        dic = json.loads(request.body)
        terrace = dic['terrace']
        txt = dic['txt']
        data_time = time.strftime("%Y-%m-%d %H:%M:%S")
        data_notice = Notice.objects.create(add_time=data_time,
                                            text=txt,
                                            terrace=int(terrace))
        data_notice.save()
        return JsonResponse({"state": 200, "msg": "添加成功"})


# 删除公告
def announcement_del(request):
    if request.method == "GET":
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
        notice_id = request.GET.get('notice_id', False)
        if notice_id:
            Notice.objects.get(id=int(notice_id)).delete()
            return JsonResponse({"state": 200, "msg": "删除成功"})
        return JsonResponse({"state": 403, "msg": "没有notice_id"})


# 后台登陆
def login(request):
    if request.method == "POST":
        try:
            dic = json.loads(request.body)
            # 接收用户名
            username = dic["username"]
            # 接收用户密码
            password = dic["password"]
        except Exception as e:
            text('后台登陆1', e)
            return JsonResponse({"state": 403, "msg": "数据不完整"})
        try:
            # 如果用户或者密码为空
            if not username or not password:
                return JsonResponse({"state": 403, "msg": "数据不完整"})
            # 验证用户是否存在
            name = User.objects.filter(username=username, is_superuser=1)
            # 登录判断用户是否存在
            if name.count() < 1:
                return JsonResponse({"state": 403, "msg": "不存在该账户"})
            try:
                # 验证密码
                user = authenticate(username=username, password=password)
            except Exception as e:
                text('后台登陆2', e)
                return JsonResponse({"state": 403, "msg": "账号或密码错误"})
            if user is not None:
                text('后台登陆用户：', str(username))
                # 向redis中存储登陆信息'
                token = create_token(username)
                res = JsonResponse({
                    "state": 200, "msg": "登陆成功",
                    "data": {'token': token, 'username': username, 'reg': "退出"}
                })
                # 不设置 max_age时间  cookie默认为会话期有效
                res.set_cookie('username', username)
                res.set_cookie('user_id', name[0].id)
                res.set_cookie('token', token)
                res.set_cookie('islogin', True)
                return res
            else:
                return JsonResponse({"state": 403, "msg": "账号或密码错误"})
        except Exception as e:
            text('后台登陆3', e)
            return JsonResponse({"state": 403, "msg": "数据错误"})


def alter_price(request):
    if request.method == "GET":
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
        data_rates = Rates.objects.all()
        dic_list = []
        for x in data_rates:
            dic = {
                'id': x.id,  # id
                'rates': x.rates,  # 价格
                'rates_name': x.rates_name,  # 价格名称
            }
            dic_list.append(dic)
        return JsonResponse({"state": 200, "data": dic_list})
    else:
        data_admin = user_admin(request)
        if not data_admin:
            return JsonResponse({"state": 403, "msg": "没有访问权限"})
