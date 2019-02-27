from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django.http import HttpResponse
import logging

from utils.captcha.captcha import captcha
from .constant import IMAGE_CODE_REDIS_KEY_EXISTS

logger = logging.getLogger('django')   # 导入日志器


# Create your views here.

class ImageVerification (View):
    """
    生成图片验证码
    url  "/verification/image_codes/uuid/"   uuid 为前端传入
    :return 图片验证码
    """
    def get(self,request,image_code_id):
        text,image  = captcha.generate_captcha()
        con_redis = get_redis_connection(alias='verify_codes')
        img_key = 'img_{}'.format(image_code_id)
        con_redis.setex(img_key, IMAGE_CODE_REDIS_KEY_EXISTS, text)
        logger.info("image_code {}".format(text))
        return HttpResponse(image,content_type='image/jpg')

