import hashlib
import random
import re
import time
from urllib.parse import urlencode

import requests
from pymongo import MongoClient

requests.packages.urllib3.disable_warnings()

client = MongoClient('mongodb://127.0.0.1:27017/kuaishou')
author_list_coll = client['kuaishou']['author_list']
profile_coll = client['kuaishou']['author_profile']
hy_profile_coll = client['kuaishou']['author_hy_profile']
phone_coll = client['kuaishou']['phones']


class Profile:
    def __init__(self):
        self.salt = '382700b563f4'

    @staticmethod
    def handle_map_param(did, did_gt, token, user):
        map_1 = 'isp=CTCC, mod=Xiaomi(Redmi 5 Plus), lon=114.106142, country_code=cn, kpf=ANDROID_PHONE, did={did}, kpn=KUAISHOU, net=WIFI, app=0, oc=HUAWEI, ud={ud}, hotfix_ver=, c=HUAWEI, sys=ANDROID_7.1.2, appver=6.5.0.9223, ftt=, language=zh-cn, iuid=, lat=22.559172, did_gt={did_gt}, ver=6.5, max_memory=192'.format(
            did=did, ud=token.split('-')[-1], did_gt=did_gt)
        map_2 = 'privacy=public, token={token}, browseType=1, lang=zh, client_key=3c2cd3f3, referer=ks://profile/{user}/-1/-1/8,2, count=30, os=android, user_id={user}'.format(
            token=token, user=user)

        map_1_list = [i.strip() for i in map_1.split(', ')]
        map_2_list = [j.strip() for j in map_2.split(', ')]
        return ''.join(sorted((map_1_list + map_2_list), reverse=False))

    @staticmethod
    def NStokensig(_sig, ClientSalt):
        _str = _sig + ClientSalt
        hashobj = hashlib.sha256(bytes(_str, encoding="utf8"))
        return hashobj.hexdigest()

    def sig(self, _uri):
        hashobj = hashlib.md5(bytes((_uri + self.salt), encoding="utf8"))
        return hashobj.hexdigest()

    def request(self, user_id):
        phones = [ph for ph in phone_coll.find({'status': 1, 'profile_type': 1})]
        if not phones:
            print('没有可用的账号')
            return 'break'
        phone = random.choice(phones)
        phone_num = phone.get('phone')
        ClientSalt = phone.get('ClientSalt')
        did = phone.get('did')
        did_gt = phone.get('did_gt')
        token = phone.get('token')

        url = 'https://apijs1.gifshow.com/rest/n/feed/profile2?' \
              'isp=CTCC' \
              '&mod=Xiaomi%28Redmi%205%20Plus%29' \
              '&lon=114.106142' \
              '&country_code=cn' \
              '&kpf=ANDROID_PHONE' \
              '&did={did}' \
              '&kpn=KUAISHOU' \
              '&net=WIFI' \
              '&app=0' \
              '&oc=HUAWEI' \
              '&ud={ud}' \
              '&hotfix_ver=' \
              '&c=HUAWEI' \
              '&sys=ANDROID_7.1.2' \
              '&appver=6.5.0.9223' \
              '&ftt=' \
              '&language=zh-cn' \
              '&iuid=' \
              '&lat=22.559172' \
              '&did_gt={did_gt}' \
              '&ver=6.5' \
              '&max_memory=192'.format(did=did, ud=token.split('-')[-1], did_gt=did_gt)
        uri = self.handle_map_param(did, did_gt, token, user_id)

        sig = self.sig(uri)
        NStokensig = self.NStokensig(sig, ClientSalt)

        FormData = {
            'token': token,
            'user_id': str(user_id),
            'lang': 'zh',
            'count': '30',
            'privacy': 'public',
            'referer': 'ks://profile/{}/-1/-1/8,2'.format(user_id),
            'browseType': '1',
            '__NStokensig': NStokensig,
            'client_key': '3c2cd3f3',
            'os': 'android',
            'sig': sig
        }

        data = urlencode(FormData)

        headers = {
            'Cookie': 'token={}'.format(token),
            'User-Agent': 'kwai-android',
            'X-REQUESTID': '958594',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-cn',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '217',
            'Host': 'api3.gifshow.com',
            'Accept-Encoding': 'gzip'
        }
        resp = requests.post(url=url, headers=headers, data=data, verify=False)

        return self.save_data(phone_num, user_id, resp.json())

    @staticmethod
    def save_data(phone_num, user_id, jsonData: dict):
        if jsonData.get('error_url') and '/verify/captcha.html?' in jsonData.get('error_url'):
            print('{} --- 需要验证'.format(phone_num))
            print(jsonData)
            phone_coll.update_one({'phone': phone_num},
                                  {'$set': {
                                      'status': 0,
                                      'profile_type': 2,
                                      'update_time': int(time.time())}}, upsert=True)
            return False
        if jsonData.get('error_msg') and '操作太快了' in jsonData.get('error_msg'):
            print('{} --- 操作太快了'.format(phone_num))
            print(jsonData)
            phone_coll.update_one({'phone': phone_num},
                                  {'$set': {
                                      'status': 2,
                                      'profile_type': 2,
                                      'update_time': int(time.time())}}, upsert=True)
            return False
        try:
            print('手机 {} ---- 加载用户作品列表 {}'.format(phone_num, user_id))
            if jsonData.get('feeds'):
                time_list = []
                for video in jsonData.get('feeds'):
                    time_list.append(video.get('timestamp', 0))

                if time_list:
                    time_list = sorted(time_list, reverse=True)
                    author_list_coll.update_one({'user_id': user_id}, {'$set': {'time_list': time_list, 'hy_time_status': 1}}, upsert=True)
                else:
                    author_list_coll.update_one({'user_id': user_id}, {'$set': {'hy_time_status': 2}}, upsert=True)

                jsonData.update({'user_id': user_id})
                hy_profile_coll.update_one({'user_id': user_id}, {'$set': jsonData}, upsert=True)
            else:
                author_list_coll.update_one({'user_id': user_id}, {'$set': {'hy_time_status': 2}}, upsert=True)

            return True
        except:
            return True


if __name__ == '__main__':
    while 1:
        pro = Profile()
        usrs = []
        print(author_list_coll.find({"verified" : False,'hy_contact_status': 1,"hy_time_status": None}).count())
        usrs.extend(author_list_coll.find({
            "verified" : False,
            'hy_contact_status': 1,
            "hy_time_status": None
        }).limit(30000))

        for num, usr in enumerate(usrs):
            print(num, '   ', usr['user_id'])
            pro.request(usr['user_id'])

            time.sleep(random.uniform(1, 3))
            # break
        time.sleep(10)
