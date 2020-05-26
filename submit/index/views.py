from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from submit import settings
from package.token import get_username
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
import time
import json

'''

ip访问限制

'''
MAX_REQUEST_PER_SECOND = 2  # 每秒访问次数


# Create your views here.
def Check_Login(func):  # 自定义登录验证装饰器
    def warpper(self, *args):
        # start_time = time.time()
        ABC = func(self, args[0])
        # end_time = time.time()
        # take_up_time = end_time-start_time
        # print(args[0].get_full_path(),take_up_time)
        return ABC


class Index(View):
    def get(self, request):
        ip = request.META['REMOTE_ADDR']
        print(ip)
        # user_agents = request.META['HTTP_USER_AGENT']
        # out_trade_on = request.GET.get('out_trade_no', False)
        # print('PC端访问')
        return render(request, 'index.html')


class UserAdmin(View):
    def get(self, request):
        return render(request, 'admin.html')


class RequestBlockingMiddleware(MiddlewareMixin):

    def process_request(self, request):
        now = time.time()
        request_queue = request.session.get('request_queue', [])
        if len(request_queue) < MAX_REQUEST_PER_SECOND:
            request_queue.append(now)
            request.session['request_queue'] = request_queue
        else:
            time0 = request_queue[0]
            if (now - time0) < 1:
                time.sleep(5)
            request_queue.append(time.time())
            request.session['request_queue'] = request_queue[1:]


class MD1(MiddlewareMixin):
    def process_request(self, request):
        try:
            token = request.COOKIES['token']
        except:
            token = False
        if token:
            conn = settings.REDIS_CONN
            username = get_username(token)
            try:
                token_lists = conn.get(username).decode()
            except:
                token_lists = False
            if token_lists:
                data_dict = isinstance(token_lists, (dict))
                if data_dict:
                    token_lists = token_lists['token']
                # print(type(token_lists))
                # print("中间件", token_lists)
                # print("中间件", token)
                if token not in token_lists:
                    # print("***********来了*************")
                    # return render(request, 'index.html')
                    response = JsonResponse({'state': 1406, 'token': '请登录,token失效！'})
                    response.delete_cookie('username')
                    response.delete_cookie('user_id')
                    response.delete_cookie('token')
                    response.delete_cookie('islogin')
                    return response
            else:
                print("没有token******************")

    def process_response(self, request, response):
        # print('********走了**********')
        # return render(request, 'index.html')
        return response
