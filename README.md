# 免登录下载微博图片(Python2移植版)

批量下载微博图片
移植自Java项目 [yAnXImIN/weiboPicDownloader](https://github.com/yAnXImIN/weiboPicDownloader)
~~骗star~~

## 更新日志

2017/12/24
- 接口变更
- 优化代码

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

## 下载

### 开箱即用
转到 [Release](https://github.com/nondanee/weiboPicDownloader/releases) 下载，使用PyInstaller打包

### 克隆源码
```
git clone https://github.com/nondanee/weiboPicDownloader.git && cd weiboPicDownloader
pip install futures
python weiboPicDownloader.py
```

## 运行
![show](show/screenshot.png)

*运行报错? 很有可能是接口又改了, 来提issue我会及时跟进*
