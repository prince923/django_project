from django import forms
from django.core.validators import RegexValidator

from .models import UserModel
from django_redis import get_redis_connection

#  定义手机号验证器
mobile_validators = RegexValidator(r'^1[3-9]\d{9}$', '手机号格式有误')


class CheckSmsForm(forms.Form):
    """
    发送手机短信验证码需要验证的参数
    1.   mobile    手机号
    2. image_code_id   图片uuid
    3. text    图片验证码信息
    """

    mobile = forms.CharField(max_length=11, min_length=11, validators=[mobile_validators, ],
                             error_messages={
                                 'required': '手机号不能为空', 'max_length': '手机号格式有误', 'min_length': '手机号格式有误'
                             })
    image_code_id = forms.UUIDField(error_messages={'required': '图片uuid不能为空'})
    text = forms.CharField(min_length=4, max_length=4,
                           error_messages={
                               'required': '图片验证码不能为空',
                               'min_length': '图片验证码格式有误',
                               'max_length': '图片验证码格式有误'
                           })

    def clean(self):
        cleaned_data = super().clean()
        mobile = cleaned_data.get('mobile')
        image_code_id = cleaned_data.get('image_code_id', '')
        text = cleaned_data.get('text')
        #  1.  验证手机号是否已注册
        if UserModel.objects.filter(mobile=mobile):
            raise forms.ValidationError("该手机号已经注册")
        # 2. 验证图片验证码是否存在,以及 是否正确
        redis_conn = get_redis_connection(alias='verify_codes')
        #  (1)   构建img_key
        image_key = 'img_{}'.format(image_code_id)
        # (2)   取  image_code 并进行验证
        image_code_origin = redis_conn.get(image_key)
        image_code = image_code_origin.decode('utf-8') if image_code_origin else None
        if not image_code or image_code != text.upper():
            raise forms.ValidationError('图片验证码验证失败')
        # 3.   查看短信验证码是否在60s 内重复发送
        sms_flag_fmt = 'sms_flag_{}'.format(mobile).encode('utf-8')
        sms_flag = redis_conn.get(sms_flag_fmt)
        if sms_flag:
            raise forms.ValidationError('获取短信验证码过于频繁')


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=5,
                               error_messages={'required': '用户名不能为空', 'max_length': '用户名最大长度不能超过20位',
                                               'min_length': '用户名最小长度不能低于5位'})
    password = forms.CharField(max_length=16, min_length=6,
                               error_messages={'required': '密码不能为空', 'max_length': '密码最大长度不能超过16位',
                                               'min_length': '密码最小长度不能低于6位'})
    password_repeat = forms.CharField(max_length=16, min_length=6,
                                      error_messages={'required': '密码不能为空', 'max_length': '密码最大长度不能超过16位',
                                                      'min_length': '密码最小长度不能低于6位'})
    mobile = forms.CharField(max_length=11, min_length=11, validators=[mobile_validators, ],
                             error_messages={
                                 'required': '手机号不能为空', 'max_length': '手机号格式有误', 'min_length': '手机号格式有误'
                             })
    sms_code = forms.CharField(max_length=6, min_length=6,
                               error_messages={'required': '短信验证码不能为空', 'max_length': '短信验证码长度有误',
                                               'mix_length': '短信验证码长度有误'})

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if UserModel.objects.filter(mobile=mobile):
            raise forms.ValidationError("该手机号已经被注册")
        return mobile

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if UserModel.objects.filter(username=username):
            raise forms.ValidationError("该用户名已经被注册，请重新输入")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password', '')
        password_repeat = cleaned_data.get('password_repeat', '')
        mobile = cleaned_data.get('mobile')
        sms_code = cleaned_data.get('sms_code')
        if password == '' or password_repeat == '':
            raise forms.ValidationError('密码以及重复密码不能为空')
        if password != password_repeat:
            raise forms.ValidationError('两次密码输入不一致,请确认')
        #  建立redis连接
        redis_conn = get_redis_connection(alias='verify_codes')
        sms_text_fmt = 'sms_{}'.format(mobile).encode('utf8')
        real_sms_code = redis_conn.get(sms_text_fmt)
        if not real_sms_code or sms_code != real_sms_code.decode('utf8'):
            raise forms.ValidationError("短信验证码输入有误")
