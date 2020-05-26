from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


# 用户表
class User(AbstractUser):
    register_time = models.DateTimeField(null=True, blank=True, verbose_name='时间')
    vip_time = models.DateTimeField(null=True, blank=True, verbose_name='vip到期时间')
    balance = models.IntegerField(null=True, default=0, verbose_name='余额')
    total = models.IntegerField(null=True, default=0, verbose_name='充值累计')

    class Meta:
        db_table = 'users'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name


# 积分明细
class Detail(models.Model):
    add_time = models.DateTimeField(auto_now_add=False, verbose_name='创建时间', db_index=True)
    rates_name = models.CharField(max_length=255, default='0', verbose_name="套餐")
    counts = models.IntegerField(default=0, verbose_name='总数量')
    correct = models.IntegerField(default=0, verbose_name='上传成功数量')
    status = models.IntegerField(default=0, verbose_name='加积分或减积分')
    consume = models.IntegerField(default=0, verbose_name='消耗积分')
    balance = models.IntegerField(default=0, verbose_name='剩余积分')
    username = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='用户关联ID')

    class Meta:
        db_table = 'detail'
        verbose_name = '积分明细表'
        verbose_name_plural = verbose_name


# 上传记录表
class UploadingRecord(models.Model):
    add_time = models.DateTimeField(auto_now_add=False, verbose_name='创建时间', db_index=True)
    uploading_explain = models.CharField(max_length=255, default='0', verbose_name="上传说明")
    counts = models.IntegerField(default=0, verbose_name='总数量')
    correct = models.IntegerField(default=0, verbose_name='上传成功数量')
    error = models.IntegerField(default=0, verbose_name='失败数量')
    username = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='用户关联ID')

    class Meta:
        db_table = 'uploadingRecord'
        verbose_name = '上传记录表'
        verbose_name_plural = verbose_name


# 价格表
class Rates(models.Model):
    rates = models.IntegerField(verbose_name='价格')
    rates_name = models.CharField(max_length=255, verbose_name="名称")
    name = models.CharField(max_length=255, default='无', verbose_name="名称")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'rates'
        verbose_name = '积分明细表'
        verbose_name_plural = verbose_name


# 百度熊掌推送会员时间表
class PawVip(models.Model):
    vip_name = models.CharField(max_length=50, verbose_name="vip名称")
    fund = models.IntegerField(default=0, verbose_name="价格")
    v_time = models.IntegerField(default=0, verbose_name="vip有效时间天")

    class Meta:
        db_table = 'PawVip'
        verbose_name = '百度熊掌推送会员时间表'
        verbose_name_plural = verbose_name


# 网站收录表
class Classify(models.Model):
    url = models.CharField(max_length=255, null=True, unique=True, verbose_name='网站链接')
    rates_name = models.CharField(max_length=255, null=True, verbose_name='收费标准')
    agentqq = models.CharField(max_length=255, null=True, verbose_name='站长qq')
    title = models.CharField(max_length=255, null=True, db_index=True, verbose_name='网站标题')
    keyword = models.CharField(max_length=255, null=True, db_index=True, verbose_name='关键字,中间用英文逗号分隔')
    describe = models.TextField(null=True, verbose_name='网站描述')
    add_time = models.DateTimeField(null=True, blank=True, verbose_name='添加时间')
    accomplish_time = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    status = models.IntegerField(null=True, default=0, verbose_name='状态')
    rates = models.ForeignKey(to=Rates, on_delete=models.CASCADE, default=4, verbose_name='价格关联ID')
    username = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='用户关联ID')

    class Meta:
        db_table = 'classify'
        verbose_name = '网站收录表'
        verbose_name_plural = verbose_name


# 分类提交数量
class Submitcount(models.Model):
    succeed = models.IntegerField(null=True, default=0, verbose_name='提交成功数量')
    nothing = models.IntegerField(null=True, default=0, verbose_name='提交失败数量')
    str_time = models.CharField(max_length=255, null=True, verbose_name='表格显示时间')
    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='更新时间')

    class Meta:
        db_table = 'submitcount'
        verbose_name = '分类提交数量'
        verbose_name_plural = verbose_name


# 百度js推送url表
class JsUrl(models.Model):
    url = models.CharField(max_length=255, null=True, unique=True, verbose_name='网站链接')
    add_time = models.DateTimeField(null=True, blank=True, verbose_name='添加时间')
    accomplish_time = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    status = models.IntegerField(null=True, default=0, verbose_name='状态')
    rates_name = models.CharField(max_length=255, default='无', verbose_name='收费标准')
    rates = models.ForeignKey(to=Rates, on_delete=models.CASCADE, verbose_name='价格关联ID')
    username = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='用户关联ID')

    class Meta:
        db_table = 'JsUrl'
        verbose_name = 'Js推送Url表'
        verbose_name_plural = verbose_name


# 百度熊掌推送
class Paws(models.Model):
    add_time = models.DateTimeField(null=True, blank=True, verbose_name='添加时间')
    domain_url = models.CharField(max_length=255, null=True, verbose_name='绑定域名链接')
    status = models.IntegerField(default=0, verbose_name='API接口状态')
    api = models.CharField(max_length=255, unique=True, verbose_name='API接口')
    api_id = models.CharField(max_length=255, default='0', verbose_name='API的id')
    rank = models.IntegerField(default=1, verbose_name='熊掌级别')
    file = models.CharField(max_length=255, default='无', verbose_name='文件名称')
    present = models.IntegerField(verbose_name='提交方式')
    rates_name = models.CharField(max_length=255, default='无', verbose_name='收费标准')
    vip_time = models.DateTimeField(default=True, verbose_name='到期时间')
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='用户关联ID')

    class Meta:
        db_table = 'paws'
        verbose_name = '百度熊掌推送表'
        verbose_name_plural = verbose_name


# paw推送记录
class PawPush(models.Model):
    add_time = models.DateTimeField(null=True, blank=True, verbose_name='推送时间')
    domain_url = models.CharField(max_length=255, null=True, verbose_name='绑定域名链接')
    api = models.CharField(max_length=255, default='0', verbose_name='API接口')
    rank = models.IntegerField(default=1, verbose_name='熊掌级别')
    url = models.CharField(max_length=255, null=True, verbose_name='推送url')
    consume = models.IntegerField(default=0, verbose_name='提交成功数')
    balance = models.IntegerField(default=0, verbose_name='剩余次数')
    api_id = models.IntegerField(default=0, verbose_name='api的id')

    class Meta:
        db_table = 'pawpush'
        verbose_name = '百度熊掌推送记录表'
        verbose_name_plural = verbose_name


# 百度熊掌天级
class Day(models.Model):
    add_time = models.DateTimeField(null=True, blank=True, verbose_name='添加时间')
    accomplish_time = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    domain_url = models.CharField(max_length=255, null=True, verbose_name='绑定域名链接')
    url = models.CharField(max_length=255, verbose_name='url链接')
    api_id = models.CharField(max_length=255, null=True, default='0', verbose_name='API接口')
    status = models.IntegerField(null=True, default=0, verbose_name='状态')
    paw = models.ForeignKey(to=Paws, on_delete=models.CASCADE, verbose_name='推送关联id')
    username = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='用户关联ID')

    class Meta:
        db_table = 'day'
        verbose_name = '百度熊掌天级表'
        verbose_name_plural = verbose_name


# Paw推送url表
class PawUrl(models.Model):
    domain_url = models.CharField(max_length=255, null=True, verbose_name='域名链接')
    url = models.CharField(max_length=255, null=True, unique=True, verbose_name='网站链接')
    api = models.CharField(max_length=255, null=True, default='无', verbose_name='API接口')
    add_time = models.DateTimeField(null=True, blank=True, verbose_name='添加时间')
    accomplish_time = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    status = models.IntegerField(null=True, default=0, verbose_name='状态')
    rates_name = models.CharField(max_length=255, default='无', verbose_name='收费标准')
    rates = models.ForeignKey(to=Rates, on_delete=models.CASCADE, verbose_name='价格关联ID')
    username = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='用户关联ID')

    class Meta:
        db_table = 'pawUrl'
        verbose_name = 'paw推送Url表'
        verbose_name_plural = verbose_name


# Ping推送url表
class PingUrl(models.Model):
    domain_url = models.CharField(max_length=255, null=True, verbose_name='域名链接')
    url = models.CharField(max_length=255, null=True, unique=True, verbose_name='网站链接')
    add_time = models.DateTimeField(null=True, blank=True, verbose_name='添加时间')
    accomplish_time = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    status = models.IntegerField(null=True, default=0, verbose_name='状态')
    rates_name = models.CharField(max_length=255, default='无', verbose_name='收费标准')
    rates = models.ForeignKey(to=Rates, on_delete=models.CASCADE, verbose_name='价格关联ID')
    username = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='用户关联ID')

    class Meta:
        db_table = 'PingUrl'
        verbose_name = 'Ping推送Url表'
        verbose_name_plural = verbose_name
