#!/usr/bin/python3
# -*- coding:utf-8  -*-

import base64
import json
import requests
import logging
import os
from os import path

df = os.path.abspath(path.dirname(__file__))
dh = os.path.abspath(path.dirname(df))

logPath = os.path.abspath(os.path.join(dh + '/Logs/CaptchaTujianApi.log'))
logger = logging.getLogger(logPath)
fh = logging.FileHandler(logPath, mode='a+', encoding='utf-8')
fh.setLevel(logging.WARNING)
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

"""
    一、图片文字类型(默认 3 数英混合)：
        1 : 纯数字
        1001：纯数字2
        2 : 纯英文
        1002：纯英文2
        3 : 数英混合
        1003：数英混合2
         4 : 闪动GIF
        7 : 无感学习(独家)
        11 : 计算题
        1005:  快速计算题
        16 : 汉字
        32 : 通用文字识别(证件、单据)
        66:  问答题
        49 :recaptcha图片识别 参考 https://shimo.im/docs/RPGcTpxdVgkkdQdY
    二、图片旋转角度类型：
        29 :  旋转类型
    三、图片坐标点选类型：
        19 :  1个坐标
        20 :  3个坐标
        21 :  3 ~ 5个坐标
        22 :  5 ~ 8个坐标
        27 :  1 ~ 4个坐标
        48 : 轨迹类型
    四、缺口识别
        18：缺口识别
    五、拼图识别
        53：拼图识别
"""


class TujianApi():
    def __init__(self, imgPath):
        self.uname = 'zhq996'
        self.pwd = 'zhq91513'
        self.imgPath = imgPath
        self.typeid = 33

    def base64_api(self):
        """
        base64_api
        :param img: 传入的图片
        :param typeid: 验证码类型
        :return: 识别后的数值
        """
        with open(self.imgPath, 'rb') as f:
            base64_data = base64.b64encode(f.read())
            b64 = base64_data.decode()
        data = {"username": self.uname, "password": self.pwd, "typeid": self.typeid, "image": b64}
        result = json.loads(requests.post("http://api.ttshitu.com/predict", json=data).text)
        if result['success']:
            return result["data"]["result"]
        else:
            return result["message"]
        return ""

