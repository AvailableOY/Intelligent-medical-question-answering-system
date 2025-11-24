from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from doctors.models import Doctors

def reg(request):
    data = {"code": 200, "message": "注册成功"}
    doctors = Doctors.objects.all().values(
        "image", "name", "department", "rank", "ifo", "advantage"
    )
    return JsonResponse(list(doctors), safe=False)
    # return JsonResponse(data)

