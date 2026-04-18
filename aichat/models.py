from django.db import models


'''
    Topic：类名，当我们进行模型迁移之后，会根据类名自动创建一个表topic
    models.Model：是Django写好的基类，在创建模型的时候，一定要继承该类
'''
# Create your models here.
class Topic(models.Model):
    # 主键id :自动增加，key是唯一的
    id = models.AutoField(primary_key=True)  # 自增
    # 话题 title,varchar(500)
    title = models.CharField(max_length=500)
    # 添加一个新的字段 问题的摘要，长度为40
    summary = models.CharField(max_length=40, null=True)
    # status:status状态,int 默认为1
    status = models.IntegerField(default=1)
    # 用户id:user_id,int
    user_id = models.IntegerField()
    # 话题开启时间：create_time,datetime  当前时间默认值
    create_time = models.DateTimeField(auto_now_add=True)

class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    topic_id = models.IntegerField()
    user_id = models.IntegerField()
    # 角色：user assiant
    role = models.CharField(max_length=10)
    # 用于存储检索到的上下文，可以为空：没命中
    # context = models.TextField(null=True)
    
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
