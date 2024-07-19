import hashlib
import random
import re
import time
from urllib.parse import urlencode

import requests
from pymongo import MongoClient

requests.packages.urllib3.disable_warnings()

client = MongoClient('mongodb://readWrite:readWrite123456@120.48.21.244:27017/kuaishou')
author_list_coll = client['kuaishou']['author_list']
profile_coll = client['kuaishou']['author_profile']
phone_coll = client['kuaishou']['phones']


class Profile:
    def __init__(self):
        self.salt = '382700b563f4'

    @staticmethod
    def handle_map_param(did, did_gt, token, user):
        map_1 = 'isp=CTCC, mod=Xiaomi(Redmi 5 Plus), lon=114.106142, country_code=cn, kpf=ANDROID_PHONE, did={did}, kpn=KUAISHOU, net=WIFI, app=0, oc=HUAWEI, ud={ud}, hotfix_ver=, c=HUAWEI, sys=ANDROID_7.1.2, appver=6.5.0.9223, ftt=, language=zh-cn, iuid=, lat=22.559172, did_gt={did_gt}, ver=6.5, max_memory=192'.format(
            did=did, ud=token.split('-')[-1], did_gt=did_gt)
        map_2 = 'client_key=3c2cd3f3,' \
                ' token={token},' \
                ' user={user},' \
                ' os=android,' \
                ' pv=true'.format(token=token, user=user)

        map_1_list = [i.strip() for i in map_1.split(',')]
        # print(map_1_list)
        map_2_list = [j.strip() for j in map_2.split(',')]
        # print(map_2_list)
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
        phones = [ph for ph in phone_coll.find({"profile_type" : 1})]
        if not phones:
            print('没有可用的账号')
            return 'break'
        phone = random.choice(phones)
        phone_num = phone.get('phone')
        ClientSalt = phone.get('ClientSalt')
        did = phone.get('did')
        did_gt = phone.get('did_gt')
        token = phone.get('token')

        url = 'https://apijs1.gifshow.com/rest/n/user/profile/v2?' \
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
            'pv': 'true',
            'os': 'android',
            'client_key': '3c2cd3f3',
            'token': token,
            'user': user_id,
            'sig': sig,
            '__NStokensig': NStokensig
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

    # 联系电话:    contact_status   有 1  无 2
    def save_data(self, phone_num, user_id, jsonData: dict):
        if jsonData.get('error_url') and '/verify/captcha.html?' in jsonData.get('error_url'):
            print('手机 {} --- 需要验证'.format(phone_num))
            print(jsonData)
            phone_coll.update_one({'phone': phone_num},
                                  {'$set': {
                                      'status': 0,
                                      'profile_type': 3,
                                      'update_time': int(time.time())}}, upsert=True)
            return False
        if jsonData.get('error_msg') and '操作太快了' in jsonData.get('error_msg'):
            print('手机 {} --- 操作太快了'.format(phone_num))
            print(jsonData)
            phone_coll.update_one({'phone': phone_num},
                                  {'$set': {
                                      'profile_type': 2,
                                      'update_time': int(time.time())}}, upsert=True)
            return False
        try:
            print('手机 {} ---- 加载用户 {}'.format(phone_num, user_id))
            profile_info = self.parse_profile(jsonData)
            print(profile_info)
            if profile_info:
                jsonData.update(profile_info)
                profile_coll.update_one({'user_id': user_id}, {'$set': jsonData}, upsert=True)
            else:
                if jsonData.get('error_msg'):
                    print(jsonData.get('error_msg'))
                    phone_coll.update_one({'phone': phone_num},
                                          {'$set': {'status': 0, 'update_time': int(time.time())}}, upsert=True)
                    return
                else:
                    author_list_coll.update_one({'user_id': user_id},
                                                {'$set': {'contact_status': 2, 'status': 'no_used'}}, upsert=True)
                    return

            contact = profile_info.get('contact')
            # print(contact)
            if not contact:
                author_list_coll.update_one({'user_id': user_id}, {'$set': {
                    'contact_status': 2,
                    'status': 'no_used',
                    'contact': contact
                }}, upsert=True)
            else:
                author_list_coll.update_one({'user_id': user_id}, {'$set': {
                    'contact_status': 1,
                    'contact': contact
                }}, upsert=True)
            return True
        except:
            return True

    def parse_profile(self, jsonData):
        data = {}
        contact_info = []
        contact = []

        try:
            if isinstance(jsonData, dict) and jsonData.get('userProfile'):
                if isinstance(jsonData.get('userProfile'), dict):
                    try:
                        adBusinessInfo = jsonData.get('userProfile').get('adBusinessInfo')
                        if adBusinessInfo:
                            phoneNo = adBusinessInfo.get('conversionBar')
                            if phoneNo:
                                contact_info.append(phoneNo.get('phoneNo'))

                            phoneInfo = adBusinessInfo.get('phoneInfo')
                            if phoneInfo:
                                contact_info.append(phoneInfo.get('phoneNo'))

                        profile = jsonData.get('userProfile').get('profile')
                        if profile:
                            kwaiId = profile.get('kwaiId')
                            if kwaiId:
                                contact_info.append(kwaiId)
                                data.update({'kwaiId': kwaiId})
                            user_name = profile.get('user_name')
                            data.update({'user_name': user_name})
                            user_text = profile.get('user_text')
                            if user_text:
                                contact_info.append(self.illegal_char(user_text))
                            verified_desc = profile.get('verifiedDetail').get('description') if profile.get(
                                'verifiedDetail') else None
                            data.update({'verified_desc': verified_desc})

                        if contact_info:
                            # print(contact_info)
                            for info in contact_info:
                                info = info.replace(' ', '').replace('-', '').replace('/', '').replace('_', '').replace(' - ', '').replace('—', '')
                                results = re.findall('0\d{2,3}-[1-9]\d{6,7}|1[3-9]\\d{9}|\d+-\d+-\d+|400\d{7}', info, re.S)
                                contact.extend(results)
                            if contact:
                                contact = ' / '.join(list(set(contact)))
                                data.update({'contact': contact})

                        return data
                    except:
                        return None
                else:
                    return None
            else:
                return None
        except:
            return None

    # 清洗非法字符
    @staticmethod
    def illegal_char(_str):
        s = re.compile(u"[^"
                       u""u"\u4e00-\u9fa5"
                       u""u"\u0041-\u005A"
                       u"\u0061-\u007A"
                       u"\u0030-\u0039"
                       u"\u3002\uFF1F\uFF01\uFF0C\u3001\uFF1B\uFF1A\u300C\u300D\u300E\u300F\u2018\u2019\u201C\u201D\uFF08\uFF09\u3014\u3015\u3010\u3011\u2014\u2026\u2013\uFF0E\u300A\u300B\u3008\u3009"
                       u"\!\@\#\$\%\^\&\*\(\)\-\=\[\]\{\}\\\|\;\'\:\"\,\.\/\<\>\?\/\*\+"
                       u"]+").sub('', _str)
        return s


if __name__ == '__main__':
    while 1:
        pro = Profile()
        usrs = []
        usrs.extend(author_list_coll.find({
            'verified': True,
            'status': None,
            'contact_status': None,
            'timeStamp': {'$lt': 1640966399}
        }).limit(300))
        if not usrs:
            usrs.extend(author_list_coll.find({
                'verified': True,
                'status': None,
                'contact_status': None,
            }).limit(300))

        for num, usr in enumerate(usrs):
            try:
                # 蓝v 10     橙v 4
                _type = usr.get('verifiedDetail').get('type')
                if _type != 10:
                    print('cheng v')
                    author_list_coll.update_one({'_id': usr['_id']},
                                                {'$set': {'lanv_status': 'chengv', 'status': 'chengv'}}, upsert=True)
                    continue

                print(num, '   ', usr['user_id'])
                if pro.request(usr['user_id']) == 'break':
                    time.sleep(30)
                    break
                time.sleep(random.uniform(1, 3))
            except:
                continue

        time.sleep(10)
