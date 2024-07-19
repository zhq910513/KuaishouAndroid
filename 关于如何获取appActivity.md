# 获取 appName 
    # 方法一
    cd C:\Program Files (x86)\Android\android-sdk\build-tools\29.0.3  (添加至环境变量也行)
        aapt dump badging C:\Users\hqzh02\Desktop\dy.apk
            package: name='com.ss.android.ugc.aweme'
            
    # 方法二
        # 解压 app
            # 右键 app 改为 xxx.rar
            # 通过 notepad++  打开 AndroidManifest.xml
    
    # 方法三
        # 反编译 apk
            # cd F:\Android\apktools  打开 CMD
            # 执行： apktool d xxx.apk
            # 用 jadx 查看文件  
                appPackage/packageName: package="com.ss.android.ugc.aweme"
                appActivity/Activity: targetActivity="com.ss.android.ugc.aweme.main.MainActivity"
    
    # 方法四  推荐
        # 使用 adb shell
            # 手机或者模拟器打开目标软件
            # CMD 运行 
            adb shell 
            dumpsys window | grep mCurrentFocus
                        
    
    
# DY 反爬机制
    # 未登录状态
        # 可直接搜索50次左右， 重装模拟器可以刷新， 直接更换手机类型或者网络无效
    
    # 登陆状态
        # 一个账号一天可搜索300~500次左右
        # 账号不变，刷新模拟器或更换手机型号无效
    
    # 重装模拟器
        # 可刷新不登陆状态， 可换账号登录