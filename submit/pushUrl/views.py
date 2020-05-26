from django.http import JsonResponse
from django.db.models import Q, F
from package.token import get_username, username_id
from django.core.paginator import Paginator
from submit.settings import *
from package.log import text
from django.db import transaction
from login.models import *
from userAdmin.models import *
import json
import datetime
import time
import math
import os
import re


# 预算接口
def budget(request):
    if request.method == "GET":
        data_id = request.GET.get('id', 1)
        if not data_id:
            return JsonResponse({"state": 403, "msg": "id不存在"})
        data = PawVip.objects.filter(id=int(data_id))
        if data.count() < 1:
            return JsonResponse({"state": 403, "msg": "价格查询错误"})
        return JsonResponse({"state": 200, "budget": data[0].fund})


# 充值
def recharge(request):
    if request.method == "GET":
        try:
            token = request.COOKIES['token']
            close = request.GET.get('close', False)
        except Exception as e:
            text('百度js文本提交1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问"})
        if not close:
            return JsonResponse({"state": 403, "msg": "请输入卡密"})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "没有此用户"})
        data_name = User.objects.filter(id=user_id)[0]
        try:
            data_clip = ClipClose.objects.get(close=close, status=0)
        except Exception as e:
            text('卡密查询失败', e)
            return JsonResponse({"state": 403, "msg": "卡密错误"})
        data_time = time.strftime("%Y-%m-%d %H:%M:%S")
        balance = data_name.balance + data_clip.integral
        total = data_name.total + data_clip.integral
        data_clip.status = 1
        data_clip.conversion_time = data_time
        data_clip.ago = data_name.balance
        data_clip.later = balance
        data_clip.user_id = data_name.id
        data_clip.user_name = data_name.username
        data_name.balance = balance
        data_name.total = total
        try:
            data_name.save()
            data_clip.save()
            detail = Detail.objects.create(add_time=data_time,
                                           rates_name='卡密兑换',
                                           consume=data_clip.integral,
                                           balance=balance,
                                           status=1,
                                           username_id=data_name.id)
            detail.save()
        except Exception as e:
            text('卡密兑换提交错误用户{},卡密：{}'.format(data_name[0].id, close), e)
            return JsonResponse({"state": 403, "msg": "卡密兑换错误"})

        return JsonResponse({"state": 200, "msg": "兑换成功"})


# 百度js文本提交
def js_reception(request):
    if request.method == "POST":
        # 把文件保存到项目中一个叫做uploads的文件夹下面
        # file_ = os.path.join("uploads", files.name)
        # f = open(file_, "wb")
        try:
            token = request.COOKIES['token']
        except Exception as e:
            text('百度js文本提交1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        username = get_username(token)
        data_name = User.objects.filter(username=username).all()[0]
        if data_name.balance < 1:
            return JsonResponse({"state": 200, "msg": "账户余额不足！ 请充值", "balance": False})
        files = request.FILES.get("file")
        a = 0
        try:
            for txt in files:
                a += 1
                if a > 100000:
                    return JsonResponse({"state": 403, "msg": "数量超出上限！最多一次上传10万条", "balance": False})
        except Exception as e:
            text('百度js文本提交格式错误', e)
            return JsonResponse({"state": 403, "msg": "格式错误 上传失败", "balance": False})
        try:
            data_rates = Rates.objects.filter(id=1)[0]
            counts = a * data_rates.rates
            if data_name.balance < counts:
                difference = counts - data_name.balance
                return JsonResponse(
                    {"state": 200, "msg": "账户余额不足！ 缺少{}个币".format(difference), "balance": False})
        except Exception as e:
            text('百度js文本提交价格查询错误', e)
            return JsonResponse({"state": 403, "msg": "请求错误rates"})
        data_time = time.strftime("%Y-%m-%d %H:%M:%S")
        b = 0
        try:
            for txt in files:
                txt_str = txt.decode().strip()
                url = re.sub(r'[,|，]', '', txt_str)
                if 'http' not in url or len(url) > 100 or len(url) < 1:
                    continue
                try:
                    data_js = JsUrl.objects.create(url=url,
                                                   rates_id=data_rates.id,
                                                   rates_name=data_rates.rates_name,
                                                   add_time=data_time,
                                                   username_id=data_name.id,
                                                   )
                    data_js.save()
                    b += 1
                except Exception as e:
                    text('百度js文本提交2' + data_name.username, e)
                    continue
        except Exception as e:
            text('百度js文本提交3', e)
        consume = b * data_rates.rates
        data_name.balance = data_name.balance - consume
        data_name.save()
        c = a - b
        uploading = UploadingRecord.objects.create(counts=a,
                                                   correct=b,
                                                   error=c,
                                                   add_time=data_time,
                                                   uploading_explain='百度JS文本上传',
                                                   username_id=data_name.id)

        deta_deta = Detail.objects.create(counts=0,
                                          correct=0,
                                          consume=consume,
                                          balance=data_name.balance,
                                          username_id=data_name.id,
                                          add_time=data_time,
                                          rates_name=data_rates.rates_name)
        deta_deta.save()
        uploading.save()
        return JsonResponse(
            {"state": 200, "msg": "上传成功", "balance": True})


# js手动提交
def js_receptions(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            token = request.COOKIES['token']
        except Exception as e:
            text('js手动提交1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        username = get_username(token)
        data_name = User.objects.filter(username=username).all()[0]
        if data_name.balance < 1:
            return JsonResponse({"state": 200, "msg": "账户余额不足！ 请充值", "balance": False})
        data_list = data['url_list']
        url_list = re.sub('http', ',http', data_list).split(',')
        if len(url_list) < 2:
            return JsonResponse({"state": 403, "msg": "至少上传1条url", "balance": False})
        a = 0
        for x in url_list:
            a += 1
            if a > 1000:
                return JsonResponse({"state": 200, "msg": "数量超出上限！最多一次上传1千条", "balance": False})
        data_rates = Rates.objects.get(id=1)
        counts = a * data_rates.rates
        if data_name.balance < counts:
            difference = counts - data_name.balance
            return JsonResponse(
                {"state": 200, "msg": "账户余额不足！ 缺少{}个币".format(difference), "balance": False})
        data_time = time.strftime("%Y-%m-%d %H:%M:%S")
        b = 0
        print(url_list)
        for x in url_list:
            url = re.sub(r'[,|，]', '', x)
            if 'http' not in url or len(url) > 100 or len(url) < 1:
                continue
            try:
                data_js = JsUrl.objects.create(url=url,
                                               rates_id=data_rates.id,
                                               rates_name=data_rates.rates_name,
                                               add_time=data_time,
                                               username_id=data_name.id,
                                               )
                data_js.save()
                b += 1
            except Exception as e:
                text('js手动提交2' + data_name.username, e)
                continue
        consume = b * data_rates.rates
        data_name.balance = data_name.balance - consume
        data_name.save()
        c = a - b
        uploading = UploadingRecord.objects.create(counts=a,
                                                   correct=b,
                                                   error=c,
                                                   add_time=data_time,
                                                   uploading_explain='百度JS手动上传',
                                                   username_id=data_name.id)
        deta_deta = Detail.objects.create(counts=0,
                                          correct=0,
                                          consume=consume,
                                          balance=data_name.balance,
                                          username_id=data_name.id,
                                          add_time=data_time,
                                          rates_name=data_rates.rates_name)
        deta_deta.save()
        uploading.save()
        return JsonResponse(
            {"state": 200, "msg": "上传成功", "balance": True})


# js查看提交记录
def js_check(request):
    if request.method == "GET":
        try:
            page = int(request.GET.get('page', 1))
            token = request.COOKIES['token']
        except Exception as e:
            text('js查看提交记录1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        user = username_id(token)
        if not user:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        try:
            data_js = JsUrl.objects.filter(username_id=user).values('id',
                                                                    'url',
                                                                    'add_time',
                                                                    'accomplish_time',
                                                                    'status',
                                                                    'rates_name',
                                                                    ).order_by('-add_time')
            data_count = data_js.count()
            if data_count < 1:
                return JsonResponse({"state": 200, "data": []})
            maximum = math.ceil(data_count / 10)
            if page > maximum:
                page = maximum
            if page < 1:
                page = 1
            p = Paginator(data_js, 10)
            data_list = p.page(page)
            dic_list = []
            for x in list(data_list):
                dic = {
                    'id': x['id'],  # id
                    'url': x['url'],  # 网站
                    'add_time': x['add_time'],  # 添加时间
                    'accomplish_time': x['accomplish_time'],  # 完成时间
                    'status': x['status'],  # 状态
                    'rates_name': x['rates_name'],  # 套餐
                }
                dic_list.append(dic)
        except Exception as e:
            text('js查看提交记录2', e)
            dic_list = []
        return JsonResponse({"state": 200, "data": dic_list, "count": data_count})


# js重新提交
def js_up(request):
    if request.method == "GET":
        try:
            js_id = request.GET.get('id', False)
            token = request.COOKIES['token']
        except Exception as e:
            text('分类目录重新提交1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        if not js_id:
            text('分类目录重新提交2', js_id)
            return JsonResponse({"state": 403, "msg": "id不存在"})
        user = username_id(token)
        if not user:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        data_js = JsUrl.objects.get(id=int(js_id))
        if data_js.status == 0:
            return JsonResponse({"state": 200, "msg": '请等待审核'})
        if data_js.status == 1:
            return JsonResponse({"state": 200, "msg": '审核中 请等待'})
        if data_js.status == 2:
            return JsonResponse({"state": 200, "msg": '审核已通过'})
        if data_js.status == 3:
            data_js.status = 0
            data_js.save()
            return JsonResponse({"state": 200, "msg": '重新提交成功！'})


# paw文本提交
def paw_reception(request):
    if request.method == "POST":
        # 把文件保存到项目中一个叫做uploads的文件夹下面
        # file_ = os.path.join("uploads", files.name)
        # f = open(file_, "wb")
        try:
            token = request.COOKIES['token']
            data_dic = request.POST.dict()
            month = int(data_dic['month'])  # 选择时间
            present = int(data_dic['present'])  # 提交方式
            print(month)
            print(present)
            if not present:
                return JsonResponse({"state": 403, "msg": "请选择提交方式", "balance": False})
            if present == 1:
                files = data_dic['import_files']
                files_name = '手动输入'
                paw_record = '熊掌手动上传'
                files = re.sub('http', ',http', files).split(',')
                if len(files) < 2:
                    return JsonResponse({"state": 403, "msg": "至少上传1条url", "balance": False})
            if present == 2:
                files = request.FILES.get("file")
                files_name = files.name
                if 'txt' not in files_name:
                    return JsonResponse({"state": 403, "msg": "请上传txt文件类型", "balance": False})
                paw_record = '熊掌文本上传'
        except Exception as e:
            text('paw文本提交1', e)
            print(e)
            return JsonResponse({"state": 403, "msg": "参数错误", "referer": request.get_full_path()})
        if not month:
            return JsonResponse({"state": 403, "msg": "请选择套餐", "balance": False})
        username = get_username(token)
        data_name = User.objects.filter(username=username).all()[0]
        try:
            data_rates = PawVip.objects.get(id=month)
        except Exception as e:
            text('paw month查询不存在', e)
            return JsonResponse({"state": 403, "msg": "month不存在"})
        if data_name.balance < data_rates.fund:
            return JsonResponse({"state": 403, "msg": "账户余额不足！ 请充值", "balance": False})
        rank = int(data_dic['rank'])
        domain_url = data_dic['domain_url']
        api = data_dic['api']
        url_download = data_dic['url_download']
        if not rank or not domain_url or not api:
            return JsonResponse({"state": 403, "msg": "参数缺少", "balance": False})
        api_id = re.findall('appid=(.*?)&', api)[0]
        if not api_id:
            return JsonResponse({"state": 403, "msg": "API接口填写错误", "balance": False})
        api_data = Paws.objects.filter(api=api).count()
        if api_data != 0:
            return JsonResponse({"state": 403, "msg": "API接口已存在", "balance": False})
        data_time = time.strftime("%Y-%m-%d %H:%M:%S")
        # 天级
        if rank == 1:
            a = 0
            try:
                for txt in files:
                    a += 1
                    if a > 30000:
                        return JsonResponse({"state": 403, "msg": "数量超出上限！天级最多上传三万url条", "balance": False})
            except Exception as e:
                text('paw天级文本提交格式错误1', e)
                return JsonResponse({"state": 403, "msg": "格式错误 上传失败", "balance": False})
            try:
                vip_time = datetime.datetime.now() + datetime.timedelta(days=data_rates.fund)
                data_paw = Paws.objects.create(add_time=data_time,
                                               domain_url=domain_url,
                                               api=api,
                                               rank=rank,
                                               file=files_name,
                                               vip_time=vip_time,
                                               present=present,
                                               rates_name=data_rates.vip_name,
                                               user_id=data_name.id)
                data_name.balance = data_name.balance - data_rates.fund
                with transaction.atomic():
                    data_paw.save()
                    data_name.save()
                # with transaction.atomic():  # 在执行上下文里面的内容时候时，遇到错误执行回滚操作，类似mysql回滚函数
                b = 0
                for url in files:
                    if type(url) != str:
                        url = re.sub(r'[,|，]', '', url.decode().strip())
                    if 'http' not in url or len(url) > 100 or len(url) < 1:
                        continue
                    try:
                        data_day = Day.objects.create(add_time=data_time,
                                                      domain_url=domain_url,
                                                      url=url,
                                                      paw_id=data_paw.id,
                                                      username_id=data_name.id
                                                      )
                        data_day.save()
                        b += 1
                    except Exception as e:
                        text('paw天级提交失败错误2' + data_name.username, e)
                        continue
            except Exception as e:
                text('paw天级数据库提交失败错误3', e)
                return JsonResponse({"state": 403, "msg": "格式错误 上传失败", "balance": False})

        # 周级
        else:
            try:
                if present == 2:
                    files_name = files.name
                if present == 3:
                    files_name = '自动生成'
                    paw_record = '熊掌自动生成上传'
                    a = 0
                    b = 0
                if present == 4:
                    files_name = url_download
                    paw_record = '熊掌自动采集上传'
                    a = 0
                    b = 0
            except Exception as e:
                text('paw周级文件写入失败错误1', e)
                return JsonResponse({"state": 403, "msg": "格式错误 上传失败", "balance": False})

            try:
                vip_time = datetime.datetime.now() + datetime.timedelta(days=data_rates.fund)
                data_paw = Paws.objects.create(add_time=data_time,
                                               domain_url=domain_url,
                                               api=api,
                                               rank=rank,
                                               file=files_name,
                                               present=present,
                                               vip_time=vip_time,
                                               rates_name=data_rates.vip_name,
                                               user_id=data_name.id)
                data_name.balance = data_name.balance - data_rates.fund
                with transaction.atomic():
                    data_paw.save()
                    data_name.save()
            except Exception as e:
                text('paw周级数据库提交失败错误3', e)
                return JsonResponse({"state": 403, "msg": "格式错误 上传失败", "balance": False})
            data_dir = os.path.join(os.path.join(BASE_DIR, 'static/data'))
            f = open(os.path.join(data_dir, '{}.txt'.format(data_paw.id)), 'wb+')
            a = 0
            b = 0
            for txt in files:
                a += 1
                add = 1
                if type(txt) != str:
                    url = re.sub(r'[,|，]', '', txt.decode().strip())
                    if 'http' not in url or len(url) > 100 or len(url) < 1:
                        add = 0
                if add == 0:
                    continue
                f.write(txt)
                b += 1
            f.close()
        c = a - b
        uploading = UploadingRecord.objects.create(counts=a,
                                                   correct=b,
                                                   error=c,
                                                   add_time=data_time,
                                                   uploading_explain=paw_record,
                                                   username_id=data_name.id)
        deta = Detail.objects.create(counts=0,
                                     correct=0,
                                     consume=data_rates.fund,
                                     balance=data_name.balance,
                                     username_id=data_name.id,
                                     add_time=data_time,
                                     rates_name=data_rates.vip_name)
        uploading.save()
        deta.save()
        return JsonResponse(
            {"state": 200, "msg": "上传成功", "balance": True})


# 　查看api提交记录
def paw_api(request):
    if request.method == "GET":
        try:
            token = request.COOKIES['token']
            page = int(request.GET.get('page', 1))
        except Exception as e:
            text('查看api提交记录1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        data = Paws.objects.filter(user_id=user_id).values('id',
                                                           'add_time',
                                                           'domain_url',
                                                           'status',
                                                           'api',
                                                           'rank',
                                                           'file',
                                                           'present',
                                                           'rates_name',
                                                           'vip_time', ).order_by('-add_time')
        data_count = data.count()
        if data_count < 1:
            return JsonResponse({"state": 200, "data": []})
        try:
            maximum = math.ceil(data_count / 10)
            if page > maximum:
                page = maximum
            if page < 1:
                page = 1
            p = Paginator(data, 10)
            data_list = p.page(page)
            dic_list = []
            for x in list(data_list):
                api = re.findall('appid=(.*?)&', x['api'])[0]
                if int(x['present']) == 4:
                    if len(x['file']) < 1:
                        file = x['file']
                    else:
                        file_list = x['file'].split('/')
                        for file_s in file_list:
                            if '.' in file_s:
                                file = file_s
                else:
                    file = x['file']
                dic = {
                    'id': x['id'],  # id
                    'add_time': x['add_time'],  # 添加时间
                    'domain_url': x['domain_url'],  # 绑定域名链接
                    'status': x['status'],  # API接口状态
                    'api': api,  # API接口id
                    'rank': x['rank'],  # 熊掌级别
                    'file': file,  # 文件名称
                    'present': x['present'],  # 提交方式
                    'rates_name': x['rates_name'],  # 收费标准
                    'vip_time': x['vip_time'],  # 到期时间
                }
                dic_list.append(dic)
        except Exception as e:
            text('查看api提交记录2', e)
            dic_list = []
        return JsonResponse({"state": 200, "data": dic_list, "count": data_count})


#  paw的推送记录
def paw_check(request):
    if request.method == "GET":
        try:
            token = request.COOKIES['token']
            page = int(request.GET.get('page', 1))
            paw_id = request.GET.get('paw_id', False)
        except Exception as e:
            text('paw的推送记录1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        data_paw = PawPush.objects.filter(api_id=int(paw_id)).values('add_time',
                                                                     'domain_url',
                                                                     'url',
                                                                     'api',
                                                                     'rank',
                                                                     'consume',
                                                                     'balance').order_by('-add_time')
        try:
            data_count = data_paw.count()
            if data_count < 1:
                return JsonResponse({"state": 200, "data": []})
            maximum = math.ceil(data_count / 10)
            if page > maximum:
                page = maximum
            if page < 1:
                page = 1
            p = Paginator(data_paw, 10)
            data_list = p.page(page)
            dic_list = []
            for x in list(data_list):
                api = re.findall('appid=(.*?)&', x['api'])[0]
                dic = {
                    'add_time': x['add_time'],  # 推送时间
                    'domain_url': x['domain_url'],  # 绑定域名链接
                    'api': api,  # API接口id
                    'rank': x['rank'],  # 熊掌级别
                    'url': x['url'],  # 推送url
                    'consume': x['consume'],  # 提交成功数
                    'balance': x['balance'],  # 剩余次数
                }
                dic_list.append(dic)
        except Exception as e:
            text('paw的推送记录2', e)
            dic_list = []
    return JsonResponse({"state": 200, "data": dic_list, "count": data_count})


#  paw的天级管理
def paw_day(request):
    if request.method == "GET":
        try:
            token = request.COOKIES['token']
            paw_id = request.GET.get('paw_id', False)
            page = int(request.GET.get('page', 1))
        except Exception as e:
            text('paw的天级管理', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        data_day = Day.objects.filter(paw_id=int(paw_id)).values('add_time',
                                                                 'id',
                                                                 'accomplish_time',
                                                                 'domain_url',
                                                                 'paw__api',
                                                                 'url',
                                                                 'status',
                                                                 'paw__rank').order_by('-accomplish_time')
        try:
            data_count = data_day.count()
            if data_count < 1:
                return JsonResponse({"state": 200, "data": []})
            maximum = math.ceil(data_count / 10)
            if page > maximum:
                page = maximum
            if page < 1:
                page = 1
            p = Paginator(data_day, 10)
            data_list = p.page(page)
            dic_list = []
            for x in list(data_list):
                api = re.findall('appid=(.*?)&', x['paw__api'])[0]
                dic = {
                    'id': x['id'],
                    'add_time': x['add_time'],  # 添加时间
                    'accomplish_time': x['accomplish_time'],  # 推送完成时间
                    'domain_url': x['domain_url'],  # 绑定域名链接
                    'api': api,  # API接口id
                    'url': x['url'],  # 推送url
                    'status': x['status'],  # 推送状态
                    'rank': x['paw__rank'],  # 熊掌等级
                }
                dic_list.append(dic)
        except Exception as e:
            text('paw的天级管理2', e)
            dic_list = []
    return JsonResponse({"state": 200, "data": dic_list, "count": data_count, "paw_id": paw_id})


# paw_day_delete管理 天级删除
def paw_day_delete(request):
    if request.method == "GET":
        try:
            token = request.COOKIES['token']
            day_id = request.GET.get('day_id', False)
        except Exception as e:
            text('paw天级删除1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        try:
            Day.objects.get(username_id=user_id, id=int(day_id)).delete()
        except Exception as e:
            text('paw天级删除2', e)
            return JsonResponse({"state": 403, "msg": "操作错误"})

        return JsonResponse({"state": 200, "msg": "删除成功！"})


# paw_day_add管理 天级添加
def paw_day_add(request):
    if request.method == "POST":
        try:
            token = request.COOKIES['token']
            data_dic = request.POST.dict()
            paw_id = int(data_dic['paw_id'])  # paw_id
            present = int(data_dic['present'])  # 提交方式
        except Exception as e:
            text('paw天级添加数据接收参数错误', e)
            return JsonResponse({"state": 403, "msg": "参数错误", "referer": request.get_full_path()})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        data_paw = Paws.objects.filter(id=paw_id, user_id=user_id)
        if data_paw.count() < 1:
            return JsonResponse({"state": 403, "msg": "不存在该paw_id"})
        data_time = time.strftime("%Y-%m-%d %H:%M:%S")
        if present == 1:
            files = data_dic['import_files']
            files = re.sub('http', ',http', files).split(',')
            if len(files) < 2:
                return JsonResponse({"state": 200, "msg": "至少上传1条url", "balance": False})
        else:
            if present == 2:
                files = request.FILES.get("file")
        a = 0
        try:
            for txt in files:
                a += 1
                if a > 30000:
                    return JsonResponse({"state": 403, "msg": "数量超出上限！天级最多上传三万url条", "balance": False})
        except Exception as e:
            text('paw天级添加数据格式错误1', e)
            return JsonResponse({"state": 403, "msg": "格式错误 上传失败", "balance": False})
        b = 0
        for url in files:
            if type(url) != str:
                url = re.sub(r'[,|，]', '', url.decode().strip())
            if 'http' not in url or len(url) > 100 or len(url) < 1:
                continue
            try:
                data_day = Day.objects.create(add_time=data_time,
                                              domain_url=data_paw[0].domain_url,
                                              url=url,
                                              paw_id=paw_id,
                                              username_id=user_id
                                              )
                data_day.save()
                b += 1
            except Exception as e:
                text('paw天级添加数据错误2', e)
                continue
        c = a - b
        uploading = UploadingRecord.objects.create(counts=a,
                                                   correct=b,
                                                   error=c,
                                                   add_time=data_time,
                                                   uploading_explain='熊掌天级添加数据',
                                                   username_id=user_id)
        uploading.save()
        return JsonResponse({"state": 200, "data": "上传成功！"})


# paw_week管理 周级
def paw_week(request):
    if request.method == "GET":
        try:
            token = request.COOKIES['token']
            paw_id = request.GET.get('paw_id', False)
        except Exception as e:
            text('paw管理 周级', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        try:
            data_paw = Paws.objects.filter(id=int(paw_id), user_id=user_id)[0]
        except Exception as e:
            text('paw_id查询错误', e)
            return JsonResponse({"state": 403, "msg": "paw_id查询错误"})
        api = re.findall('appid=(.*?)&', data_paw.api)[0]
        try:
            dic = {
                'add_time': data_paw.add_time,  # 添加时间
                'domain_url': data_paw.domain_url,  # 绑定域名链接
                'api': api,  # API接口id
                'rank': data_paw.rank,  # 熊掌等级
                'file': data_paw.file,  # 文件名称
            }
        except Exception as e:
            text('paw管理 周级2', e)
            dic = []
        return JsonResponse({"state": 200, "data": [dic], "paw_id": paw_id})


# paw_week_add管理周级文件替换
def paw_week_add(request):
    if request.method == "POST":
        try:
            token = request.COOKIES['token']
            data_dic = request.POST.dict()
            paw_id = int(data_dic['paw_id'])  # paw_id
        except Exception as e:
            text('paw管理 周级', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        data_paw = Paws.objects.filter(id=paw_id, user_id=user_id)
        if data_paw.count() < 1:
            return JsonResponse({"state": 403, "msg": "不存在paw_id"})
        files = request.FILES.get("file")
        files_name = files.name
        data_dir = os.path.join(os.path.join(BASE_DIR, 'static/data'))
        f = open(os.path.join(data_dir, '{}.txt'.format(data_paw[0].id)), 'wb+')
        a = 0
        b = 0
        try:
            for txt in files:
                a += 1
                add = 1
                if type(txt) != str:
                    url = re.sub(r'[,|，]', '', txt.decode().strip())
                    if 'http' not in url or len(url) > 100 or len(url) < 1:
                        add = 0
                if add == 0:
                    continue
                f.write(txt)
                b += 1
            f.close()
        except Exception as e:
            text('paw管理周级文件替换,文件写入错误', e)
            return JsonResponse({"state": 403, "msg": "写入错误"})
        data_paw[0].file = files_name
        try:
            data_paw[0].save()
            c = a - b
            data_time = time.strftime("%Y-%m-%d %H:%M:%S")
            uploading = UploadingRecord.objects.create(counts=a,
                                                       correct=b,
                                                       error=c,
                                                       add_time=data_time,
                                                       uploading_explain='熊掌周级添加数据',
                                                       username_id=user_id)
            uploading.save()
        except Exception as e:
            text('paw管理周级文件替换,保存错误', e)
            return JsonResponse({"state": 403, "msg": "保存错误"})
        return JsonResponse({"state": 200, "msg": "上传成功！"})


# paw_gather 自动采集地址修改
def paw_gather(request):
    if request.method == "GET":
        try:
            token = request.COOKIES['token']
        except Exception as e:
            text('自动采集地址修改', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问"})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        paw_id = request.GET.get('paw_id', False)
        try:
            data_paw = Paws.objects.get(user_id=user_id, id=int(paw_id))
        except Exception as e:
            text('get修改API信息查询错误', e)
            return JsonResponse({"state": 403, "msg": "查询错误"})
        dic = {
            'api': data_paw.api,
            'domain_url': data_paw.domain_url,
            'gather': data_paw.file
        }
        return JsonResponse({"state": 200, "data": dic, "paw_id": paw_id})
    else:
        try:
            token = request.COOKIES['token']
        except Exception as e:
            text('修改API1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问"})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        dic = json.loads(request.body)
        api = dic['api']
        domain_url = dic['domain_url']
        gather = dic['gather']
        paw_id = dic['paw_id']
        if not gather or not paw_id or not domain_url or not api:
            return JsonResponse({"state": 403, "msg": "缺少参数"})
        api_id = re.findall('appid=(.*?)&', api)[0]
        if not api_id:
            return JsonResponse({"state": 403, "msg": "API接口填写错误", "balance": False})
        try:
            data_paw = Paws.objects.get(id=int(paw_id), user_id=user_id, present=4)
        except Exception as e:
            text('post自动采集地址修改查询失败', e)
            return JsonResponse({"state": 403, "msg": "查询失败"})
        data_paw.file = gather
        data_paw.api = api
        data_paw.domain_url = domain_url
        data_paw.save()
        return JsonResponse({"state": 200, "msg": "修改成功"})


# api信息修改
def paw_alter(request):
    if request.method == "GET":
        try:
            token = request.COOKIES['token']
        except Exception as e:
            text('get api信息修改1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问"})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        paw_id = request.GET.get('paw_id', False)
        present = request.GET.get('present', False)
        try:
            data_paw = Paws.objects.get(user_id=user_id, id=int(paw_id))
        except Exception as e:
            text('get api信息修改修改API信息查询错误', e)
            return JsonResponse({"state": 403, "msg": "查询错误"})
        if int(present) == 4:
            dic = {
                'api': data_paw.api,
                'domain_url': data_paw.domain_url,
                'gather': data_paw.file,
            }
        else:
            dic = {
                'api': data_paw.api,
                'domain_url': data_paw.domain_url
            }
        return JsonResponse({"state": 200, "data": dic, "paw_id": paw_id, "present": present})

    else:
        try:
            token = request.COOKIES['token']
        except Exception as e:
            text('post 修改API1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问"})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        dic = json.loads(request.body)
        api = dic['api']
        domain_url = dic['domain_url']
        paw_id = dic['paw_id']
        gather = dic['gather']
        present = dic['present']
        if not api or not domain_url or not paw_id:
            return JsonResponse({"state": 403, "msg": "缺少参数"})
        if not present:
            return JsonResponse({"state": 403, "msg": "缺少参数present"})
        api_id = re.findall('appid=(.*?)&', api)[0]
        if not api_id:
            return JsonResponse({"state": 403, "msg": "API接口填写错误", "balance": False})
        try:
            data_paw = Paws.objects.filter(id=int(paw_id), user_id=user_id)[0]
        except Exception as e:
            text('post api修改paw_id查询错误', e)
            return JsonResponse({"state": 403, "msg": "paw_id查询错误"})
        data_paw.domain_url = domain_url
        data_paw.api = api
        if int(present) == 4:
            data_paw.file = gather
        try:
            data_paw.save()
        except Exception as e:
            text('api修改失败', e)
            return JsonResponse({"state": 403, "msg": "修改失败 请重试！"})
        return JsonResponse({"state": 200, "msg": "修改成功"})


# 上传记录
def upload_record(request):
    if request.method == "GET":
        try:
            token = request.COOKIES['token']
            page = int(request.GET.get('page', 1))
        except Exception as e:
            text('上传记录1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        uploading = UploadingRecord.objects.filter(username_id=user_id).values('uploading_explain',
                                                                               'counts',
                                                                               'correct',
                                                                               'error',
                                                                               'add_time').order_by('-add_time')
        try:
            data_count = uploading.count()
            if data_count < 1:
                return JsonResponse({"state": 200, "data": []})
            maximum = math.ceil(data_count / 10)
            if page > maximum:
                page = maximum
            if page < 1:
                page = 1
            p = Paginator(uploading, 10)
            data_list = p.page(page)
            dic_list = []
            for x in list(data_list):
                dic = {
                    'uploading_explain': x['uploading_explain'],  # 上传说明
                    'counts': x['counts'],  # 总数量
                    'correct': x['correct'],  # 上传成功数量
                    'error': x['error'],  # 失败数量
                    'add_time': x['add_time'],  # 时间
                }
                dic_list.append(dic)
        except Exception as e:
            text('上传记录2', e)
            dic_list = []
        return JsonResponse({"state": 200, "data": dic_list, "count": data_count})


# 公告
def proclamation(request):
    if request.method == "GET":
        # 1 分类目录免责说明
        # 2 分类目录使用说明
        # 3 百度推送说明
        # 4 百度熊掌推送说明
        # 5 百度JS推送说明
        terrace = int(request.GET.get('terrace', 1))
        data_notice = Notice.objects.filter(terrace=terrace)
        dic_list = []
        a = 0
        for x in data_notice:
            a += 1
            dic = {
                'id': x.id,
                'add_time': x.add_time,
                'text': '{}. {}'.format(a, x.text)
            }
            dic_list.append(dic)
        return JsonResponse({"state": 200, "data": dic_list})

