import re
import time

from pymongo import MongoClient
import pandas as pd


client = MongoClient('mongodb://127.0.0.1:27017/kuaishou')
author_coll = client['kuaishou']['author_list']
web_author_coll = client['kuaishou']['web_author_list']


def save_format_data():
    data_list = []
    for num, i in enumerate(author_coll.find({'status': None,
                                              'hy_contact_status': 1,
                                              'hy_time_status': 1
                                              })):
        time_list = i.get('time_list')
        time_stamp = int(time.time()*1000) - (31*86400*1000)
        if time_list[0] > time_stamp:
            print('save...', '   ', str(num))
            activityTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time_list[0]/1000)))
            msg = {
                'keyword': i.get('keyword'),
                'user_id': i.get('user_id'),
                'kwaiId': i.get('kwaiId'),
                'user_name': i.get('user_name'),
                'contact': i.get('contact'),
                'activityTime': activityTime
            }
            # print(msg)
            data_list.append(msg)
            author_coll.update_one({'_id': i['_id']}, {'$set': {'status': time.strftime("%m-%d", time.localtime(int(time.time())))}}, upsert=True)
            # break
        else:
            author_coll.update_one({'_id': i['_id']}, {'$set': {'status': str(time.strftime("%m-%d", time.localtime(int(time.time()))))+'_no_use'}}, upsert=True)

    key_list = ['keyword', 'user_id', 'kwaiId', 'user_name' , 'contact', 'activityTime']
    info = pd.DataFrame(data_list, columns=key_list)
    info.to_csv('ks_old.csv')


if __name__ == '__main__':
    save_format_data()
