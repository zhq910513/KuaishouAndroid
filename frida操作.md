# 手机中安装Frida服务端
    查看Android手机设备设置
    adb shell
    getprop ro.product.cpu.abi
    
    https://github.com/frida/frida/releases
        arm-v8a    https://github-releases.githubusercontent.com/9405122/93093215-fc1a-4a1e-a668-e66194cae08c?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20210825%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20210825T105843Z&X-Amz-Expires=300&X-Amz-Signature=6ba756af9c528f99d1843ed2091dc119c4c2645cccccaa630acc8098690b2a84&X-Amz-SignedHeaders=host&actor_id=0&key_id=0&repo_id=9405122&response-content-disposition=attachment%3B%20filename%3Dfrida-server-15.0.18-android-arm64.xz&response-content-type=application%2Foctet-stream
    
    # 进行adb端口转发
    adb forward tcp:27042 tcp:27042
    adb forward tcp:27043 tcp:27043
    
    # 进入解压文件路径
    adb push frida-server64 /data/local/tmp
    
    # 启动Frida
    adb shell
    su
    cd /data/local/tmp
    chmod 755 frida-server64
    ./frida-server64 &
    
    # 校验
    cmd执行   frida-ps -U
    
    获取系统api版本：adb shell getprop ro.build.version.sdk


# 问题
    1.如何确定手机与电脑frida都启动成功了？
    2.frida-ps -U 手机找不到启动的APP进程？           frida -U --no-pause -f "com.xxx.xxx"
    3.执行py文件  无法连接指定APP？



# 操作流程
    adb reboot

    adb kill-server
    adb start-server
    adb devices

    # 每次重新启动都要转发端口
    adb forward tcp:27042 tcp:27042
    adb forward tcp:27043 tcp:27043

    # 进入解压文件路径
    D:/Projects/kuaishou_android/software/frida-server64
    adb push D:/Projects/kuaishou_android/software/frida-server64 /data/local/tmp

    adb shell
    su
    cd /data/local/tmp
    chmod 755 frida-server64
    ./frida-server64 &

    # 检查链接状况
    cmd执行   frida-ps -U

    frida -U -f com.smile.gifmaker -l D:\Projects\kuaishou_android\ks_token.js --no-pause
    frida -U -f com.ss.android.ugc.aweme -l G:\PycharmProjects\douyin_android\spiders\dy_token.js --no-pause
    
    frida -U -f com.example.parameterstest -l D:\ks_token.js --no-pause


# mongo
// db.getCollection('author_list').find({}).count()
db.getCollection('author_list').find({'verified': true, 'status': null, 'contact_status': null}).count()
// db.getCollection('author_list').find({'verified': true, 'status': null, 'contact_status': 1, 'lanv_status': 1, 'timeStamp': {'$gt': 1640966399}}).count()
db.getCollection('author_list').find({'verified': true, 'status': null, 'contact_status': 1, 'lanv_status': 1, 'timeStamp': {'$lt': 1640966399}}).count()
// db.getCollection('author_list').find({'verified': true, 'status': 'no_used', 'contact_status': 1, 'lanv_status': 2}).count()


#  6.5 版快手封号分析
    注册受号段影响  171 无需认证    165 需要

    账号可用     手机网络可用                实际可用
    账号可用     iphone-WiFi可用            实际可用
    账号可用     PDCN-WiFi不可用            实际不可用
    账号可用     PDCN-WiFi代理不可用        实际不可用
    账号可用     PDCN-WiFi切换IP不可用      实际不可用
