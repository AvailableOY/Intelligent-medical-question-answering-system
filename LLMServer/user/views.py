from django.http import JsonResponse
from django.shortcuts import render
from .models import User
from django.conf import settings
STATIC_ROOT = settings.STATICFILES_DIRS[0]
from django.core.files.storage import FileSystemStorage
import os

def reg(request):
    data = {"code":200,"message":"注册成功"}
    return JsonResponse(data)

def login(request):
    # 接收客户端提交上来的手机号tel和密码passwd
    tel = request.POST.get("tel","")
    password = request.POST.get("passwd","")
    data = {"code":200,"message":"登录成功"}
    # 简单判断
    if tel == '' or password == '':
        return JsonResponse({"code":400,"message":"手机号或密码不能为空"})
    
    '''
        1，如果有该账号（tel)，则验证密码是否正确；
        2，如果没有该账号，则直接使用该账号创建一个新的用户即可；
    '''
    user = User.objects.filter(tel=tel).first()
    if user:
        if user.passwd == password:
            data = {"code":200,"message":"登录成功","user_id":user.id}
        else:
            data = {"code":400,"message":"密码错误"}
    else:
        # 创建用户
        result = User.objects.create(tel=tel,passwd=password)
        user_id = result.id
        data = {"code":200,"message":"登录成功","user_id":user_id}
        # 获取用户id
    return JsonResponse(data)

def set(request):
    data = {"code":200,"message":"设置成功"}
    return JsonResponse(data)


def avatar(request):
    data = {"code": 200, "message": "头像更新成功"}
    
    # 接收文件
    uploaded_file = request.FILES.get("avatar")
    if not uploaded_file:
        return JsonResponse({"code": 400, "message": "未收到文件"}, status=400)

    # 确保 STATIC_ROOT 存在
    tmpdir = os.path.join(STATIC_ROOT, 'avatar')
    os.makedirs(tmpdir, exist_ok=True)  # 自动创建目录

    # 保存头像文件到静态资源目录
    fs = FileSystemStorage(location=tmpdir)
    saved_filename = fs.save(uploaded_file.name, uploaded_file)  # 关键：传 uploaded_file，不是 avatar！

    print('文件名：', saved_filename)
    # 构建url访问地址
    url = 'http://' + request.get_host() + '/static/avatar/' + saved_filename
    print('url:', url)
    # 更新头像
    user_id = request.POST.get("user_id")
    User.objects.filter(id=user_id).update(avatar=url)
    return JsonResponse(data)