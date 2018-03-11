# 免登录下载微博图片

批量下载微博图片(CLI)  ~~骗star~~  

根源自Java项目 [yAnXImIN/weiboPicDownloader](https://github.com/yAnXImIN/weiboPicDownloader)  

也从另一移植项目学习了好多 [ningshu/weiboPicDownloader](https://github.com/ningshu/weiboPicDownloader) 

非常感谢两位巨巨

## 描述

应 issue [#2](https://github.com/nondanee/weiboPicDownloader/issues/2) [#3](https://github.com/nondanee/weiboPicDownloader/issues/3) 的要求

支持真·批量下载

通过命令行设置参数

可以从文件导入

基本重写了代码

简化了大量的交互

于是新开一个分支

*暂不支持通过 id 下载*

## 使用

```
$ python weiboPicDownloader.py -h
usage: weiboPicDownloader [-h] [-n nickname] [-f file] [-d directory]
                          [-s size]

optional arguments:
  -h, --help    show this help message and exit
  -n nickname   target a weibo user's nickname
  -f file       use a nickname list from file
  -d directory  set picture saving path
  -s size       set size of thread pool
```

必需参数（二选一）

- `-n` 用户昵称
- `-f` 昵称列表文件（用换行分隔）

可选参数

- `-d` 图片保存路径（默认为工作路径下的weiboPic目录）
- `-s` 线程池大小（默认为20）



![screenshot](show/screenshot.png)

