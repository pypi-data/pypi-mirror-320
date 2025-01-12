# -*- coding: utf-8 -*-
# -------------------------------
import json

import requests


# @软件：PyCharm
# @项目：自己的库

# -------------------------------

# @文件：指纹浏览器.py
# @时间：2024/12/21 下午6:37
# @作者：小峰
# @邮箱：ling_don@qq.com

# -------------------------------
class ixBrowser:
    def __init__(self, 端口):
        self.端口 = 端口

    def 获取浏览器列表(self):
        data = {
            "page": 1,
            "limit": 10,
            "group_id": 0,
            "tag_id": 0,
            "name": ""
        }
        res = requests.post(f"http://127.0.0.1:{self.端口}/api/v2/profile-list", json=data)
        res = json.loads(res.text)
        return res['data']['data']

    def 打开浏览器(self, 窗口序号):
        data = {
            "profile_id": 窗口序号,
            "args": [
                "--disable-extension-welcome-page"
            ],
            "load_extensions": True,
            "load_profile_info_page": False,
            "cookies_backup": False,
            "cookie": ""
        }
        res = requests.post(f"http://127.0.0.1:{self.端口}/api/v2/profile-open-with-random-fingerprint", json=data)
        print(res.text)
        res = json.loads(res.text)
        return res['data']['debugging_address']

    def 关闭浏览器(self, 窗口序号):
        data = {
            "profile_id": 窗口序号
        }
        res = requests.post(f"http://127.0.0.1:{self.端口}/api/v2/profile-close", json=data)
        res = json.loads(res.text)
        return res['data']