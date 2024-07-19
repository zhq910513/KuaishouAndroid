# coding=utf-8
import hashlib
import json
import random
import time
from urllib.parse import urlencode

import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMPLEMENTOFDEFAULT"

client = MongoClient('mongodb://readWrite:readWrite123456@120.48.21.244:27017/kuaishou')
key_coll = client['kuaishou']['keys']
author_list_coll = client['kuaishou']['author_list']
profile_coll = client['kuaishou']['author_profile']
phone_coll = client['kuaishou']['phones']
web_author_coll = client['kuaishou']['web_author_list']

# 代理服务器
proxyHost = "27.44.216.177"
proxyPort = "4278"

proxyMeta = "http://%(host)s:%(port)s" % {

    "host": proxyHost,
    "port": proxyPort,
}

proxies = {
    "http": proxyMeta,
    "https": proxyMeta
}


def get_keys(phone):
    try:
        keys = []
        url = "http://120.48.21.244:65512/ks_server/keys?hash_key={}".format(phone)
        response = requests.get(url=url)
        code = json.loads(response.text)["code"]
        if code == "9999":
            keys = json.loads(response.text)["data"]
    except Exception as error:
        print(error)
    return keys

class UserList:
    def __init__(self):
        self.salt = '382700b563f4'

    @staticmethod
    def handle_map_param(did, did_gt, token, keyword, pcursor=None, ussid=None):
        map_1 = 'isp=CTCC, mod=Xiaomi(Redmi 5 Plus), lon=0, country_code=cn, kpf=ANDROID_PHONE, did={did}, kpn=KUAISHOU, net=WIFI, app=0, oc=HUAWEI, ud={ud}, hotfix_ver=, c=HUAWEI, sys=ANDROID_7.1.2, appver=6.5.0.9223, ftt=, language=zh-cn, iuid=, lat=0, did_gt={did_gt}, ver=6.5, max_memory=192'.format(did=did, ud=token.split('-')[-1], did_gt=did_gt)
        if not pcursor and not ussid:
            map_2 = 'client_key=3c2cd3f3, token={token}, os=android, keyword={keyword}'.format(token=token, keyword=keyword)
        else:
            map_2 = 'ussid={ussid}, token={token}, keyword={keyword}, pcursor={pcursor}, client_key=3c2cd3f3, os=android'.format(ussid=ussid, token=token, keyword=keyword, pcursor=pcursor)

        map_1_list = [i.strip() for i in map_1.split(',')]
        map_2_list = [j.strip() for j in map_2.split(',')]
        return ''.join(sorted((map_1_list + map_2_list), reverse=False))

    @staticmethod
    def NStokensig(_sig, ClientSalt):
        _str = _sig + ClientSalt
        hashobj = hashlib.sha256(bytes(_str, encoding="utf8"))
        return hashobj.hexdigest()

    def sig(self, _uri):
        hashobj = hashlib.md5(bytes((_uri + self.salt), encoding="utf8"))
        return hashobj.hexdigest()

    def request(self, keyword, pcursor=0, ussid=None):
        phone = phone_coll.find_one({"phone" : phoneNum})
        phone_num = phone.get('phone')
        ClientSalt = phone.get('ClientSalt')
        did = phone.get('did')
        # did = random.choice(['ANDROID_7e630ed90c304b99'])
        # print(did)
        did_gt = phone.get('did_gt')
        token = phone.get('token')

        url = 'https://apijs1.gifshow.com/rest/n/search/user' \
              '?isp=CTCC' \
              '&mod=Xiaomi%28Redmi%205%20Plus%29' \
              '&lon=0' \
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
              '&lat=0' \
              '&did_gt={did_gt}' \
              '&ver=6.5' \
              '&max_memory=192'.format(did=did, ud=token.split('-')[-1], did_gt=did_gt)
        # print('****' * 50, '\n',url)

        if not pcursor and not ussid:
            uri = self.handle_map_param(did, did_gt, token, keyword)
            sig = self.sig(uri)
            # print(keyword, sig)
            NStokensig = self.NStokensig(sig, ClientSalt)
            FormData = {
                'keyword': keyword,
                'client_key': '3c2cd3f3',
                '__NStokensig': NStokensig,
                'token': token,
                'os': 'android',
                'sig': sig
            }
            # print( sig, '\n', NStokensig, '\n', FormData, '****' * 50)
        else:
            if pcursor != 'no_more':
                uri = self.handle_map_param(did, did_gt, token, keyword, pcursor, ussid)
                sig = self.sig(uri)
                NStokensig = self.NStokensig(sig, ClientSalt)
                FormData = {
                    'keyword': keyword,
                    'pcursor': pcursor,
                    'ussid': ussid,
                    '__NStokensig': NStokensig,
                    'token': token,
                    'client_key': '3c2cd3f3',
                    'os': 'android',
                    'sig': sig
                }
                # print('****'*50,'\n', sig,'\n', NStokensig, '\n', FormData, '****'*20)
            else:
                key_coll.update_one({'keyword': keyword}, {'$set': {'status': 1}}, upsert=True)
                return
        data = urlencode(FormData)

        headers = {
            'Cookie': 'token={}'.format(token),
            'User-Agent': 'kwai-android',
            'X-REQUESTID': '502506',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-cn',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '222',
            'Host': 'apijs1.gifshow.com',
            'Accept-Encoding': 'gzip'
        }
        if pro:
            resp = requests.post(url=url, headers=headers, proxies=proxies, data=data, verify=False)
        else:
            resp = requests.post(url=url, headers=headers, data=data, verify=False)
        if resp.status_code == 200:
            self.parse_usr_list(keyword, phone_num, pcursor, resp.json())
        else:
            print(resp.status_code)

    def parse_usr_list(self, keyword, phone_num, pcursor, jsonData):
        try:
            if jsonData.get('result') == 1:
                if jsonData.get('users') and isinstance(jsonData.get('users'), list):
                    print('手机 {} --- 搜索关键词--{}  第{}页 结果 {}'.format(phone_num, keyword, pcursor,
                                                                   len(jsonData.get('users'))))
                    self.save_data(keyword, jsonData.get('users'))

                pcursor = jsonData.get('pcursor')
                ussid = jsonData.get('ussid')
                if pcursor and ussid:
                    time.sleep(random.uniform(5, 10))
                    return self.request(keyword, pcursor, ussid)
            else:
                print(jsonData)
                time.sleep(300)
                phone_coll.update_one({'phone': phone_num},
                                      {'$set': {'list_type': 2, 'profile_type': 1, 'update_time': int(time.time())}},
                                      upsert=True)
        except Exception as error:
            print(error)

    @staticmethod  # 过期时间:    lanv_status   匹配 1  未匹配 2  用过 '09-15'
    def save_data(keyword, dataList):
        try:
            if dataList:
                for usr in dataList:
                    # 更新关键词
                    user_id = usr.get('user_id')
                    if user_id:
                        usr.update({'keyword': keyword, 'update_time': time.strftime("%Y-%m-%d", time.localtime(int(time.time())))})

                    if usr.get('verifiedDetail'):
                        if usr.get('verifiedDetail').get('type') != 10:
                            usr.update({
                                'lanv_status': 'chengv',
                                'status': 'chengv'
                            })
                        else:
                            # 更新过期时间
                            user_name = usr.get('user_name')
                            if user_name:
                                info = web_author_coll.find_one({'user_name': user_name})
                                if info:
                                    if info.get('status') == 1:
                                        author_list_coll.update_one({'user_id': user_id},
                                                                    {'$set': {
                                                                        'contact_status': 1,
                                                                        'lanv_status': 1,
                                                                        'status': '09-15'
                                                                    }}, upsert=True)
                                    else:
                                        usr.update({
                                            'lanv_status': 1,
                                            'expireTime': info.get('expireTime'),
                                            'web_user_id': info.get('web_user_id'),
                                            'timeStamp': info.get('timeStamp')})
                                else:
                                    usr.update({'lanv_status': 2})
                    # 插入数据
                    try:
                        author_list_coll.update_one({'user_id': user_id}, {'$set': usr}, upsert=True)
                    except Exception as error:
                        print(error)
        except:
            pass


if __name__ == '__main__':
    pro = False
    phoneNum = 1
    hash_key = 3
    while 1:
        if phone_coll.find({'phone': phoneNum}):
            ul = UserList()
            keys = get_keys(hash_key)
            for num, key in enumerate(keys):
                try:
                    print(num, '   ', key.get('keyword'))
                    ul.request(key.get('keyword'))
                    # break
                except:
                    continue
        else:
            time.sleep(60)
