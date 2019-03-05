# -*- coding:utf-8 -*-

# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
from utils.yuntongxun.CCPRestSDK import REST

_accountSid = '8aaf07086904be0b01694e6ac93e20f0'

# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_accountToken = '9132e1fc92fb4e87be65f68162bd9115'

# 请使用管理控制台首页的APPID或自己创建应用的APPID
_appId = '8aaf07086904be0b01694e6ac9a720f7'

# 说明：请求地址，生产环境配置成app.cloopen.com
_serverIP = 'sandboxapp.cloopen.com'

# 说明：请求端口 ，生产环境为8883
_serverPort = "8883"

# 说明：REST API版本号保持不变
_softVersion = '2013-12-26'


class CCP(object):
    """发送短信的辅助类"""

    def __new__(cls, *args, **kwargs):
        # 判断是否存在类属性_instance，_instance是类CCP的唯一对象，即单例
        if not hasattr(CCP, "_instance"):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls._instance.rest = REST(_serverIP, _serverPort, _softVersion)
            cls._instance.rest.setAccount(_accountSid, _accountToken)
            cls._instance.rest.setAppId(_appId)
        return cls._instance

    def send_template_sms(self, to, datas, temp_id):
        """
        发送模板短信
        :param to: 发给哪个手机号（‘18866666666’）
        :param datas: ['6666', 5] 短信验证码6666和过期时间5分钟
        :param temp_id: ‘1’ 内容模板id
        :return:
        """
        # @param to 手机号码
        # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
        # @param temp_id 模板Id
        res = None
        try:
            res = self.rest.sendTemplateSMS(to, datas, temp_id)
        except Exception as e:
            print(e)
        # 如果云通讯发送短信成功，返回的字典数据result中statuCode字段的值为"000000"
        if res.get("statusCode") == "000000":
            # 返回0 表示发送短信成功
            return 0
        else:
            # 返回-1 表示发送失败
            return -1


if __name__ == '__main__':
    ccp = CCP()
    # 注意： 测试的短信模板编号为1
    result = None
    while True:
        result = ccp.send_template_sms('17696273938', ['6666', 5], "1")
        if result == 0:
            print('短信验证码发送成功！')
            break
