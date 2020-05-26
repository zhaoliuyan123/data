from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.generic import View
from .models import *
from submit.settings import *
from package.log import *
from package.token import create_token, get_username, username_id
from io import BytesIO
from PIL import ImageDraw, Image, ImageFont
import json
import datetime
import time
import random
import re
import math


# 图片验证码
class get_verify_img(View):

    def get_random_color(self):
        R = random.randrange(255)
        G = random.randrange(255)
        B = random.randrange(255)
        return (R, G, B)

    # 生个图片验证码
    def get(self, request):
        # uuid
        uuid = request.GET['uuid']
        if not uuid:
            return JsonResponse({"state": 403, "msg": "uuid错误"})
        print(uuid, '标识码')
        try:
            # 定义画布背景颜色
            bg_color = self.get_random_color()
            # 画布大小
            img_size = (130, 70)
            # 定义画布
            image = Image.new("RGB", img_size, bg_color)
            # 定义画笔
            draw = ImageDraw.Draw(image, "RGB")
            # 创建字体（字体的路径，服务器路径
            if windwos == True:
                # windwos使用这个字体地址
                font_path = windwos_typeface_path
            else:
                # linux使用这个字体地址
                font_path = linux_typeface_path  # 系统存放字体样式的地址，指定一种字体
            # 实例化字体，设置大小是30
            font = ImageFont.truetype(font_path, 30)
            # 准备画布上的字符集
            source = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789"
            # 保存每次随机出来的字符
            code_str = ""
            for i in range(4):
                # 获取数字随机颜色
                text_color = self.get_random_color()
                # 获取随机数字 len
                tmp_num = random.randrange(len(source))
                # 获取随机字符 画布上的字符集
                random_str = source[tmp_num]
                # 将每次随机的字符保存（遍历） 随机四次
                code_str += random_str
                # 将字符画到画布上
                draw.text((10 + 30 * i, 20), random_str, text_color, font)
            # 记录给哪个请求发了什么验证码
            conn = settings.REDIS_CONN
            code_str = code_str.lower()
            conn.setex(uuid, 60 * 5, code_str)
            print(code_str, '验证码')
            # 使用画笔将文字画到画布上
            # draw.text((10, 20), "X", text_color, font)
            # draw.text((40, 20), "Q", text_color, font)
            # draw.text((60, 20), "W", text_color, font)
            # 获得一个缓存区
            buf = BytesIO()
            # 将图片保存到缓存区
            image.save(buf, 'png')
            # 将缓存区的内容返回给前端 .getvalue 是把缓存区的所有数据读取
            return HttpResponse(buf.getvalue(), 'image/png')
        except Exception as e:
            text("图片验证码生成错误", e)
            return JsonResponse({"state": 403, "msg": "图片验证码生成错误", "verif": False})


# 注册
class Register(View):

    def get(self, request):
        pass
        #     if request.method == 'GET':
        #         print('aaaaaa')
        #         return JsonResponse({"state": 403, "msg": "用户名或密码位数错误，请注意长度"})

    def post(self, request):
        dic = json.loads(request.body)
        try:
            username = dic['username']  # 用户名
            password = dic['password']  # 密码
            email = dic['email']
            uuid = dic['uuid']
            yzm = dic['yzm']
        except Exception as e:
            text('注册', "用户注册缺少参数" + str(e))
            return JsonResponse({"state": 403, "msg": "缺少参数"})
        # username = request.GET.get('username', False)
        # password = request.GET.get('password', False)
        # email = request.GET.get('email', False)
        # uuid = request.GET.get('uuid', False)
        # yzm = request.GET.get('yzm', False)
        if len(username) > 20 or len(password) > 20 or len(username) < 6 or len(password) < 6:
            return JsonResponse({"state": 403, "msg": "用户名或密码位数错误，请注意长度"})
        passwords = make_password(password)
        if not (username and password):
            text('注册', "用户注册缺少参数")
            return JsonResponse({"state": 403, "msg": "缺少参数"})
        try:
            # 判断缓存里有没有这个验证码
            conn = settings.REDIS_CONN
            yzm1 = conn.get(uuid).decode()
        except Exception as e:
            yzm1 = '错误'
            text('注册验证码错误', e)
        print('验证码', yzm, '缓存验证码', yzm1)
        if yzm != yzm1:
            return JsonResponse({"state": 403, "msg": "验证码错误"})
        usernames = User.objects.filter(username=username).count()
        if usernames > 0:
            return JsonResponse({"state": 403, "msg": "此用户已被注册！"})
        times = time.strftime("%Y-%m-%d %H:%M:%S")
        user = User.objects.create(username=username,
                                   password=passwords,
                                   email=email,
                                   register_time=times,
                                   vip_time=times)
        try:
            user.save()
        except Exception as e:
            text('注册错误', e)
            return JsonResponse({"state": 403, "msg": "注册错误"})
        text(username, "用户注册成功")
        return JsonResponse({"state": 200, "msg": "注册成功"})


# 登陆
class Login(View):

    # COOKIES登录
    def get(self, request):
        pass
        #     try:
        #         name = request.COOKIES['user_id']
        #     except:
        #         return JsonResponse({"state": 403, "msg": "用户未登陆!!!"})
        #     try:
        #         conn = settings.REDIS_CONN
        #         r = conn.get('user_id').decode()
        #         print(r)
        #     except:
        #         return JsonResponse({"state": 403, "msg": "用户未登陆!!!"})
        #     text(name, "登录成功！")
        #     return JsonResponse({"state": 200, "msg": "用户登陆成功"})
        #
        # # 输入账号密码登录

    def post(self, request, expire=None):
        try:
            dic = json.loads(request.body)
            # 接收用户名
            username = dic["username"]
            # 接收用户密码
            password = dic["password"]
            # username = request.GET.get('username', False)
            # password = request.GET.get('password', False)
            print(username)
            print(password)
        except Exception as e:
            text('注册1', e)
            return JsonResponse({"state": 403, "msg": "数据不完整"})
        try:
            # 如果用户或者密码为空
            if not username or not password:
                return JsonResponse({"state": 403, "msg": "数据不完整"})
            # 验证用户是否存在
            name = User.objects.filter(username=username)
            # 登录判断用户是否存在
            if not name:
                print("不存在该账户！！1")
                return JsonResponse({"state": 403, "msg": "不存在该账户"})
            try:
                # 验证密码
                user = authenticate(username=username, password=password)
            except Exception as e:
                text('注册2', e)
                return JsonResponse({"state": 403, "msg": "账号或密码错误"})
            if user is not None:
                text('登陆用户：', str(username))
                # 向redis中存储登陆信息'
                token = create_token(username)
                res = JsonResponse({
                    "state": 200, "msg": "登陆成功",
                    "data": {'token': token, 'username': username, 'reg': "退出"}
                })
                # if expire is None:
                #     max_age = 60 * 60 * 24 * 365 * 3  # 默认max_age为一年, 如果存在expires,则覆盖max_age
                # res.set_cookie('username', username, max_age)
                # res.set_cookie('user_id', name[0].id, max_age)
                # res.set_cookie('token', token, max_age)

                # 不设置 max_age时间  cookie默认为会话期有效
                res.set_cookie('username', username)
                res.set_cookie('user_id', name[0].id)
                res.set_cookie('token', token)
                res.set_cookie('islogin', True)
                return res
            else:
                return JsonResponse({"state": 403, "msg": "账号或密码错误"})
        except Exception as e:
            text('注册3', e)
            return JsonResponse({"state": 403, "msg": "数据错误"})


# 退出登陆
class OutLogin(View):

    def get(self, request):
        try:
            token = request.COOKIES['token']
        except Exception as e:
            text('退出登陆1', e)
            token = False
        try:
            if token:
                conn = settings.REDIS_CONN
                username = get_username(token)  # 调用get_username()函数，用token查询到用户名
                try:
                    token_lists = conn.get(username).decode()  # 拿到用户名在redis取出token列表
                except Exception as e:
                    text('退出登陆2', e)
                    return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
                if token_lists:
                    data = isinstance(token_lists, (str))  # 如果token_lists是str则返回True,否则返回False
                    if data:
                        token_lists = json.loads(token_lists)
                    data_dict = isinstance(token_lists, (dict))  # 如果token_lists是字典则返回True,否则返回False
                    if data_dict:
                        token_lists = token_lists['token']
                    print("退出登录token_lists***", token_lists)
                    print("退出登录token***", token)
                    # 如果长度大于1说明token列表不止一个token,只删除当前token在token列表的值
                    if len(token_lists) > 1:
                        if token in token_lists:
                            token_lists.remove(token)  # 删除当前的token
                            token_json = json.dumps(token_lists)  # 转换json
                            print("删除token之后的tokenlist", token_lists)
                            conn.set(username, token_json, 60 * 60 * 24)  # 再保存到redis
                            response = JsonResponse({"state": 200, "msg": "退出登陆成功"})
                            response.delete_cookie('username')
                            response.delete_cookie('user_id')
                            response.delete_cookie('token')
                            response.delete_cookie('islogin')
                            text(username, "退出登录！")
                            return response
                    # 如果长度不大于一 证明token列表里只有只有一个token,直接删除token列表
                    else:
                        response = JsonResponse({"state": 200, "msg": "退出登陆成功"})
                        response.delete_cookie('username')
                        response.delete_cookie('user_id')
                        response.delete_cookie('token')
                        response.delete_cookie('islogin')
                        conn.delete(username)
                        text(username, "退出登录！{}")
                        return response
            else:
                return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        except Exception as e:
            text('退出登陆3', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})


class Amount(View):
    def get(self, request):
        count = int(time.strftime("%Y-%m-%d %H:%M:%S").split(' ')[1].split(':')[0])
        dic_list = []
        if count == 0:
            count = 1
        else:
            count += 1
        for x in range(count):
            dic = {
                'id': x,
                'count': random.randint(300, 1200)
            }
            dic_list.append(dic)
        return JsonResponse({"state": 200, "data": dic_list})

    def post(self):
        pass


# 后台首页 今日分类提交数量
class Submits(View):
    def get(self, request):
        today_time = datetime.datetime.strptime(time.strftime("%Y-%m-%d 00:00:00", time.localtime(time.time())),
                                                "%Y-%m-%d %H:%M:%S")
        try:
            data = Submitcount.objects.filter(submit_time__gt=today_time)
            if data.count() > 24:
                data = data[20]
            dic_list = []
            for x in data:
                dic = {
                    'succeed': x.succeed,
                    'nothing': x.nothing,
                }
                dic_list.append(dic)
        except Exception as e:
            dic_list = []
            text('后台首页今日分类提交数量', e)
        succeed_count = Classify.objects.filter(accomplish_time__gt=today_time, status=2).count()
        nothing_count = Classify.objects.filter(accomplish_time__gt=today_time, status=3).count()
        return JsonResponse({"state": 200, "data": dic_list, 'succeed': succeed_count, 'nothing': nothing_count})


# 后台首页 分类目录站点公示
class Record(View):

    def get(self, request):
        try:
            data = Classify.objects.all().values('id',
                                                 'url',
                                                 'add_time',
                                                 'status').order_by('-add_time')[:5]
            dic_list = []
            for x in list(data):
                dic = {
                    'id': x['id'],
                    'url': x['url'],
                    'time': re.sub(r'T', '', str(x['add_time'])),
                    'status': x['status'],
                }
                dic_list.append(dic)
        except Exception as e:
            text('后台首页 分类目录站点公示', e)
            dic_list = []
        return JsonResponse({"state": 200, "data": dic_list})


# 分类目录站列表
class Directory(View):

    def get(self, request):
        try:
            page = int(request.GET.get('page', 1))
            token = request.COOKIES['token']
        except Exception as e:
            text('分类目录站列表1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        user = username_id(token)
        if not user:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        try:
            data = Classify.objects.filter(username_id=user).values('id',
                                                                    'url',
                                                                    'rates_name',
                                                                    'add_time',
                                                                    'accomplish_time',
                                                                    'status'
                                                                    ).order_by('-add_time')
            data_count = data.count()
            if data_count < 1:
                return JsonResponse({"state": 200, "data": []})
            maximum = math.ceil(data_count / 10)
            if page > maximum:
                page = maximum
            if page < 1:
                page = 1
            p = Paginator(data, 10)
            data_list = p.page(page)
            dic_list = []
            for x in list(data_list):
                accomplish_time = re.sub(r'T', '', str(x['accomplish_time']))
                if accomplish_time == 'None':
                    accomplish_time = ''
                dic = {
                    'id': x['id'],  # id
                    'url': x['url'],  # 网站
                    'charge': x['rates_name'],  # 收费标准
                    'add_time': re.sub(r'T', '', str(x['add_time'])),  # 添加时间
                    'accomplish_time': accomplish_time,  # 完成时间
                    'status': x['status'],  # 状态
                }
                dic_list.append(dic)
        except Exception as e:
            text('分类目录站列表', e)
            dic_list = []
        return JsonResponse({"state": 200, "data": dic_list, "count": data_count})


# 分类目录站列表 搜索框
class Seek(View):
    def get(self, request):
        try:
            keyword = request.GET.get('keyword', False)
            page = int(request.GET.get('page', 1))
            token = request.COOKIES['token']
        except Exception as e:
            text('分类目录站列表1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        if not keyword:
            return JsonResponse({"state": 403, "msg": "没有关键字"})
        user = username_id(token)
        if not user:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        try:
            data = Classify.objects.filter(username_id=user, url__icontains=keyword).values('id',
                                                                                            'url',
                                                                                            'rates_name',
                                                                                            'add_time',
                                                                                            'accomplish_time',
                                                                                            'status'
                                                                                            ).order_by('-add_time')
            data_count = data.count()
            if data_count < 1:
                return JsonResponse({"state": 200, "data": []})
            maximum = math.ceil(data_count / 10)
            if page > maximum:
                page = maximum
            if page < 1:
                page = 1
            p = Paginator(data, 10)
            data_list = p.page(page)
            dic_list = []
            for x in list(data_list):
                dic = {
                    'id': x['id'],  # id
                    'url': x['url'],  # 网站
                    'charge': x['rates_name'],  # 收费标准
                    'add_time': re.sub(r'T', '', str(x['add_time'])),  # 添加时间
                    'accomplish_time': re.sub(r'T', '', str(x['accomplish_time'])),  # 完成时间
                    'status': x['status'],  # 状态
                }
                dic_list.append(dic)
        except Exception as e:
            text('分类目录站列表', e)
            dic_list = []
        return JsonResponse({"state": 200, "data": dic_list, "count": data_count})


# 分类目录价格请求
class Price(View):
    def get(self, request):
        try:
            token = request.COOKIES['token']
        except Exception as e:
            print(e)
            text('分类目录价格请求错误', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问"})
        user = username_id(token)
        if not user:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        data_rates = Rates.objects.filter(name='分类目录')
        dic_list = []
        for x in data_rates:
            dic = {
                'id': x.id,  # id
                'rates': x.rates,  # 价格
                'rates_name': x.rates_name,  # 价格名称
            }
            dic_list.append(dic)
        return JsonResponse({"state": 200, "data": dic_list})

    def post(self, request):
        pass


#  分类目录提交
class SubmitClassify(View):
    def get(self, request):
        pass

    def post(self, request):
        post_data = json.loads(request.body)
        try:
            token = request.COOKIES['token']
        except Exception as e:
            text('分类目录提交', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        username = get_username(token)
        try:
            data_name = User.objects.filter(username=username).all()[0]
        except Exception as e:
            data_name = False
            text('分类目录提交根据token获取user', e)
        if not data_name:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        rates_id = post_data['rates_id']
        if not rates_id:
            return JsonResponse({"state": 403, "msg": '套餐错误'})
        try:
            data_rates = Rates.objects.get(id=int(rates_id))
        except Exception as e:
            text('分类目录提交价格查询错误', e)
            return JsonResponse({"state": 403, "msg": '套餐ID错误'})
        if data_rates.name != '分类目录':
            return JsonResponse({"state": 403, "msg": '套餐选择错误'})
        counts = data_rates.rates
        if data_name.balance < counts:
            difference = counts - data_name.balance
            return JsonResponse(
                {"state": 200, "msg": "账户余额不足！ 缺少{}个币".format(difference), "balance": False})
        charge = post_data['charge']  # 收费标准
        url = post_data['url']  # 网站链接
        agentqq = post_data['agentqq']  # 站长qq
        title = post_data['title']  # 网站标题
        keyword = post_data['keyword']  # 关键字
        describe = post_data['describe']  # 网站描述
        if not charge or not url or not title or not keyword or not describe or not agentqq:
            return JsonResponse({"state": 403, "msg": "缺少参数"})
        if len(url) > 200:
            return JsonResponse({"state": 403, "msg": "网站链接过长"})
        if len(agentqq) > 20:
            return JsonResponse({"state": 403, "msg": "站长qq过长"})
        if len(title) > 200:
            return JsonResponse({"state": 403, "msg": "网站标题过长"})
        if len(keyword) > 200:
            return JsonResponse({"state": 403, "msg": "网站关键字过长"})
        if len(describe) > 1000:
            return JsonResponse({"state": 403, "msg": "网站描述过长"})
        data_time = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            data = Classify.objects.create(rates_name=data_rates.rates_name,
                                           url=url,
                                           agentqq=agentqq,
                                           title=title,
                                           keyword=keyword,
                                           describe=describe,
                                           add_time=data_time,
                                           username_id=data_name.id)
            data.save()
            data_name.balance = data_name.balance - counts
            data_name.save()
            name_detail = Detail.objects.create(counts=1,
                                                correct=1,
                                                consume=counts,
                                                balance=data_name.balance,
                                                username_id=data_name.id,
                                                add_time=data_time,
                                                rates_name=data_rates.rates_name)
            name_detail.save()
        except Exception as e:
            text('分类目录提交', e)
            print(e)
            return JsonResponse({"state": 403, "msg": '提交失败！'})
        return JsonResponse({"state": 200, "msg": '提交成功'})


# 分类目录重新提交
class Resubmit(View):
    def get(self, request):
        try:
            id = request.GET.get('id', False)
            token = request.COOKIES['token']
        except Exception as e:
            text('分类目录重新提交1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        if not id:
            text('分类目录重新提交2', id)
            return JsonResponse({"state": 403, "msg": "id不存在"})
        user = username_id(token)
        if not user:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        data = Classify.objects.get(id=int(id))
        if data.status == 0:
            return JsonResponse({"state": 200, "msg": '请等待审核'})
        if data.status == 1:
            return JsonResponse({"state": 200, "msg": '审核中 请等待'})
        if data.status == 2:
            return JsonResponse({"state": 200, "msg": '审核已通过'})
        if data.status == 3:
            data.status = 0
            data.save()
            return JsonResponse({"state": 200, "msg": '重新提交成功！'})


# 分类目录网站公示
class Catalogue(View):

    def get(self, request):
        page = int(request.GET.get('page', 1))
        data = Classify.objects.all().values('id',
                                             'url',
                                             'add_time',
                                             'username__username',
                                             'status',
                                             ).order_by('-add_time')
        data_count = data.count()
        if data_count < 1:
            return JsonResponse({"state": 200, "data": []})
        maximum = math.ceil(data_count / 10)
        if page > maximum:
            page = maximum
        if page < 1:
            page = 1
        try:
            p = Paginator(data, 10)
            data_list = p.page(page)
            dic_list = []
            for x in data_list:
                username = re.sub(x['username__username'][2:5], '****', x['username__username'])
                dic = {
                    'id': x['id'],  # id
                    'url': x['url'],  # 网站
                    'add_time': re.sub(r'T', '', str(x['add_time'])),  # 添加时间
                    'username': username,
                    'status': x['status'],  # 状态
                }
                dic_list.append(dic)
        except Exception as e:
            text('分类目录网站公示', e)
            dic_list = []
        return JsonResponse({"state": 200, "data": dic_list, "count": data_count})


# 消费明细
class Consumption(View):
    def get(self, request):
        try:
            page = int(request.GET.get('page', 1))
            token = request.COOKIES['token']
        except Exception as e:
            text('消费明细1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        try:
            data = Detail.objects.filter(username_id=user_id).values('add_time',
                                                                     'consume',
                                                                     'balance',
                                                                     'status',
                                                                     'rates_name',
                                                                     'id',
                                                                     ).order_by('-add_time')
            data_count = data.count()
            if data_count < 1:
                return JsonResponse({"state": 200, "data": []})
            maximum = math.ceil(data_count / 10)
            if page > maximum:
                page = maximum
            if page < 1:
                page = 1
            p = Paginator(data, 10)
            data_list = p.page(page)
            dic_list = []
            for x in list(data_list):
                if int(x['status']) == 0:
                    consume = '-{}'.format(x['consume'])
                else:
                    consume = '+{}'.format(x['consume'])
                dic = {
                    'id': x['id'],  # id
                    'add_time': re.sub(r'T', '', str(x['add_time'])),  # 创建时间
                    'consume': consume,  # 消耗积分
                    'balance': x['balance'],  # 剩余积分
                    'rates_name': x['rates_name'],  # 套餐
                }
                dic_list.append(dic)
        except Exception as e:
            text('js查看提交记录2', e)
            dic_list = []
        return JsonResponse({"state": 200, "data": dic_list, "count": data_count})


# 个人信息
class Information(View):
    def get(self, request):
        try:
            token = request.COOKIES['token']
        except Exception as e:
            text('个人信息1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问", "referer": request.get_full_path()})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        try:
            data_user = User.objects.get(id=user_id)
        except Exception as e:
            text("个人信息查询错误", e)
            return JsonResponse({"state": 403, "msg": "个人信息查询错误"})
        return JsonResponse({"state": 200, "username": data_user.username, "balance": data_user.balance})


# 修改密码
class Amend(View):
    def post(self, request):
        try:
            token = request.COOKIES['token']
        except Exception as e:
            text('修改密码1', e)
            return JsonResponse({"state": 403, "msg": "请登录后再访问"})
        user_id = username_id(token)
        if not user_id:
            return JsonResponse({"state": 403, "msg": "不存在该账户"})
        dic = json.loads(request.body)
        former_password = dic['former_password']
        new_password = dic['new_password']
        if len(new_password) > 20:
            return JsonResponse({"state": 403, "msg": "密码位数错误，最多20位"})
        if len(new_password) < 6:
            return JsonResponse({"state": 403, "msg": "密码位数错误，最少6位"})
        try:
            # 验证密码
            user = User.objects.filter(id=user_id)[0]
            data = authenticate(username=user.username, password=former_password)
            if data is None:
                return JsonResponse({"state": 403, "msg": "密码错误"})
        except Exception as e:
            text('修改密码2', e)
            return JsonResponse({"state": 403, "msg": "密码错误"})
        user.password = make_password(new_password)
        user.save()
        text('ID为：{} 用户名为：{}'.format(user.id, user.username), '修改密码成功')
        return JsonResponse({"state": 200, "msg": "修改成功"})
