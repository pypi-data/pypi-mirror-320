# -*- coding: utf-8 -*-
# -------------------------------

# @软件：PyCharm
# @项目：自己的库

# -------------------------------

# @文件：tools.py
# @时间：2024/12/20 下午10:56
# @作者：小峰
# @邮箱：ling_don@qq.com

# ------------------------------
import psutil
import pygetwindow as gw
import ctypes
def cookies_dict(cookies:str):
    cookies_dict = {}
    for cookie in cookies.split(';'):
        key, value = cookie.split('=', 1)
        cookies_dict[key.strip()] = value.strip()
    return cookies_dict
def cookies_str(cookies:dict):
    cookies_str = ''
    for key, value in cookies.items():
        cookies_str += f'{key}={value};'
    return cookies_str
def 获取浏览器端口():
    def get_pid_from_handle(handle):
        # 使用 ctypes 来调用 Windows API 获取进程ID
        pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(handle, ctypes.byref(pid))
        return pid.value

    def get_window_handle(program_name):
        # 获取所有窗口
        windows = gw.getWindowsWithTitle(program_name)
        if windows:
            # 返回第一个匹配的窗口句柄
            return windows[0]._hWnd
        else:
            return None

    def get_ports_by_pid(pid):
        # 获取所有连接
        connections = psutil.net_connections(kind='inet')
        ports = []
        for conn in connections:
            if conn.pid == pid:
                ports.append(conn.laddr.port)
        return ports

    program_name = "chrome.exe"
    handle = get_window_handle(program_name)

    if handle:
        print(f"程序 '{program_name}' 的窗口句柄是: {handle}")
        pid = get_pid_from_handle(handle)
        print(f"程序 '{program_name}' 的进程ID是: {pid}")
        ports = get_ports_by_pid(pid)
        if ports:
            print(f"程序 '{program_name}' 的进程ID {pid} 使用的端口有: {ports}")
            print(int(ports[0]))
        else:
            print(f"未找到程序 '{program_name}' 的进程ID {pid} 使用的端口。")
    else:
        print(f"未找到名称为 '{program_name}' 的程序窗口。")
