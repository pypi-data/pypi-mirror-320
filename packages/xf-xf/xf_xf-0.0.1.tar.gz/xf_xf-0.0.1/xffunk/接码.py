# -*- coding: utf-8 -*-
# -------------------------------

# @软件：PyCharm
# @项目：自己的库

# -------------------------------

# @文件：接码.py
# @时间：2024/12/21 下午6:29
# @作者：小峰
# @邮箱：ling_don@qq.com

# -------------------------------
import json
import requests
import time
import random
from loguru import logger
class 接码:
    def __init__(self,类型,项目ID列表='',豪猪账号='',豪猪密码='',椰子账号='',椰子密码='',豪猪专属项目ID='',令牌=''):
        self.proxies = {
            'http': '',
            'https': '',
        }
        self.项目ID = None
        self.类型 = 类型
        if 项目ID列表 == '':
            raise Exception('项目ID列表不能为空')
        if self.类型 == '1':
            self.服务器地址 = "api.haozhuma.com"
            self.项目ID列表 = [i for i in 项目ID列表.split(',') if i != '' and i != '\n']
            self.专属 = 豪猪专属项目ID
            self.令牌 = 令牌
            self.豪猪账号 = 豪猪账号
            self.豪猪密码 = 豪猪密码
            if self.令牌 == '':
                self.hz_login()
            self.hz_获取个人信息()
        else:
            self.服务器地址 = "api.sqhyw.net:90"
            self.项目ID列表 = [i for i in 项目ID列表.split(',') if i != '' and i != '\n']
            self.令牌 = 令牌
            self.椰子账号 = 椰子账号
            self.椰子密码 = 椰子密码
            if self.令牌 == '':
                self.yz_login()
            self.yz_获取个人信息()

    def hz_login(self):
        # https://服务器地址/sms/?api=login&user=用户名&pass=密码
        login_url = f'https://{self.服务器地址}/sms/?api=login&user={self.豪猪账号}&pass={self.豪猪密码}'
        response = requests.get(login_url, proxies=self.proxies)
        if 'token' in response.text:
            logger.info('豪猪-登录成功')
            self.令牌 = response.json()['token']
            self.cofing['豪猪token'] = self.令牌
            with open('config.josn', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.cofing, indent=4, ensure_ascii=False))
        else:
            logger.info('豪猪-登录失败')

    def hz_获取短信(self, 手机号):
        # https://服务器地址/sms/?api=getMessage&token=用户令牌&sid=项目ID&phone=手机号
        等待 = 0
        while 等待 < 40:
            try:
                response = requests.get(
                    f'https://{self.服务器地址}/sms/?api=getMessage&token={self.令牌}&sid={self.项目ID}&phone={手机号}',
                    proxies=self.proxies)
                # logger.info(response.text)
                if 'yzm' in response.text:
                    logger.info(response.text)
                    return response.json().get('yzm')
                elif '短信还未到达,请继续获取' in response.text:
                    time.sleep(1)
                    logger.info(f"短信还未到达,请继续获取,等待时间:{等待}")
                elif '等待' in response.text:
                    time.sleep(1)
                    logger.info(f"短信还未到达,请继续获取,等待时间:{等待}")
                else:
                    logger.info(response.text)
                    return None
                等待 += 1
            except Exception as e:
                if '443' in e:
                    time.sleep(2)
                    continue
        return None

    def hz_释放手机号(self, 手机号):
        # https://服务器地址/sms/?api=cancelRecv&token=用户令牌&sid=项目ID&phone=手机号
        response = requests.get(
            f'https://{self.服务器地址}/sms/?api=cancelRecv&token={self.令牌}&sid={self.项目ID}&phone={手机号}',
            proxies=self.proxies)
        if response.json()['code'] == '0' or response.json()['code'] == 0:
            logger.info("手机号:%s,释放成功" % 手机号)
        else:
            logger.info("手机号:%s,释放失败" % 手机号)

    def hz_获取手机号(self):
        self.项目ID = random.choice(self.项目ID列表)
        logger.info(f"豪猪-项目ID:{self.项目ID}")
        # https://服务器地址/sms/?api=getPhone&token=用户令牌&sid=项目ID
        if self.专属 != '':
            response = requests.get(
                f'https://{self.服务器地址}/sms/?api=getPhone&token={self.令牌}&sid={self.项目ID}&uid={self.专属}',
                proxies=self.proxies)
        else:
            response = requests.get(f'https://{self.服务器地址}/sms/?api=getPhone&token={self.令牌}&sid={self.项目ID}',
                                    proxies=self.proxies)
        try:
            return response.json()['phone']
        except:
            logger.info(response.text)
            return False

    def hz_获取个人信息(self):
        # https://服务器地址/sms/?api=getSummary&token=令牌
        response = requests.get(f'https://{self.服务器地址}/sms/?api=getSummary&token={self.令牌}',
                                proxies=self.proxies)
        res = response.json()
        logger.info(f"用户:{res['lx']}")
        logger.info(f"金额:{res['money']}")

    def yz_login(self):
        # http://api.sqhyw.net:90/api/logins?username=zzzxxx&password=xxxxx
        login_url = f'http://{self.服务器地址}/api/logins?username={self.cofing["椰子账号"]}&password={self.cofing["椰子密码"]}'
        response = requests.get(login_url, proxies=self.proxies)
        if '登录成功' in response.text:
            logger.info('登录成功')
            self.令牌 = response.json()['token']
            self.cofing['椰子token'] = self.令牌
            with open('config.josn', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.cofing, indent=4, ensure_ascii=False))
        else:
            logger.info('登录失败')

    def yz_获取个人信息(self):
        response = requests.get(f'http://{self.服务器地址}/api/get_myinfo?token={self.令牌}', proxies=self.proxies)
        res = response.json()['data'][0]
        logger.info("金额:" + str(res['money']))

    def yz_获取手机号(self):
        self.项目ID = random.choice(self.项目ID列表)
        logger.info(f"椰子-项目ID:{self.项目ID}")
        # http://api.sqhyw.net:90/api/get_mobile?token=你的token&project_id=专属项目对接码
        url = f'http://{self.服务器地址}/api/get_mobile?token={self.令牌}&project_id={self.项目ID}'
        response = requests.get(url, proxies=self.proxies)
        if 'mobile' in response.text:
            手机号 = response.json().get('mobile')
            logger.info("手机号:", 手机号)
            return 手机号
        else:
            logger.info(response.text)
            return False

    def yz_释放手机号(self, 手机号):
        # http://api.sqhyw.net:90/api/free_mobile?token=xxxxx&phone_num=xxxxx
        response = requests.get(f'http://{self.服务器地址}/api/free_mobile?token={self.令牌}&phone_num={手机号}',
                                proxies=self.proxies)
        logger.info(response.text)

    def yz_获取短信(self, 手机号):
        # http://api.sqhyw.net:90/api/get_message?token=你的token&project_id=项目ID&phone_num=取卡返回的手机号        等待 = 0
        等待 = 0
        while 等待 < 60:
            response = requests.get(
                f'http://{self.服务器地址}/api/get_message?token={self.令牌}&project_id={self.项目ID}&phone_num={手机号}',
                proxies=self.proxies)

            if 'code' in response.text:
                logger.info(response.text)
                return response.json().get('code')
            elif '短信还未到达,请继续获取' in response.text:
                time.sleep(1)
                logger.info(f"短信还未到达,请继续获取,等待时间:{等待}")
            else:
                logger.info(response.text)
                return None
            等待 += 1
        return None