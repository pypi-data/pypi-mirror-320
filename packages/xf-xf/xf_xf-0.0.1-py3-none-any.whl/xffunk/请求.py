# -*- coding: utf-8 -*-
# -------------------------------

# @软件：PyCharm
# @项目：自己的库

# -------------------------------

# @文件：请求.py
# @时间：2024/12/20 下午11:05
# @作者：小峰
# @邮箱：ling_don@qq.com

# -------------------------------
import requests
import time
def get请求(url, headers, data=None, params=None, cookies=None, proxies=None):
    for _ in range(3):  # 尝试3次
        try:
            response = requests.get(url, headers=headers, data=data, params=params, cookies=cookies,
                                    proxies=proxies)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            time.sleep(1)
    return None


def post请求(url, headers, data=None, params=None, cookies=None, files=None, json=None):
    for _ in range(3):  # 尝试3次
        try:
            # 发送POST请求
            response = requests.post(url, headers=headers, data=data, params=params, cookies=cookies, files=files,
                                     json=json)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            time.sleep(1)
    return None
