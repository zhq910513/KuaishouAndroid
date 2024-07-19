import os,shutil
from pymongo import MongoClient


def move_file(before, after):
    if not os.path.isfile(before):
        print("%s not exist!" % before)
        return False
    else:
        file_path,file_name=os.path.split(after)    #分离文件名和路径
        if not os.path.exists(file_path):
            os.makedirs(file_path)                #创建路径
        shutil.move(before, after)          #移动文件
        print("move  {0} -->  {1}".format(before, after))
        return True


def match_sort_videos():
    client = MongoClient('mongodb://127.0.0.1:27017/douyin')
    coll = client['douyin']['video_info']

    for num, video_info in enumerate(coll.find({'video_status': 2}).sort('video.digg_count', -1).limit(1500), start=0):
        print(video_info)
        hash_key = video_info['hash_key']

        before_file = r'C:\Users\hqzh02\PycharmProjects\douyin_android\videos\{}.mp4'.format(hash_key)
        after_file = r'C:\Users\hqzh02\PycharmProjects\douyin_android\sort_videos\{}.mp4'.format(hash_key)

        try:
            if move_file(before_file, after_file):
                coll.update_one({'hash_key': hash_key}, {'$set': {'video_status': 3}}, upsert=True)
        except:
            pass
        # break


if __name__ == '__main__':
    match_sort_videos()
