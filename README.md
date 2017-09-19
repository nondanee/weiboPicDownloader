# 免登录下载微博图片(Python2移植版)

批量下载特定用户的高清大图  
移植自Java项目 [yAnXImIN/weiboPicDownloader](https://github.com/yAnXImIN/weiboPicDownloader)

## 更新日志

2017/9/20  
- 增加多线程下载, 支持设置线程数, 可选择重试下载
- 设置默认选项, 添加更多交互, 完善输入检测
- 规范路径处理
- 优化代码

* 如果卡在"已下载图片 XX/XX"的位置, 可以注意下网速和下载文件夹, 除当前资源下载线程等待外, 其它线程应该正常工作, 请耐心等待 *  
* 下载期间可能严重影响正常上网 *  

2017/9/17  
- 更正一处编码错误
- 优化代码  

## 用法

- ### 没有Python2的Windows环境
下载 [weiboPicDownloader.exe](https://raw.githubusercontent.com/nondanee/weiboPicDownloader/master/dist/weiboPicDownloader.exe), 双击运行

*注: 由py2exe打包而成, setup.py 为其打包配置*  

- ### 有Python2环境的Windows/macOS/Linux环境
控制台执行 `python weiboPicDownloader.py` 

*注: 增加多线程下载后需pip安装futures模块*  

>无法运行? 那很有可能是我写崩了, 来提issue或者自己动手丰衣足食  

![show](show/screenshot.png)
1. 输入要保存图片的地址
2. 输入 3 当然你也可以输入1和2, 具体可以看[原作者(yAnXImIN)](https://github.com/yAnXImIN/)的[这篇博客](http://blog.yanximin.site/2017/09/05/weibo-userid-containerid/)
3. 输入用户昵称
4. 等待下载完成即可. So Easy!


欢迎Fork, 或者PR  
要是能骗点Star最好了 :)  
