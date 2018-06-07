# weiboPicDownloader

(not real) weibo user album batch download tool (CLI)

build user album by picking all photos from original weibos in user's post feed

for more weibo free login APIs, turn to [wiki](https://github.com/nondanee/weiboPicDownloader/wiki)


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
                          [-d directory] [-s size] [-r retry] [-v] [-o]

optional arguments:
  -h, --help            show this help message and exit
  -u user               target a weibo user's nickname or id
  -us users [users ...]
                        target weibo users' nickname or id
  -f file               import user list from file
  -d directory          set picture saving path
  -s size               set size of thread pool
  -r retry              set maximum number of retries
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
- `-v` download miaopai videos at the same time
- `-o` overwrite existing files (skipping if exists for default)