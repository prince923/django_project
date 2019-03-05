from django import forms
from django.core.validators import RegexValidator

from .models import UserModel
from django_redis import get_redis_connection


class CheckSmsForm(forms.Form):
    """
    发送手机短信验证码需要验证的参数
    1.   mobile    手机号
    2. image_code_id   图片uuid
    3. text    图片验证码信息
    """
    mobile_validators = RegexValidator(r'^1[3-9]\d{9}$', '手机号格式有误')
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
        image_code_id = cleaned_data.get('image_code_id')
        text = cleaned_data.get('text')
        #  1.  验证手机号是否已注册
        if UserModel.objects.filter(mobile=mobile):
            raise forms.ValidationError("该手机号已经注册")
        # 2. 验证图片验证码是否存在,以及 是否正确
        redis_conn = get_redis_connection(alias='verify_codes')
        #  (1)   构建img_key
        image_key = 'img_{}'.format(image_code_id.encode('utf-8'))
        # (2)   取  image_code 并进行验证
        image_code_origin = redis_conn.get(image_key)
        image_code = image_code_origin.decode('utf-8') if image_code_origin else None
        if not image_code or image_code != text:
            raise forms.ValidationError('图片验证码验证失败')
        # 3.   查看短信验证码是否在60s 内重复发送
        sms_flag_fmt = 'sms_flag_{}'.format(mobile).encode('utf-8')
        sms_flag = redis_conn.get(sms_flag_fmt)
        if sms_flag:
            raise forms.ValidationError('获取短信验证码过于频繁')

