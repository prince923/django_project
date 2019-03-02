from django.shortcuts import render
from django.views import View
from .models import UserModel
# Create your views here.

from utils.json_fun import to_json_data


class LoginView(View):
    def get(self, request):
        return render(request, 'user/login.html')

    def post(self, request):
        pass


class RegisterView(View):
    def get(self, request):
        return render(request, 'user/register.html')

    def post(self, request):
        pass


class CheckUsername(View):
    """
    检测用户名是否存在数据库中
    count  1 为存在  0 为不存在
    """

    def get(self, request, username):
        count = UserModel.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count,
        }
        return to_json_data(data=data)


class CheckMobile(View):
    """
    判断手机号是否存在数据库中
    """
    def get(self, request, mobile):
        data = {
            'mobile': mobile,
            'count': UserModel.objects.filter(mobile=mobile).count()
        }
        return to_json_data(data=data)
