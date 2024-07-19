# -*- encoding: utf-8 -*-
'''
@File    :   kuaishou.py
@Time    :   2020年09月27日 15:08:24 星期天
@Author  :   ermao
@Version :   1.0
@Link    :   https://erma0.gitee.io
@Desc    :   快手相关接口
'''

print('start kuaishou.py')

import requests
import re
import time
import os
import json
# import hashlib
# from hashlib import md5
from io import BytesIO
from fontTools.ttLib import TTFont

headers = {
    'Upgrade-Insecure-Requests':
    '1',
    'User-Agent':
    'Mozilla/5.0 (Linux; U; Android 4.0; en-us; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
}
# 获取cookie用的作品链接
baseURL = 'https://v.kuaishou.com/4WAqVg'
baseURL_long = 'https://c.kuaishou.com/fw/photo/3x6ekfj54act2uc?fid=1420702805&cc=share_copylink&followRefer=151&shareMethod=TOKEN&docId=0&kpn=KUAISHOU&subBiz=PHOTO&photoId=3x6ekfj54act2uc&shareId=240777235900&shareToken=X3LVe5KWXlXzyEy_A&shareResourceType=PHOTO_OTHER&userId=3xqwdqazs5juny4&shareType=1&et=1_a%2F2000104399621290673_bs713%24s&shareMode=APP&groupName=&originShareId=240777235900&appType=21&shareObjectId=35593157332&shareUrlOpened=0&timestamp=1599377456260'
htmlRe = re.compile(r'pageData=([\s\S]*?)</script')
# end = '?fid=1420702805&cc=share_copylink&followRefer=151&shareMethod=TOKEN&docId=0&kpn=KUAISHOU&subBiz=PROFILE&shareId=239777105474&docABKey=share_textid_profile&shareToken=X-1jqzFTsHrXe1Bh_A&shareResourceType=PROFILE_OTHER&groupABKey=share_group_profile&shareMode=APP&groupName=&originShareId=239777105474&expTag=null&appType=21&shareObjectId=1250106104&shareUrlOpened=0'
end2 = '?fid=1173628593&cc=share_copylink&shareMethod=TOKEN&docId=0&kpn=KUAISHOU&subBiz=PHOTO&photoId=3xyavifvduu96bs&shareId=170921058277&shareToken=X975rh0HoqjF191_A&shareResourceType=PHOTO_OTHER&userId=3x8jnxjsvqepnj4&shareType=1&et=1_i%2F0_unknown0&groupName=&appType=21&shareObjectId=28211741097&shareUrlOpened=0&timestamp=1588991909301'


def setdid_env(did='none'):
    import fc2
    client = fc2.Client(endpoint='', accessKeyID='', accessKeySecret='')
    client.update_function('', '', environmentVariables={'did': did})


def get_timestamp(long=13):
    if long == 10:
        timestamp = str(int(time.time()))
    else:  # long == 13:
        timestamp = str(int(time.time() * 1000))
    return timestamp


def setdid_header():
    t = time.perf_counter()
    did = os.environ.get('did')
    # did = 'web_30b697e2338c49d8a98692eefc5c38f2'
    if did and len(did) > 10:
        print(did)
        headers['Cookie'] = 'did=' + did
    else:
        refresh_did()
    t = time.perf_counter() - t
    # print("@@@@@@@@",headers['Cookie'], t)
    return t


# 通过访问作品获取可以访问用户主页的did
# 下午还可以用，晚上就不行了。。。
# 同一ip访问次数多了就不行了，看来还是要用refresh_did了
def new_did_userinfo():
    url = baseURL_long
    setdid_header()
    try:
        requests.get(url, headers=headers)
        return {'success': '成功取到did'}
    except Exception:
        return {'error': '未取得可有效did'}


def user_info(id):
    res = new_did_userinfo()  # 取用户信息之前必须刷新did
    if res.get('error'):
        return res
    u = {'kuaiId': id}
    url = 'https://c.kuaishou.com/fw/user/' + id  # + end
    try:
        res = requests.get(url, headers=headers).text
        user_json = htmlRe.search(res).group(1)
        userinfo = json.loads(user_json)
        u['userId'] = userinfo['userIdInfo']['userId']
        u['userName'] = userinfo['share']['title'][4:-12]
        u['desc'] = userinfo['share']['desc']
        u['imgUrl'] = userinfo['share']['imgUrl']
        u['count'] = userinfo['pageTabs'][0]['count']
        fontCdnUrl = userinfo['obfuseData']['fontCdnUrl']
        # print(res)
        # u['fontCdnUrl'] = userinfo['obfuseData']['fontCdnUrl']

        # 映射表 网页字符：明文
        key_map = {}
        # 动态获取字体
        font_content = requests.get(fontCdnUrl).content
        font = TTFont(BytesIO(font_content))  # 从内存加载
        code = font.getGlyphOrder()[1:]  # 固定顺序的字符编码列表（去除第一个无效字符）
        nums = [  # 固定顺序明文列表
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', 'w', 'k',
            'm', '+'
        ]
        temp = dict(zip(code, nums))  # 临时映射（固定顺序），字符编码uni****：明文
        res = font.getBestCmap()  # 获取关键映射，网页字符转码：字符编码uni****
        for k, v in res.items():
            # 网页字符去除前缀，再从16进制转10进制，就得到k，这里逆向写，即k转16进制后拼接前缀
            kk = '&#' + str(hex(k))[1:]
            # 从临时映射中根据字符编码uni****取出明文
            key_map[kk] = temp[v]
        # print(len(key_map), key_map)
        re_html_code = re.compile(r'&#x[\da-f]{4}')
        # for word in ['fan', 'follow', 'photo', 'collect']:  # 遍历需要用到的字体加密的参数
        for word in ['fan', 'follow']:  # 遍历需要用到的字体加密的参数
            # ('photo', 'collect'这两个重复了，可以不要)
            text = userinfo['obfuseData'][word]
            words = re_html_code.findall(text)
            u[word] = ''.join(key_map[i] for i in words)
        return u
    except Exception:
        setdid_env()  # os无法修改环境变量，只能通过SDK实现
        # os.environ.pop('did')  # 解析失败的话就把did删了，下次重新获取
        return {'error': '出错！'}


def user_info_url(url):
    try:
        if '/profile/' in url:
            id = re.findall(r'/profile/(\w*?)\??', url)[0]
        elif 'fw/user/' in url:
            id = re.findall(r'fw/user/(\w*?)\??', url)[0]
        else:
            # https://v.kuaishou.com/6vPcKW
            r = requests.head(url, headers=headers, allow_redirects=False)
            # redirectURL = r.headers['Location'].split('?')
            # global end
            # end = '?' + redirectURL[1]
            # id = redirectURL[0].split('/fw/user/')[1]
            id = re.findall(r'fw/user/(\w*?)\?', r.headers['Location'])[0]
    except Exception:
        return {'error': '出错了！'}
    return user_info(id)


# 这个did取不到用户信息，需要取回来之后new_did_userinfo
def refresh_did(did=''):
    headers.pop('Cookie', None)
    url = baseURL
    if len(did) < 10:
        try:
            r = requests.head(url, headers=headers, allow_redirects=False)
            did = r.cookies.get('did')
        except Exception:
            res = {'error': '未取得可有效did'}
    if did and len(did) > 10:
        url = 'https://wlog.gifshow.com/rest/kd/log/web/action?_json=1'
        data = {
            "events": [{
                "client_timestamp": int(get_timestamp(13)),
                "bus": "share",
                "page_tag": "验证码",
                "url": "https://c.kuaishou.com/fw/photo/3xrkjbikwdh5chm",
                "did": did,
                "uid": 0,
                "sid": "",
                "vid": 1,
                "sys": "android",
                "v_size": "360x640",
                "n_size": "720x1280",
                "action_type": "pv",
                "from": ""
            }]
        }

        try:
            headers['Content-Type'] = 'text/plain;charset=UTF-8'
            headers['Accept'] = '*/*'
            # headers['Referer'] = url_long
            headers[
                'Referer'] = "https://c.kuaishou.com/fw/photo/3xrkjbikwdh5chm"

            r = requests.post(
                url,
                json=data,
                # ///---+++ 这里卡了几个小时，没注意到问题，
                # 因为用的data=data，同时又设置了Content-Type不是json，导致参数被格式化
                headers=headers,
                allow_redirects=False)
            headers['Cookie'] = 'did=' + did
            headers.pop('Content-Type')
            headers.pop('Accept')
            headers.pop('Referer')
            # os.environ['did'] = did
            # 本地调试不设置
            setdid_env(did)  # os无法修改环境变量，只能通过SDK实现
            time.sleep(2)  # 提交之后需要等待2秒，cookie才生效
            # print('环境变量是否设置成功：{}'.format(did == os.environ.get('did')))
            res = {'did': did}
        except Exception:
            res = {'error': 'did刷新失败！'}
    else:
        res = {'error': '未取得可有效did'}
    return res


# 用另一个可以直接取到内容,不用先取id再用id取内容
def parse_by_url(url):
    did = ''
    try:
        if 'photoId=' in url:
            id = re.findall(r'photoId=(\w*?)&?', url)[0]
        elif '/fw/photo/' in url:
            id = re.findall(r'/photo/(\w*?)\??', url)[0]
        else:
            # https://v.kuaishou.com/4WAqVg
            r = requests.head(url, headers=headers, allow_redirects=False)
            redirectURL = r.headers['Location'].split('?')
            global end2
            end2 = '?' + redirectURL[1]
            id = redirectURL[0].split('/fw/photo/')[1]
            # id = re.findall(r'/photo/(\w*?)\?', r.headers['Location'])[0]
            did = r.cookies.get('did')
    except Exception:
        return {'error': '出错了！'}
    return parse_by_id(id, did)


# 不用did，直接可以访问
# IP限制，访问多了就不行了，还是要refresh_did
def parse_by_url2(url):
    v = {}
    try:
        res = requests.get(url, headers=headers).text
        user_json = htmlRe.search(res).group(1)
        res_json = json.loads(user_json)
        v['photoId'] = res_json['photoId']
        v['video'] = res_json['video']
        v['user'] = res_json['user']
        return v
    except Exception:
        return {'error': '解析出错！'}


def parse_by_id(id, did=''):
    setdid_header()
    v = {}
    # 如果不加后面的end2会使did立即失效
    url = 'https://c.kuaishou.com/fw/photo/' + id + end2
    try:
        r = requests.get(url, headers=headers).text
        m = htmlRe.search(r)
        if m:
            user_json = m.group(1)
        else:  # 环境变量的did失效了，re匹配不到
            res = refresh_did(did)  # 刷新did
            if res.get('error'):
                return res  # 刷新did失败
            else:  # 刷新did完成，重新访问，re匹配
                r = requests.get(url, headers=headers).text
                user_json = htmlRe.search(r).group(1)  # 这里再出现解析出错的话，就是刷新功能失效
        res_json = json.loads(user_json)
        # print(res_json)
        v['photoId'] = res_json['photoId']
        v['video'] = res_json['video']
        v['user'] = res_json['user']
        return v
    except Exception:
        return {'error': '解析出错！'}


if __name__ == "__main__":
    # refresh_did()
    # r = parse_by_url('https://v.kuaishou.com/4WAqVg')
    # r = parse_by_url2('https://v.kuaishou.com/4WAqVg')
    # r = parse_by_id('3xrkjbikwdh5chm')
    for i in range(100):
        # r = parse_by_id2('3xrkjbikwdh5chm')
        r = user_info('1286274291')
        # r = user_info_url('https://v.kuaishou.com/6vPcKW')
        # print(os.environ.get('did'))
        print("###########",r)
    # print(os.environ.get('did'))