import logging
import random
import pprint
import re

from spiders.auto_proxy import get_ip

pp=pprint.PrettyPrinter(indent=4)
from multiprocessing.pool import ThreadPool
import time

import requests
from pymongo import MongoClient
requests.packages.urllib3.disable_warnings()
client = MongoClient('mongodb://readWrite:readWrite123456@127.0.0.1:27017/ks')
# client = MongoClient('mongodb://readWrite:readWrite123456@180.76.162.140:27017/ks')
author_list_coll = client['ks']['author_list']

ip_client = MongoClient('mongodb://127.0.0.1:27017/zyl_company_info')
ip_coll = ip_client['zyl_company_info']['ips']

query = "query graphqlSearchUser($keyword: String, $pcursor: String, $searchSessionId: String) {\n  visionSearchUser(keyword: $keyword, pcursor: $pcursor, searchSessionId: $searchSessionId) {\n    result\n    users {\n      fansCount\n      photoCount\n      isFollowing\n      user_id\n      headurl\n      user_text\n      user_name\n      verified\n      verifiedDetail {\n        description\n        iconType\n        newVerified\n        musicCompany\n        type\n        __typename\n      }\n      __typename\n    }\n    searchSessionId\n    pcursor\n    __typename\n  }\n}\n"


def thread_handle(_s, _pro, _list, _func):
    try:
        pool = ThreadPool(processes=4)
        thread_list = []
        for _ls in _list:
            out = pool.apply_async(func=_func, args=(_s, _pro, _ls,))  # 异步
            thread_list.append(out)
            # break
        pool.close()
        pool.join()
    except Exception as error:
        print(error)

def get_bluev(_session, _ip_info, _info, retry=0):
    try:
        # time.sleep(random.uniform(1, 3))
        hash_key = _info.get("hash_key")
        web_user_id = _info.get("user_id")

        info_headers = {
            'Host': 'webview-b.e.kuaishou.com',
            'Connection': 'keep-alive',
            'Content-Length': '28',
            'Accept': 'application/json',
            'Origin': 'https://webview-b.e.kuaishou.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; Redmi 5 Plus Build/N2G47H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.158 Mobile Safari/537.36 Kwai/6.5.0.9223',
            'Content-Type': 'application/json;charset=UTF-8',
            'Referer': 'https://webview-b.e.kuaishou.com/?&hyId=merchant_aggregate',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.9',
            'Cookie': 'isp=CTCC; mod=Xiaomi%28Redmi+5+Plus%29; kpf=ANDROID_PHONE; kpn=KUAISHOU; app=0; oc=HUAWEI; hotfix_ver=; c=HUAWEI; ftt=; language=zh-cn; iuid=; did_gt=1631786306391; ver=6.5; max_memory=192; sys=ANDROID_7.1.2; appver=6.5.0.9223; did=ANDROID_d75ed9f9ae768bed; client_key=3c2cd3f3; country_code=cn; lon=114.106142; lat=22.559172; ud=2285319590; token=82f43ba96cac4c2690b5bf7292bd1b4a-2285319590; Hm_lvt_86a27b7db2c5c0ae37fee4a8a35033ee=1631863132; Hm_lpvt_86a27b7db2c5c0ae37fee4a8a35033ee=1631863132; net=LTE; sid=8a970619-f9b0-46fc-820d-d319cff2104d',
            'X-Requested-With': 'com.smile.gifmaker'
        }
        _session.headers.update(info_headers)

        formData = {
            "userId": web_user_id
        }

        url = 'https://webview-b.e.kuaishou.com/rest/business/h5/profile/bluev/detail'

        resp = _session.post(url=url, json=formData, timeout=10, verify=False)
        if resp.status_code == 200:
            save_data(hash_key, resp.json())
        elif resp.status_code == 501:
            print(resp.status_code)
            time.sleep(300)
            ip_coll.update_one({"ip": _ip_info["ip"]}, {"$set": {"status": 0}}, upsert=True)
            new_ip_info = get_ip()
            print(new_ip_info["ip"])
            _session.proxies.update(new_ip_info["proxies"])
            return get_bluev(_session, new_ip_info, _info, retry + 1)
        else:
            print(resp.status_code)
    except Exception as error:
            if retry < 5:
                ip_coll.update_one({"ip": _ip_info["ip"]}, {"$set": {"status": 0}}, upsert=True)
                new_ip_info = get_ip()
                print(new_ip_info["ip"])
                _session.proxies.update(new_ip_info["proxies"])
                return get_bluev(_session, new_ip_info, _info, retry+1)
            else:
                print(error)

def save_data(hash_key, jsonData):
    try:
        msg = {}
        if jsonData.get('error_msg') == '操作已超时':
            # 更新数据
            msg = {
                "hash_key": hash_key,
                "lanv_status": 400
            }

        elif jsonData.get('data').get('profileDetail'):
            blueV = jsonData.get('data').get('blueV')
            blueVStatus = jsonData.get('data').get('blueVStatus')
            profilePic = jsonData.get('data').get('profileDetail').get('profilePic')
            eTime = jsonData.get('data').get('profileDetail').get('expireTime')
            expireTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(eTime / 1000)))
            timeStamp = int(eTime / 1000)
            msg = {
                "hash_key": hash_key,
                "lanv_status": 1,
                "web_data":
                    {
                        'blueV': blueV,
                        'blueVStatus': blueVStatus,
                        'profilePic': profilePic,
                        'expireTime': expireTime,
                        'expireTimeStamp': timeStamp
                    }
            }

        else:
            print(f"--- 出现新数据 {jsonData} ---")

        if msg:
            # 更新数据
            print(msg)
            author_list_coll.update_one({'hash_key': hash_key}, {'$set': msg}, upsert=True)
        else:
            author_list_coll.update_one({"hash_key": hash_key}, {"$set": {"lanv_status": 0}}, upsert=True)
    except Exception as error:
        print(error)

def handle_contact(_info):
    contact = []
    try:
        _info = _info.replace(' ', '').replace('-', '').replace('/', '').replace('_', '').replace(' - ', '').replace('—', '')
        results = re.findall('0\d{2,3}-[1-9]\d{6,7}|1[3-9]\\d{9}|\d+-\d+-\d+|400\d{7}', _info, re.S)
        contact.extend(results)
    except:
        pass
    if contact:
        contact = ' / '.join(list(set(contact)))
    return contact


if __name__ == '__main__':
    # while 1:
    #     _usr_list = []
    #     _usr_list.extend(author_list_coll.find({"verifiedDetail.type": 10, "lanv_status": None}).limit(1))
    #     if _usr_list:
    #         # print(_usr_list[0])
    #         info_session = requests.session()
    #
    #         ip_info = get_ip()
    #         # ip_info = {}
    #         print(ip_info["ip"])
    #
    #         info_session.proxies.update(ip_info["proxies"])
    #         info_session.adapters.DEFAULT_RETRIES = 5
    #         info_session.keep_alive = False
    #         info_session.verify = False
    #
    #         thread_handle(info_session, ip_info, _usr_list, get_bluev)
    #     # else:
    #     #     time.sleep(300)

    # while True:
    #     for num, i in enumerate(author_list_coll.find({})):
    #         print(num)
    #         _hash_key = i["hash_key"]
    #         usr_text = i.get("user_text")
    #         if usr_text:
    #             _contact = handle_contact(usr_text)
    #             if _contact:
    #                 print(_contact)
    #                 author_list_coll.update_one({"hash_key": _hash_key}, {"$set": {"contact": _contact, "contact_status": 1}}, upsert=True)
    #             else:
    #                 author_list_coll.update_one({"hash_key": _hash_key}, {"$set": {"contact_status": 0}}, upsert=True)
    #         else:
    #             author_list_coll.update_one({"hash_key": _hash_key}, {"$set": {"contact_status": 0}}, upsert=True)

    while True:
        for num, i in enumerate(author_list_coll.find({"lanv_status": None}).limit(1000)):
            print(num)
            _hash_key = i["hash_key"]
            author_list_coll.update_one({"hash_key": _hash_key}, {"$set": {"lanv_status": 0}}, upsert=True)
