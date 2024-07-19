import time
from pymongo import MongoClient

client = MongoClient('mongodb://readWrite:readWrite123456@120.48.21.244:27017/kuaishou')
phone_coll = client['kuaishou']['phones']

while True:
    for i in phone_coll.find({'status': 1, 'list_type': 1, 'profile_type': 2}):
        # print(i)
        if (int(time.time()) - i.get('update_time', 0)) > 3600:
            print('--- {}号手机被启用 ---'.format(i['phone']))
            phone_coll.update_one({'_id': i['_id']}, {'$set': {'profile_type': 1, 'update_time': int(time.time())}}, upsert=True)

    time.sleep(60)
