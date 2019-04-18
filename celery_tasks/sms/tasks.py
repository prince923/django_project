from utils.yuntongxun.sms import CCP
from celery_tasks.celery_main import app
import logging

logger = logging.getLogger('django')  # 导入日志器


@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_num, expires, temp_id):
    """
    发送短信验证码
    :param mobile: 手机号
    :param sms_num: 短信验证码
    :param expires: 云通讯验证码过期时间
    :param temp_id: 短信模版id
    :return:
    """
    try:
        result = CCP().send_template_sms(mobile, [sms_num, expires], temp_id)
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
    else:
        if result == 0:
            logger.info("发送验证码短信[正常][ mobile: %s sms_code: %s]" % (mobile, sms_num))
        else:
            logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)