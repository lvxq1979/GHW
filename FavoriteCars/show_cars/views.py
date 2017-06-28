from django.shortcuts import render

# coding=utf-8

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import Context
from show_cars.models import CarModel
import datetime


def current_datetime(request):
    # 计算当前日期和时间，并以 datetime.datetime 对象的形式保存为局部变量 now
    now = datetime.datetime.now()

    # 构建Html响应，使用now替换占位符%s
    html = "<html><body>It is now %s.</body></html>" % now

    # 返回一个包含所生成响应的HttpResponse对象
    return HttpResponse(html)

def carlist(request):
    cars = CarModel.objects.all()
    return render_to_response("carlist.html", {"carlist": cars})
    #return render("carlist.html", c)

