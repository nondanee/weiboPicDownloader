# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 01:38:07 2017

@author: nondanee
"""

import os
import sys
import locale
import urllib2
import json
import re
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"

def print_fit(string):
    if type(string) is unicode:
        print(string).encode(sys.stdin.encoding or locale.getpreferredencoding(True))
    elif type(string) is str:
        print(string.decode("utf-8")).encode(sys.stdin.encoding or locale.getpreferredencoding(True))
        
def raw_input_fit(string = ""):
    if type(string) is unicode:
        prompt = string.encode(sys.stdin.encoding or locale.getpreferredencoding(True))
    elif type(string) is str:
        prompt = string.decode("utf-8").encode(sys.stdin.encoding or locale.getpreferredencoding(True))
        
    return raw_input(prompt).decode(sys.stdin.encoding or locale.getpreferredencoding(True))

def get_img_urls(containerid,page):    
    url = "https://m.weibo.cn/api/container/getIndex?count=25&page=%s&containerid=%s"%(page,containerid)
    requset = urllib2.Request(url = url, headers = {'User-Agent' : USER_AGENT})
    response = urllib2.urlopen(requset)
    jsondata = json.loads(response.read())
    
    if len(jsondata["cards"]) == 0:
        return
    else: 
        urls = []
        for card in jsondata["cards"]:
            if "mblog" in card:
                if "pics" in card["mblog"]:
                    for pic in card["mblog"]["pics"]:
                        if "large" in pic:
                            urls.append(pic["large"]["url"])
        return urls

def uid_to_containerid(uid):
    if re.search(r'^\d{10}$',uid) == None:
        return
    else:
        return "107603" + uid
       
def username_to_containerid(name):
    url = "https://weibo.cn/" + name.encode("utf-8")
    requset = urllib2.Request(url = url, headers = {'User-Agent' : USER_AGENT})
    try:
        response = urllib2.urlopen(requset)
    except urllib2.HTTPError:
        return
    htmlback = response.read()
    print htmlback
    response.close()
    find = re.search(r'<a href="/(\d{10})/info">',htmlback)
    if find == None:
        return
    else:
        uid = find.group(1)
        return "107603" + uid
        
def nickname_to_containerid(nickname):
    url = "https://m.weibo.com/n/" + nickname.encode("utf-8")
    requset = urllib2.Request(url = url, headers = {'User-Agent' : USER_AGENT})
    try:
        response = urllib2.urlopen(requset)  
    except urllib2.HTTPError:
        return
    urlback = response.geturl()
    response.close()
    if urlback == url:
        return
    else:
        uid = urlback[27:]
        return "107603" + uid
    
def download(url):
    reconnect = 0
    while True:
        try:
            request = urllib2.Request(url = url,headers = {'User-Agent':USER_AGENT})
            response = urllib2.urlopen(request,timeout = 5)
            return response.read()
        except Exception as e:
            print_fit("出现错误 %s"%e)
            reconnect = reconnect + 1
            if reconnect > 10:
                return
            print_fit("重试 %d次"%reconnect)
        
if __name__ == "__main__":
    
    while True:
        print_fit("请输入图片要保存的地址:")
        home_path = raw_input_fit()
        if os.path.exists(home_path) == True:
            break
        confirm = raw_input_fit("该目录不存在, 是否创建?(Y/N):")
        confirm = re.sub("\s","",confirm)
        if confirm == "y" or confirm == "Y":
            try:
                os.makedirs(home_path)
            except:
                print_fit("目录创建失败, 请尝试手动创建, 或者更改目录\n")
            else:
                break
        elif confirm == "n" or confirm == "N":
            print_fit("请手动创建, 或者更改目录\n")
                
    while True:
        print_fit("请输入要下载的账号类型:\n[1]用户ID\n[2]用户名\n[3]用户昵称(建议)")
        choice = raw_input_fit("(1/2/3):")
        choice = re.sub("\s","",choice)
        if choice == "1":
            uid = raw_input_fit("请输入用户ID:")
            containerid = uid_to_containerid(uid)
            if containerid == None:
                print_fit("用户ID无效\n")
            else:
                break
        elif choice == "2":
            name = raw_input_fit("请输入用户名:")
            containerid = username_to_containerid(name)
            if containerid == None:
                print_fit("无法找到该用户\n")
            else:
                break
        elif choice == "3":
            nickname = raw_input_fit("请输入用户昵称:")
            containerid = nickname_to_containerid(nickname)
            if containerid == None:
                print_fit("无法找到该用户\n")
            else:
                break
            
    i = 1
    downloadlist = []
    while True:
        print_fit("分析微博中: %d"%i)
        listback = get_img_urls(containerid,i)
        if listback != None:
            downloadlist.extend(listback)
            i = i + 1
            time.sleep(1)
        else:
            break
    
    print_fit("分析完毕")
    amount = len(downloadlist)
    print_fit("图片数量: %d"%amount)
    
    user_path = home_path + "/" + containerid[6:] + "/"
    if os.path.exists(user_path) == False:
        os.mkdir(user_path)
        
    for x in xrange(1,amount+1):
        print_fit("下载图片: %d"%x)
        downloadUrl = downloadlist[x-1]
        data = download(downloadUrl)
        filename = str(x).zfill(len(str(amount)))
        filetype = downloadUrl[-3:]
        if data == None:
            print_fit("图片 %s 下载失败"%downloadUrl.encode("utf-8"))
            continue
        f = open(user_path + filename + "." + filetype,'wb')
        f.write(data)
        f.close()
        
    print_fit("图片下载完成, 路径是 %s"%user_path.encode("utf-8"))
    sys.stdin.read()
    exit()
