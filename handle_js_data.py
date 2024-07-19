#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: kuaishou_android
@file: handle_js_data.py
@time: 2023/7/26 3:27
"""
import copy
import os
import pprint
import re
import subprocess
from os import path

from pymongo import MongoClient

client = MongoClient('mongodb://readWrite:readWrite123456@180.76.162.140:27017/ks')
phone_coll = client['ks']['phones']

phone_format_data = {
    "uid": "",
    "number": 0,
    "phone_code": "",
    "token": "",
    "client_key": "",
    "did": "",
    "did_gt": "",
    "sys": "",
    "appver": "",
    "status": 0
}

_path = os.path.abspath(path.dirname(__file__))
frida_path = os.path.abspath(os.path.join(_path + r'/software/frida-server64'))
js_path = os.path.abspath(os.path.join(_path + r'/ks_token.js'))
pp = pprint.PrettyPrinter(indent=4)


# 通用shell
def adb_shell(cmd):
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return str(result.stdout.read())


# 更新phone数据到数据库
def update_phone_info(_data):
    try:
        phone_coll.update_one({"uid": _data["uid"]}, {"$set": _data}, upsert=True)
        pp.pprint(_data)
        print(f"Notice --- 手机[{_data['number']}]信息入库成功，请执行下一部手机 ---")
    except Exception as error:
        print(error)


# 检查frida结果
def check_result(_str, _data):
    try:
        if "unable to find application" in _str:
            print("Warning --- App 未安装 ---")
        else:
            token = re.search("token=(.*?),", _str, re.S).group(1)
            if token and not _data.get("token"):
                _data["token"] = token

            did = re.search("did=(.*?),", _str, re.S).group(1)
            if did and not _data.get("did"):
                _data["did"] = did

            did_gt = re.search("did_gt=(\d+),", _str, re.S).group(1)
            if did_gt and not _data.get("did_gt"):
                _data["did_gt"] = did_gt

            client_key = re.search("client_key=(.*?),", _str, re.S).group(1)
            if client_key and not _data.get("client_key"):
                _data["client_key"] = client_key

            _sys = re.search("sys=(.*?),", _str, re.S).group(1)
            if _sys and not _data.get("sys"):
                _data["sys"] = _sys

            appver = re.search("appver=(.*?),", _str, re.S).group(1)
            if appver and not _data.get("appver"):
                _data["appver"] = appver
    except Exception as error:
        print(error)
    finally:
        if _data.get("uid") and _data.get("token") and _data.get("number") and _data.get("client_key") and _data.get("sys") and _data.get("appver") and _data.get("did") and _data.get("did_gt"):
            _data["status"] = 1
            return _data, False
        else:
            return _data, False


# 实时获取frida结果并检测
def timely_get_frida_result(cmd, _data):
    # 创建一个子进程并指定stdout和stderr为PIPE，这样可以捕获子进程的输出
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 读取子进程的输出
    data_status = True
    while data_status:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            result = output.strip()
            _data, data_status = check_result(result, _data)
        if not data_status:
            break

    # 等待子进程执行完毕，并获取返回码
    return_code = process.wait()
    print("子进程返回码:", return_code)
    update_phone_info(_data)


# 查询设备uid
def search_devices():
    cmd = "adb devices"
    devices = [msg for msg in re.findall(r'\\n(.*?)\\r', adb_shell(cmd), re.S) if msg]
    return str(devices[0]).split("\\")[0]


# 检查系统frida环境
def check_win_frida_env():
    # 进行adb端口转发
    cmd = "adb forward tcp:27042 tcp:27042"
    if "27042" in adb_shell(cmd):
        print("Notice --- frida 27042 端口监听成功 ---")
    else:
        print("Warning --- frida 27042 端口已经监听 ---")

    cmd = "adb forward tcp:27043 tcp:27043"
    if "27043" in adb_shell(cmd):
        print("Notice --- frida 27043 端口监听成功 ---")
    else:
        print("Warning --- frida 27043 端口已经监听 ---")


# 检查手机frida环境
def check_phone_frida_env():
    cmd = f"adb push {frida_path} /data/local/tmp"
    if "1 file pushed, 0 skipped" in adb_shell(cmd):
        print("Notice --- frida 放入手机成功 ---")

        result = input("请打开CMD命令行，依次输入如下代码："
                       "\n\n"
                       "adb shell\n"
                       "su\n"
                       "cd /data/local/tmp\n"
                       "chmod 755 frida-server64\n"
                       "./frida-server64 &\n"
                       "\n\n"
                       "CMD输入完后页面出现 [1] 即按下Enter键:\n")
        if result == "":
            print("Notice --- 即将进入下一步... ---")
        else:
            print("Warning --- 输入错误，重新执行中... ---")
            return run()
    else:
        print("Warning --- frida 放入手机失败 ---")
        return


# 使用frida连接App
def contact_app(_data):
    cmd = f"frida -U -f com.smile.gifmaker -l {js_path} --no-pause"
    timely_get_frida_result(cmd, _data)


def run():
    _data = copy.deepcopy(phone_format_data)

    number = input("Notice --- 请输入当前手机的编号(查看手机背后登记号码)：")
    try:
        _data["number"] = int(number)
    except Exception as error:
        print(f"Warning --- 请输入数字,不要附带其他符号或字符 {error}---")
        return

    phone_code = input("Notice --- 请输入当前快手的账号(手机号)，此为选填项：")
    _data["phone_code"] = phone_code

    phone_uid = search_devices()
    if not phone_uid:
        print("Warning --- 未检测到设备，请检查设备插口及驱动 ---")
    _data["uid"] = phone_uid

    check_win_frida_env()
    check_phone_frida_env()
    contact_app(_data)


if __name__ == "__main__":
    run()
