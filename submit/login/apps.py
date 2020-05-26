from django.apps import AppConfig


class LoginConfig(AppConfig):
    name = 'login'


class DemoConfig(AppConfig):
    name = "login"
    verbose_name = "用户管理"