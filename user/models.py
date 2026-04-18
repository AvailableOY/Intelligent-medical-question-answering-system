from django.db import models

# Create your models here.
class User(models.Model):
    # 手机号 11位
    tel = models.CharField(max_length=11,unique=True)
    # 密码
    passwd = models.CharField(max_length=32)
    # 头像
    avatar = models.CharField(max_length=500,null=True)
    # 注册时间
    call_name = models.DateTimeField(auto_now_add=True)
    # 最后一次登录时间
    last_login_time = models.DateTimeField(auto_now=True)