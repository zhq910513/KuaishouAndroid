import os
import re
import subprocess

from Logs.loggerDefine import loggerDefine

_dir = os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")), "Logs/"))
logger = loggerDefine(_dir, "push_files", "")


class Upload:
    # 通用shell
    @staticmethod
    def adb_shell(cmd):
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        return str(result.stdout.read())

    # 查询设备
    def search_devices(self):
        cmd = "adb devices"
        devices = [msg for msg in re.findall(r'\\n(.*?)\\r', self.adb_shell(cmd), re.S) if msg]
        if not devices:
            logger.warning('*** 请连接手机，并给手机root权限 ***')
        logger.info('--- 已连接 {} 台手机 ---'.format(len(devices)))
        return devices

    # 上传frida
    def upload_frida(self, device):
        udid = str(device).split(r'\t')[0]

        # frida
        cmd = r"adb -s {} push D:\Projects\kuaishou_android\software\frida-server64 /data/local/tmp".format(udid)
        result = self.adb_shell(cmd)
        if "1 file pushed" in result:
            logger.info('--- 手机 {} frida上传成功 ---'.format(udid))
            return True
        else:
            logger.warning('手机 {} frida上传失败'.format(udid))
            return False

    # 上传app
    def upload_app(self, device):
        udid = str(device).split(r'\t')[0]

        # app
        cmd = r"adb -s {} push D:\Projects\kuaishou_android\software\ks_6.5.0.apk /storage/emulated/0/Download".format(
            udid)
        result = self.adb_shell(cmd)
        if "1 file pushed" in result:
            logger.info('--- 手机 {} app上传成功 ---'.format(udid))
            return True
        else:
            logger.warning('手机 {} app上传失败'.format(udid))
            return False

    # 上传qpython
    def upload_qpython(self, device):
        udid = str(device).split(r'\t')[0]

        # app
        cmd = r"adb -s {} push D:\Projects\kuaishou_android\software\qpython_3s.apk /storage/emulated/0/Download".format(
            udid)
        result = self.adb_shell(cmd)
        if "1 file pushed" in result:
            logger.info('--- 手机 {} qpython上传成功 ---'.format(udid))
            return True
        else:
            logger.warning('手机 {} qpython上传失败'.format(udid))
            return False

    def run(self):
        # 检查在线手机
        devices = self.search_devices()
        if not devices: return

        for device in devices:
            self.upload_frida(device)
            #
            # self.upload_app(device)
            #
            # self.upload_qpython(device)


if __name__ == '__main__':
    up = Upload()
    up.run()
