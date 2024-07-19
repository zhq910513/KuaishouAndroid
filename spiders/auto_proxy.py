#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company_info
@file: auto_proxy.py
@time: 2023/7/6 14:44
"""

import pprint

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
pp = pprint.PrettyPrinter(indent=4)

import time

import requests

client = MongoClient('mongodb://127.0.0.1:27017/zyl_company_info')
ip_coll = client['zyl_company_info']['ips']


def get_proxies():
    """
    用户名:18613043787
    密码:18613043787
    管理地址:http://18823450513.user.xiecaiyun.com
    到期时间:2023/04/13 16:00:00
    :return:
    """
    try:
        # API链接    后台获取链接地址
        proxyAPI = "http://18823450513.user.xiecaiyun.com/api/proxies?action=getJSON&key=NP812539CC&count=1&word=&rand=true&norepeat=true&detail=true&ltime=&idshow=false"
        proxyusernm = "18823450513"  # 代理帐号
        proxypasswd = "18823450513"  # 代理密码

        # 获取IP
        resp = requests.get(proxyAPI)
        time.sleep(5)
        if resp.status_code == 200 and resp.json().get("success"):
            ip_list = []
            for info in resp.json().get("result"):
                ip_list.append({
                    "ip": info["ip"],
                    "proxies": {
                        'http': "http://" + proxyusernm + ":" + proxypasswd + "@" + info["ip"] + ":" + "%d" % info[
                            "port"],
                        'https': "http://" + proxyusernm + ":" + proxypasswd + "@" + info["ip"] + ":" + "%d" % info[
                            "port"]
                    },
                    "status": 1,
                    "end_time": info.get("ltime")
                })
            if ip_list:
                for ip_info in ip_list:
                    ip_coll.update_one({"ip": ip_info["ip"]}, {"$set": ip_info}, upsert=True)
        else:
            if "访问频率过快惩罚截止时间" in resp.json().get("message"):
                print(resp.json().get("message"))
                time.sleep(600)
            else:
                print(resp.json())
    except Exception as error:
        print(error)


def get_ip():
    try:
        now_time = int(time.time())
        ip_info = ip_coll.find_one({"status": 1, "end_time": {"$gt": now_time}})
        if ip_info:
            return ip_info
        else:
            print("无可用IP,冷却中...")
            get_proxies()
            return get_ip()
    except Exception as error:
        print(error)


if __name__ == "__main__":
    # pp.pprint(get_ip())
    get_proxies()