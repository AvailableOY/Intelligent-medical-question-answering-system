from django.urls import path
from . import views

urlpatterns = [
    # 二级路由
    path("aichat/", views.ai_chat_123, name="ai_chat"),
    path("chatlist/", views.chatlist, name="chatlist"),
    # 获取主题下面的聊天内容
    path("chathistory/",views.chathistory,name="chathistory"),
    # 删除操作
    path("deltopic/",views.deltopic,name="deltopic")
]