#coding=utf-8
import requests

#请求地址
targetUrl = "https://www.baidu.com"

#代理服务器
proxyHost = "59.33.136.188"
proxyPort = "4246"

proxies = {
    "http"  : "http://%(host)s:%(port)s" % {
        "host" : proxyHost,
        "port" : proxyPort
    },
    "https"  : "http://%(host)s:%(port)s" % {
        "host" : proxyHost,
        "port" : proxyPort
    }
}

resp = requests.get(targetUrl, proxies=proxies)
print(resp.status_code)
print(resp.text)