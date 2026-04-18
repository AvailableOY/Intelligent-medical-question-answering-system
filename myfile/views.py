from django.http import JsonResponse
# 导入文件存储的模块FilesSystemStorage
from django.core.files.storage import FileSystemStorage
# 从配置文件导入STATIC_ROOT
# from aiserver.settings import STATIC_ROOT
from django.conf import settings
STATIC_ROOT = settings.STATICFILES_DIRS[0]


def upload(request):
    # 接收用户传上来的文件
    file = request.FILES.get("userfile123")
    # 创建一个fs对象
    fs = FileSystemStorage(location=STATIC_ROOT)
    saved_filename = fs.save(file.name, file)
    # 获取文件名称
    print('文件名：',saved_filename)
    print('类型：',file.name)
    with open(str(STATIC_ROOT) + '/' + saved_filename,'r',encoding='utf-8') as f:
        file_content =f.read()
    return JsonResponse({"code":200,"message":"上传成功",'content':file_content})
