from appium import webdriver
import time
import random
import logging

from spiders.apm import Appium


class ControlKSApp:
    def __init__(self, phone_uuid, port):
        self.bluev = []
        # 配置启动 手机 driver
        self.desired_caps = {
            "platformName": "Android",
            "deviceName": "Redmi 5 Plus",
            "platformVersion": "7.1.0",
            "udid": phone_uuid,
            "appPackage": "com.smile.gifmaker",
            "appActivity": "com.yxcorp.gifshow.activity.SearchActivity",
            "unicodeKeyboard": True,
            "resetKeyboard": True,
            "noReset": True
        }

        # 启动手机
        self.driver = webdriver.Remote('http://127.0.0.1:{}/wd/hub'.format(port), self.desired_caps)
        print('启动 driver 成功！')

        self.close_s()

    def close_s(self):
        try:
            self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/aa2').click()
        except:
            pass

        try:
            self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/aa5').click()
        except:
            pass

    # 获得机器屏幕大小x,y
    def getSize(self):
        x = self.driver.get_window_size()['width']
        y = self.driver.get_window_size()['height']
        return (x, y)

    # 屏幕向上滑动
    def swipeUp(self, skiptime):
        l = self.getSize()
        x1 = int(l[0] * 0.5)  # x坐标
        y1 = int(l[1] * 0.75)  # 起始y坐标
        y2 = int(l[1] * 0.25)  # 终点y坐标
        self.driver.swipe(x1, y1, x1, y2, skiptime)

    # 手机界面操作
    def search_words(self):
        self.main_page_search()

        if not self.search_send_keys('服装'):
            self.driver.keyevent(4)
            return

        if not self.click_search_page():
            self.driver.keyevent(4)
            return

        if not self.click_usr_tab():
            self.driver.keyevent(4)
            return
        time.sleep(1)

        self.driver.keyevent(4)

    def main_page_search(self):
        try:
            # 点击搜索页搜索框
            self.driver.find_element_by_id("com.smile.gifmaker:id/inside_editor_hint").click()
            time.sleep(3)
        except:
            try:
                self.driver.tap([(281,103), (798,186)], 500)
            except:
                pass

    def search_send_keys(self, words):
        try:
            # 搜索框输入关键字
            # self.driver.find_element_by_id("com.smile.gifmaker:id/editor").clear()
            # time.sleep(1)

            self.driver.find_element_by_id("com.smile.gifmaker:id/editor").send_keys(str(words))
            time.sleep(3)
            return True
        except:
            print('搜索框输入关键字  错误')
            return False

    def click_search_page(self):
        try:
            # 点击搜索词推荐结果
            self.driver.find_elements_by_id('com.smile.gifmaker:id/item_root')[0].click()
            time.sleep(3)
            return True
        except:
            print('点击搜索词推荐结果  错误')
            return False

    def click_usr_tab(self):
        # 切换至用户
        try:
            self.driver.find_element_by_id('com.smile.gifmaker:id/tabs').find_elements_by_class_name('android.widget.TextView')[1].click()
            time.sleep(3)
            return True
        except:
            try:
                xpath = '/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.HorizontalScrollView/android.widget.LinearLayout/android.widget.TextView[2]'
                self.driver.find_element_by_xpath(xpath)
                time.sleep(3)
                return True
            except:
                print('切换至用户栏  错误')
                return False

    def click_search_result(self):
        try:
            # 点击具体用户
            self.driver.find_elements_by_id('com.smile.gifmaker:id/follower_info_layout')[0].click()
            time.sleep(5)

            self.driver.keyevent(4)
            return True
        except:
            return False

    # 判断错误机制
    def app_error(self):
        # 关闭 app
        self.driver.close_app()
        time.sleep(3)


if __name__ == '__main__':
    infos = [('8054c29e0804', 4725), ('11059b009805', 4725)]
    while 1:
        for info in infos:
            try:
                # 关闭 appium
                Appium().close_appium(info[1])
                time.sleep(5)

                # 开启appium
                Appium().start_appium(info[1], info[0])
                time.sleep(random.uniform(3, 5))

                time.sleep(5)
                xhs_search = ControlKSApp(info[0], info[1])
                time.sleep(10)

                xhs_search.search_words()
            except Exception as error:
                    logging.warning(error)

            time.sleep(random.uniform(180, 300))

        time.sleep(random.uniform(1200, 1800))

