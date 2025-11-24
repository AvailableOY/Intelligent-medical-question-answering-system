from django.db import models

# Create your models here.
class Doctors(models.Model):
    # 主键：头像链接
    image = models.CharField(max_length=5000)
    # 姓名
    name = models.CharField(max_length=50)
    # 科室
    department = models.CharField(max_length=50,null=True)
    # 等级
    rank = models.CharField(max_length=50,null=True)
    # 介绍
    ifo = models.CharField(max_length=5000,null=True)
    # 优势
    advantage = models.CharField(max_length=5000,null=True)


