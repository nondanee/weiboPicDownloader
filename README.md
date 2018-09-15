# weiboPicDownloader

(not real) weibo user album batch download tool (CLI)

build user album by picking all photos from original weibos in user's post feed

compatible with both Python2 and Python3

for more weibo free login APIs, turn to [wiki](https://github.com/nondanee/weiboPicDownloader/wiki)

[中文 README](README-CN.md)


## References

[yAnXImIN/weiboPicDownloader](https://github.com/yAnXImIN/weiboPicDownloader)  

[ningshu/weiboPicDownloader](https://github.com/ningshu/weiboPicDownloader) 

## Overview

![screenshot](show/screenshot.png)

## Dependencies

```
$ pip(pip3) install requests
$ pip(pip3) install colorama #only windows version under 10.0.14393 required
$ pip install futures #only python2 environment required
```

## Usage

```
$ python weiboPicDownloader.py -h
usage: weiboPicDownloader [-h] [-u user] [-us users [users ...]] [-f file]
                          [-d directory] [-s size] [-r retry] [-c cookie] [-v]
                          [-o]

optional arguments:
  -h, --help            show this help message and exit
  -u user               specify a weibo user's nickname or id
  -us users [users ...]
                        specify weibo users' nickname or id
  -f file               import user list from file
  -d directory          set picture saving path
  -s size               set size of thread pool
  -r retry              set maximum number of retries
  -c cookie             set cookie if needed
  -v                    download videos together
  -o                    overwrite existing files
```

Required argument (choose one)

- `-u user` user (nickname or ID)
- `-us users` multiple users (nickname or ID, separated by space)
- `-f file` user list file (nickname or ID, separated by linefeed)

Optional arguments

- `-d directory` media saving path (default value: ./weiboPic)
- `-s size` thread pool size (default value: 20)
- `-r retry` max retries (default value: 2)
- `-c cookie` login status (only need the value of a certain key named `SUB`)
- `-v` download miaopai videos at the same time
- `-o` overwrite existing files (skipping if exists for default)

✳How to get the value of `SUB` from browser (Chrome for example)

1. jump to https://m.weibo.cn and log in
2. inspect > Application > Cookies > https://m.weibo.cn
3. double click the `SUB` line and copy its value
4. paste it into terminal and run like  `-c <value>`