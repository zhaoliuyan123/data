from django.db import models


# 卡密表
class ClipClose(models.Model):
    add_time = models.DateTimeField(auto_now_add=False, verbose_name='创建时间', db_index=True)
    conversion_time = models.DateTimeField(auto_now_add=False, null=True, verbose_name='兑现时间', db_index=True)
    close = models.CharField(max_length=255, null=True, unique=True, verbose_name='卡密')
    status = models.IntegerField(null=True, default=0, verbose_name='是否兑现状态')
    integral = models.IntegerField(null=True, default=0, verbose_name='兑换积分额度')
    ago = models.IntegerField(null=True, default=0, verbose_name='兑换卡密之前积分额度')
    later = models.IntegerField(null=True, default=0, verbose_name='兑换卡密之后积分额度')
    user_id = models.IntegerField(null=True, default=0, verbose_name='兑换用户ID')
    user_name = models.CharField(max_length=255, default='0', null=True, verbose_name='兑换用户名称')

    class Meta:
        db_table = 'clipClose'
        verbose_name = '卡密表'
        verbose_name_plural = verbose_name


# 公告表
class Notice(models.Model):
    add_time = models.DateTimeField(auto_now_add=False, verbose_name='创建时间', db_index=True)
    text = models.TextField(null=True, verbose_name='公告内容')
    terrace = models.IntegerField(null=True, default=0, verbose_name='关联ID')

    class Meta:
        db_table = 'notice'
        verbose_name = '公告表'
        verbose_name_plural = verbose_name
