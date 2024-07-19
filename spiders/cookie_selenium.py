import os
import random
import math

import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
import time

from spiders.captchaTujianApi import TujianApi

chrome_js = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), r'G:/资料/Selenium 环境/selenium_demo/stealth.min.js')))

class cookie:
    def __init__(self, kw):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        # 无界面浏览器
        options.add_argument('--headless')
        # 禁止图片加载
        # prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}
        # options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Chrome(options=options)
        with open(chrome_js) as f:
            js = f.read()
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js
        })

        self.driver.get('https://www.kuaishou.com/search/author?searchKey={}'.format(kw))
        time.sleep(2)
        self.driver.refresh()

    def check_status(self):
        try:
            time.sleep(15)
            return self.get_cookie()
        except Exception as error:
            print(error)
        time.sleep(1500)

    def get_cookie(self):
        cookie_dict = dict()
        loginCookie = []
        for cookie in self.driver.get_cookies():
            cookie_dict[cookie['name']] = cookie['value']
        for item in cookie_dict.items():
            loginCookie.append('{}={}'.format(item[0], item[1]))
        cookie = ';'.join(loginCookie)
        self.driver.close()
        return cookie

    def handle_rotation_verifucate(self):
        if 'Drag to right to fill the puzzle' in str(self.driver.page_source):
            while True:
                time.sleep(random.uniform(3, 5))
                try:
                    rotation_image_src = self.driver.find_element_by_xpath('//img[@class="bg-img"]').get_attribute('src')
                    print(rotation_image_src)
                    rotation_image = requests.get(rotation_image_src).content
                    with open('./rotation_image.png', 'wb')as f:
                        f.write(rotation_image)
                except Exception as error:
                    print(error)
                    self.driver.refresh()
                    time.sleep(4)
                    continue
                try:
                    distance_api = int(TujianApi(imgPath=r"./rotation_image.png").base64_api())
                except Exception as error:
                    print(error)
                    continue
                print('distance api:', distance_api)
                if distance_api > 0:
                    distance = abs(220 * distance_api / 360)
                elif distance_api < 0:
                    distance = abs(abs(220 * (360 + distance_api) / 360))
                else:
                    continue
                print('current distance:', distance)
                partHead = math.ceil(distance * 0.8)
                partTail = distance - partHead
                slider_element = self.driver.find_element_by_xpath('//div[@class="vcode-spin-button"]/p')
                ActionChains(self.driver).click_and_hold(on_element=slider_element).perform()
                ActionChains(self.driver).move_by_offset(xoffset=partHead, yoffset=0).perform()
                tracks = self.get_tracks(partTail)
                for s in tracks:
                    ActionChains(self.driver).move_by_offset(xoffset=s, yoffset=0).perform()
                time.sleep(0.3)
                ActionChains(self.driver).release().perform()
                time.sleep(random.uniform(3, 5))
                if str(self.driver.page_source).find("百度安全验证") >= 0:
                    print('again')
                    continue
                else:
                    print('success')
                    return True

    def get_tracks(self, distance):
        v = 0
        t = 0.3
        tracks = []
        current = 0
        mid = distance * 4 / 5
        while current < distance:
            if current < mid:
                a = 2
            else:
                a = -3
            v0 = v
            s = v0 * t + 0.5 * a * (t ** 2)
            current += s
            tracks.append(round(s))
            v = v0 + a * t
        return tracks
