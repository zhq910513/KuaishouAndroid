import datetime
import re

from bson.objectid import ObjectId
from pymongo import MongoClient

client = MongoClient('mongodb://readWrite:readWrite123456@120.48.21.244:27017/kuaishou')
key_coll = client['kuaishou']['keys']
author_list_coll = client['kuaishou']['author_list']

"""
    收录关键词
"""


def hash_key(keyword):
    try:
        sum_str = 0
        for i in str(keyword):
            sum_str += ord(i)
        return int(sum_str % 20)
    except:
        return 0


def check(_string):
    zhmodel = re.compile(u'[\u4e00-\u9fa5]')
    match = zhmodel.search(_string)
    if match:
        return True
    else:
        return False


def handle_keys():
    with open(r'D:\Projects\kuaishou_android\keys.txt', 'r', encoding='utf-8') as f:
        keys = f.readlines()

    for num, key in enumerate(keys):
        if num> 332500:
            print(num)
            if not key:
                continue
            new_key = key.replace('\n', '').replace('\t', '').replace('\r', '').strip()
            hashkey = hash_key(new_key)
            if hashkey == 0:
                hashkey = 20
            if check(new_key):
                key_coll.update_one({'keyword': new_key}, {'$set': {'keyword': new_key, 'hash_key': hashkey}}, upsert=True)


"""
    统计每天数据
"""


def object_id_from_datetime(from_datetime=None):
    if not from_datetime:
        from_datetime = datetime.datetime.now()
    return ObjectId.from_datetime(generation_time=from_datetime)


def count_data(date):
    datetime_start = datetime.datetime(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2]), 0, 0,
                                       0)
    id_start = object_id_from_datetime(datetime_start)

    datetime_end = datetime.datetime(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2]) + 1, 0,
                                     0, 0)
    # datetime_end = datetime.datetime(2021, 12, 1, 0, 0, 0)
    id_end = object_id_from_datetime(datetime_end)

    today_data_count = author_list_coll.find(
        {"_id": {"$gt": ObjectId("{}".format(id_start)), "$lt": ObjectId("{}".format(id_end))}}).count()
    lanv_count = author_list_coll.find({'verified': True, "_id": {"$gt": ObjectId("{}".format(id_start)),
                                                                  "$lt": ObjectId("{}".format(id_end))}}).count()
    print('{} 一共新增用户：{}    蓝v : {}'.format(date, today_data_count, lanv_count))


if __name__ == '__main__':
    handle_keys()

    # count_data('2021-12-09')
