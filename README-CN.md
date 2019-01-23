# (免)登录下载微博图片 ![](https://img.shields.io/badge/python-2.7%7C3.4+-blue.svg)

批量下载微博用户图片 (CLI)

只对免登录接口感兴趣的话，直接看 [wiki](https://github.com/nondanee/weiboPicDownloader/wiki) 不用谢

## 致谢

根源自 Java 项目 [yAnXImIN/weiboPicDownloader](https://github.com/yAnXImIN/weiboPicDownloader)  

也从另一移植项目学到了好多 [ningshu/weiboPicDownloader](https://github.com/ningshu/weiboPicDownloader) 

非常感谢两位巨巨

## 预览

![](https://user-images.githubusercontent.com/26399680/51592598-fd48b980-1f2a-11e9-9687-4670e7dfcd83.png)

## 依赖

```
$ pip install requests
$ pip install colorama # 仅 Windows 10.0.14393 以下需要
$ pip install futures # 仅 Python2 需要
```

## 使用

```
$ python weiboPicDownloader.py -h
usage: weiboPicDownloader [-h] [-u user [user ...] | -f file [file ...]]
                          [-d directory] [-s size] [-r retry] [-c cookie] [-v]
                          [-o]

optional arguments:
  -h, --help          show this help message and exit
  -u user [user ...]  specify nickname or id of weibo users
  -f file [file ...]  import list of users from files
  -d directory        set picture saving path
  -s size             set size of thread pool
  -r retry            set maximum number of retries
  -c cookie           set cookie if needed
  -v                  download videos together
  -o                  overwrite existing files
```

必需参数（任选一）

- `-u user` 用户（昵称或 ID）
- `-f file` 用户列表文件（昵称或 ID，一个用户占一行）

可选参数

- `-d directory` 图片保存路径（默认为 ./weiboPic 目录）
- `-s size` 线程池大小（默认为 20）
- `-r retry` 最大重试次数（默认为 2）
- `-c cookie` 登录状态 (需要 cookie 中的 SUB 值)
- `-v` 同时下载秒拍视频
- `-o` 重新下载已保存的文件（默认跳过）

✳如何从浏览器中取得 `SUB` 的值（以 Chrome 举例）

1. 转到 https://m.weibo.cn 并登录
2. 右键检查 > Application > Cookies > https://m.weibo.cn
3. 双击 `SUB` 所在行并右键拷贝它的值
4. 将 `SUB` 的值粘贴到命令行窗口，以 `-c <value>` 的方式运行程序