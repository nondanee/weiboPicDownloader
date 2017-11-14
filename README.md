# 免登录下载微博图片(Python2移植版)

批量下载特定用户的高清大图  
移植自Java项目 [yAnXImIN/weiboPicDownloader](https://github.com/yAnXImIN/weiboPicDownloader)

## 更新日志

2017/11/14  
- 优化代码

2017/10/6  
- 启用flush显示进度
- 优化代码

2017/9/20  
- 增加多线程下载, 支持设置线程数, 可选择重试下载
- 设置默认选项, 添加更多交互, 完善输入检测
- 规范路径处理
- 优化代码

2017/9/17  
- 更正一处编码错误
- 优化代码  

## 运行

### 下载可执行文件
转到[Release](https://github.com/nondanee/weiboPicDownloader/releases)标签下载，使用PyInstaller打包

### 克隆源码
```
git clone https://github.com/nondanee/weiboPicDownloader.git && cd weiboPicDownloader
pip install futures
python weiboPicDownloader.py
```
*无法运行? 那很有可能是我写崩了, 来提issue或者自己动手丰衣足食*

## 使用

*多线程下载较占带宽, 可能影响正常上网*

1. 输入要保存图片的地址
2. 输入 3 当然你也可以输入1和2, 具体可以看[原作者(yAnXImIN)](https://github.com/yAnXImIN/)的[这篇博客](http://blog.yanximin.site/2017/09/05/weibo-userid-containerid/)
3. 输入用户昵称
4. 等待下载完成即可. So Easy!
![show](show/screenshot.png)

欢迎Fork, 或者PR  
要是能骗点Star最好了 :)  
