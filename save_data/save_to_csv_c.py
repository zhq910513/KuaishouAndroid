import re
import time

from pymongo import MongoClient
import pandas as pd
import pprint
pp=pprint.PrettyPrinter(indent=4)

client = MongoClient('mongodb://readWrite:readWrite123456@180.76.162.140:27017/ks')
author_coll = client['ks']['author_list']


def save_format_data():
    data_list = []
    try:
        for num, i in enumerate(author_coll.find({"contact_status": 1},no_cursor_timeout=True)):
            # for num, i in enumerate(author_coll.find({'verified': False,'contact_status': 1})):
            # for num, i in enumerate(author_coll.find({'verified': True, 'status': 'no_used', 'contact_status': 2, 'lanv_status': 1}, no_cursor_timeout=True)):
            print('save...', '   ', str(num))
            expireTime = None
            blueVStatus = None
            verified_company = None
            blueVType = None
            web_data = i.get('web_data')
            verifiedDetail = i.get('verifiedDetail')
            if verifiedDetail:
                verified_company = verifiedDetail.get("description")
                blueVType = verifiedDetail.get("type")
            if web_data:
                expireTime = web_data.get("expireTime")
                blueVStatus = web_data.get("blueVStatus")
            msg = {
                'keyword': i.get('keyword'),
                'user_id': i.get('user_id'),
                'user_name': i.get('user_name'),
                'verified_company': verified_company,
                'blueVType': blueVType,
                'expireTime': expireTime,
                'blueVStatus': blueVStatus,
                'contact': i.get('contact'),
                'lanv_status': i.get("lanv_status"),
                'contact_status': i.get("contact_status")
            }
            # print(msg)
            data_list.append(msg)
            author_coll.update_one({'hash_key': i['hash_key']}, {'$set': {'handle_date': time.strftime("%Y-%m-%d", time.localtime(int(time.time())))}}, upsert=True)
            # author_coll.update_one({'_id': i['_id']}, {'$set': {'status': str(time.strftime("%m-%d", time.localtime(int(time.time()))))+'_no_contact'}}, upsert=True)
            # break
    except Exception as error:
        print(error)

    key_list = ['keyword', 'user_id', 'user_name' , 'verified_company', 'blueVType', 'expireTime', 'blueVStatus', 'contact', 'lanv_status', 'contact_status']
    info = pd.DataFrame(data_list, columns=key_list)
    info.to_csv('ks_contact.csv')
    # info.to_csv('ks_no_phone.csv')


if __name__ == '__main__':
    # 截至时间
    # str_time = '2021-12-31 23:59:59'
    # stamp_time = int(time.mktime(time.strptime(str_time, "%Y-%m-%d %H:%M:%S")))
    save_format_data()
