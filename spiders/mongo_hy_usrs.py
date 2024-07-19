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


def find_hy_usrs():
    for num, usr in enumerate(author_list_coll.find({"verified" : False, 'hy_contact_status': None})):
        print(num)
        contact = []
        try:
            user_text = usr.get('user_text')
            if user_text:
                user_text = illegal_char(user_text).replace(' ', '').replace('-', '').replace('/', '').replace('_', '').replace(' - ', '').replace('—', '')

                contact = re.findall('0\d{2,3}-[1-9]\d{6,7}|1[3-9]\\d{9}|\d+-\d+-\d+|400\d{7}', user_text, re.S)
                if contact:
                    contact = ' / '.join(list(set(contact)))
                    print(contact)
                    hy_contact_status = 1
                    author_list_coll.update_one({'_id': usr['_id']}, {'$set': {'contact': contact, 'hy_contact_status': hy_contact_status}}, upsert=True)
                else:
                    hy_contact_status = 2
                    author_list_coll.update_one({'_id': usr['_id']}, {'$set': {'hy_contact_status': hy_contact_status}},
                                                upsert=True)
            else:
                hy_contact_status = 2
                author_list_coll.update_one({'_id': usr['_id']}, {'$set': {'hy_contact_status': hy_contact_status}}, upsert=True)
        except:
            pass


if __name__ == '__main__':
    find_hy_usrs()
