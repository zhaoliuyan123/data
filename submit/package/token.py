import json
from django.conf import settings
import random
import time
from django.core import signing
import hashlib
from submit.settings import REDIS_CONN as cache
from login.views import *
from userAdmin.models import *
from package.log import text
from login.models import User

HEADER = {'typ': 'JWP', 'alg': 'default'}
KEY = 'CHEN_FENG_YAO'
SALT = 'www.huobaowen.com'
TIME_OUT = 60 * 60 * 24  # 30min


# 加密
def encrypt(obj):
    """加密"""
    value = signing.dumps(obj, key=KEY, salt=SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value


# 解密
def decrypt(src):
    """解密"""

    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=KEY, salt=SALT)
    print(type(raw), raw)
    return raw


# 生成token信息
def create_token(username):
    """生成token信息"""
    # 1. 加密头信息
    header = encrypt(HEADER)
    # 2. 构造Payload
    payload = {"username": username, "iat": time.time()}
    payload = encrypt(payload)
    # 3. 生成签名
    md5 = hashlib.md5()
    md5.update(("%s.%s.%s" % (header, payload, ''.join(str(i) for i in random.sample(range(0, 9), 6)))).encode())
    signature = md5.hexdigest()
    token = "%s.%s.%s" % (header, payload, signature)
    # 存储到缓存中
    try:
        token_lists = cache.get(username).decode()
    except:
        token_lists = False
    # print(token_lists, "****************53")
    try:
        if token_lists:
            data = isinstance(token_lists, (str))
            if data:
                token_lists = json.loads(token_lists)
            data_dict = isinstance(token_lists, (dict))
            if data_dict:
                token_lists = token_lists['token']
            # print("token_lists", token_lists)
            # print(len(token_lists))
            if len(token_lists) >= 1:
                # print("token_list", token_lists)
                del token_lists[0]
                token_lists.append(token)
                # print("删除之后的token_list", token_lists)
            else:
                token_lists.append(token)
        else:
            token_lists = {"token": [token]}
    except:
        token_lists = {"token": [token]}
    token_json = json.dumps(token_lists)
    cache.set(username, token_json, TIME_OUT)
    return token


def get_payload(token):
    if token:
        payload = str(token).split('.')[1]
        payload = decrypt(payload)
        return payload
    else:
        return None


# 通过token获取用户名
def get_username(token):
    payload = get_payload(token)
    return payload['username']


# 根据token验证是否是管理员
def user_admin(request):
    try:
        token = request.COOKIES['token']
    except Exception as e:
        text('管理员token验证错误', e)
        return False
    username = get_username(token)
    try:
        user = User.objects.filter(username=username, is_superuser=1).all()[0]
    except Exception as e:
        user = False
        text('根据token验证是否是管理员', e)
    if not user:
        return False
    return True


# 根据token获取username的ID
def username_id(token):
    username = get_username(token)
    try:
        user = User.objects.filter(username=username).all()[0]
    except Exception as e:
        user = False
        text('根据token获取username的ID', e)
    if not user:
        return False
    return user.id


# 根据token获取用户的余额
def username_balance(token):
    username = get_username(token)
    try:
        user = User.objects.filter(username=username).all()[0]
    except Exception as e:
        user = False
        text('根据token获取username的余额', e)
    if not user:
        return 0
    return user.balance


def check_token(token):
    username = get_username(token)
    token_lists = cache.get(username).decode()
    data = isinstance(token_lists, (dict))
    if data:
        token_lists = token_lists['token']
    if token in token_lists:
        return True
    return False


def tokens(request):
    try:
        ip = False
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META.get("HTTP_X_FORWARDED_FOR")
        else:
            ip = request.META.get("REMOTE_ADDR")
        token = request.COOKIES.get('token')
        user_id = get_username(token)
        print(token, user_id)
        try:
            name = User.objects.get(username=user_id)
            if name.is_delete:
                return False, ip
            elif not name:
                return False, ip
            elif check_token(token):
                return name, ip
            else:
                return False, ip
        except Exception as e:
            print(e)
            return False, ip
    except Exception as e:
        return False, ip


# def guanRecord(name, ip, txts):
#     uss = Record.objects.create(name=txts, ip=ip, user_id=name)
#     uss.save()


# 随机卡密
def random_kai():
    source = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789"
    while True:
        code_str = ""
        for i in range(16):
            tmp_num = random.randrange(len(source))
            random_str = source[tmp_num]
            code_str += random_str
        data = ClipClose.objects.filter(close=code_str)
        if data.count() < 1:
            break
    return code_str
