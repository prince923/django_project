from django.contrib.auth import login
from django.shortcuts import render
from django.views import View
import json
import random
import string
import django_redis
import logging
from .models import UserModel
from .forms import CheckSmsForm
from .forms import RegisterForm
from verification import constant
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from utils.yuntongxun.sms import CCP

logger = logging.getLogger('django')  # 导入日志器


class LoginView(View):
    def get(self, request):
        return render(request, 'user/login.html')

    def post(self, request):
        pass


class RegisterView(View):
    def get(self, request):
        return render(request, 'user/register.html')

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        else:
            dict_data = json.loads(json_data.decode('utf8'))
        form = RegisterForm(dict_data)
        if form.is_valid():
            mobile = form.cleaned_data.get('mobile')
            password = form.cleaned_data.get('password')
            username = form.cleaned_data.get('username')
            user = UserModel.objects.create_user(username=username, password=password, mobile=mobile)
            login(request, user)
            return to_json_data(errmsg="恭喜您，注册成功")
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


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
    判断手机号是否存在
    """

    def get(self, request, mobile):
        data = {
            'mobile': mobile,
            'count': UserModel.objects.filter(mobile=mobile).count()
        }
        return to_json_data(data=data)


class SmsCodes(View):
    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        else:
            dict_data = json.loads(json_data.decode('utf8'))
        form = CheckSmsForm(dict_data)
        if form.is_valid():
            #  获取手机号
            mobile = form.cleaned_data.get('mobile')
            #  生成短信验证码
            sms_code = ''.join([random.choice(string.digits) for _ in range(6)])
            #  保存到redis数据库
            redis_conn = django_redis.get_redis_connection(alias='verify_codes')
            #  短信验证码的key
            sms_text_fmt = 'sms_{}'.format(mobile)
            #  短信验证码的标识位
            sms_flag_fmt = 'sms_flag_{}'.format(mobile)
            try:
                redis_conn.setex(sms_flag_fmt.encode('utf8'), constant.SMS_FLAG_EXISTS, 1)
                redis_conn.setex(sms_text_fmt.encode('utf8'), constant.SMS_TEXT_EXISTS, sms_code)
            except Exception as e:
                logger.error("redis 发生错误{}".format(e))
                return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])
            logger.info("短信验证码为{}".format(sms_code))
            # try:
            #     result = CCP().send_template_sms(mobile,[sms_code,5],'1')
            # except Exception as e:
            #     logger.error("手机短信验证码发送错误 {}".format(e))
            #     return to_json_data(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])
            # else:
            #     if result == 0:
            #         logger.info("手机号{}短信验证码{}发送成功".format(mobile, sms_code))
            #         return to_json_data(errmsg="发送短信验证码成功")
            #     else:
            #         logger.error("手机号{}短信验证码{}发送异常".format(mobile, sms_code))
            #         return to_json_data(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])
            return to_json_data(errmsg="发送短信验证码成功")
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)
