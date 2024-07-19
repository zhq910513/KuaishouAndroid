#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @author: Kevin
# @contact: huguangjing211@gmail.com
# @file: appium.py
# @time: 2020/11/26 14:42
# @desc:

import os
import subprocess


class Appium(object):
    @staticmethod
    def close_appium(port: int):
        """
            先通过port获取pid
            然后通过pid杀死进程
        """
        cmd = "netstat -ano | findstr {}".format(port)
        pid = os.popen(cmd).read().split("LISTENING")[-1].strip()
        cmd = "taskkill -f -pid {}".format(pid)
        subprocess.Popen(cmd, shell=True)

    @staticmethod
    def start_appium(port: int, udid: str):
        """
            python启动appium服务
        """
        # python 启动appium服务
        bootstrap_port = str(port + 1)
        cmd = 'start /b appium -a '.format(udid) + "127.0.0.1" + ' -p ' + str(port) + ' -bp ' + str(
            bootstrap_port) + ' --log-level error'
        subprocess.Popen(
            cmd,
            shell=True
        )
