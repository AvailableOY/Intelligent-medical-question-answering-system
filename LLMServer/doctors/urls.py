# 固定写法，不需要你思考
from django.urls import path
from . import views

urlpatterns = [
    # 食堂：二级路由
    path('reg/', views.reg, name='reg'),
]