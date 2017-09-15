# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 01:38:07 2017

@author: nondanee
"""

import os
import locale
import urllib2
import json
import re
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
MAX_DOWNLOAD_SIZE = 40 * 1024 * 1024

def chineseDisplay(str):
    return str.decode("utf-8").encode(locale.getpreferredencoding(True))

def getImgURL(containerid,page):    
    url = "https://m.weibo.cn/api/container/getIndex?count=25&page=%s&containerid=%s"%(page,containerid)
    requset = urllib2.Request(url = url, headers = {'User-Agent' : USER_AGENT})
    response = urllib2.urlopen(requset)
    jsondata = json.loads(response.read())
    
    if len(jsondata["cards"]) == 0:
        return
        
    urls = []

#    if len(jsondata["cards"]) != 25:
#        print len(jsondata["cards"])

    for card in jsondata["cards"]:
        if "mblog" in card:
            if "pics" in card["mblog"]:
                for pic in card["mblog"]["pics"]:
                    if "large" in pic:
                        urls.append(pic["large"]["url"])
                
    return urls

 
def nicknameToContainerId(nickname):
    url = "https://m.weibo.com/n/"+nickname.encode("utf-8")
    requset = urllib2.Request(url = url, headers = {'User-Agent' : USER_AGENT})
    try:
        response = urllib2.urlopen(requset)
        urlback = response.geturl()
        response.close()
    except urllib2.HTTPError:
        return
    if urlback == url:
        return
    else:
        uid = urlback[27:]
        return "107603" + uid
        
def uidToContainerId(uid):
    return "107603" + uid
    
def usernameToContainerId(name):
    url = "https://weibo.cn/"+name
    requset = urllib2.Request(url = url, headers = {'User-Agent' : USER_AGENT})
    try:
        response = urllib2.urlopen(requset)
    except urllib2.HTTPError:
        return
    htmlback = response.read()
    response.close()
    find = re.search(r'<a href="/(\d{10})/info">',htmlback)
    if find == None:
        return
    else:
        uid = find.group(1)
        return "107603" + uid
    
def download(url):
    reconnect = 0
    while reconnect < 10:
        try:
            request = urllib2.Request(url = url,headers = {'User-Agent':USER_AGENT})
            response = urllib2.urlopen(request,timeout = 5)
            content_length = int(response.headers["Content-Length"])
            if content_length >= MAX_DOWNLOAD_SIZE:
                response.close()
                return
            else:
                resource = response.read()
                return resource
        except Exception as e:
            print(chineseDisplay("出现错误 %s")%e)
            reconnect = reconnect + 1
            print(chineseDisplay("重试 %d次"%reconnect))
        else:
            break
        
if __name__ == "__main__":
    print(chineseDisplay("请输入图片要保存的地址:"))
    IMG_LOCATION = raw_input().decode(locale.getpreferredencoding(True))
    if os.path.exists(IMG_LOCATION) == False:
        while True:
            confirm = raw_input(chineseDisplay("该目录不存在, 是否创建?(Y/N):"))
            confirm = re.sub("\s","",confirm)
            if confirm == "y" or confirm == "Y":
                try:
                    os.makedirs(IMG_LOCATION)
                    break
                except:
                    print(chineseDisplay("目录创建失败, 请手工创建"))
                    os.system("pause")
                    exit()
            elif confirm == "n" or confirm == "N":
                os.system("pause")
                exit()
                
    while True:
        print(chineseDisplay("请输入要下载的账号类型:"))
        print(chineseDisplay("[1]用户ID"))
        print(chineseDisplay("[2]用户名"))
        print(chineseDisplay("[3]用户昵称(建议)"))
        choice = raw_input(chineseDisplay("(1/2/3):")).decode(locale.getpreferredencoding(True))
        choice = re.sub("\s","",choice)
        if choice == "1":
            uid = raw_input(chineseDisplay("请输入用户ID:")).decode(locale.getpreferredencoding(True))
            if re.search(r'^\d{10}$',uid)==None:
                print(chineseDisplay("用户ID无效\n"))
            else:
                containerId = uidToContainerId(uid)
                break
        elif choice == "2":
            name = raw_input(chineseDisplay("请输入用户名:")).decode(locale.getpreferredencoding(True))
            containerId = usernameToContainerId(name)
            if containerId == None:
                print(chineseDisplay("无法找到该用户\n"))
            else:
                break
        elif choice == "3":
            nickname = raw_input(chineseDisplay("请输入用户昵称:")).decode(locale.getpreferredencoding(True))
            containerId = nicknameToContainerId(nickname)
            if containerId == None:
                print(chineseDisplay("无法找到该用户\n"))
            else:
                break
            
    i = 1
    downloadlist = []
    while True:
        print(chineseDisplay("分析微博中: %d"%i))
        listback = getImgURL(containerId,i)
        if listback != None:
            downloadlist.extend(listback)
            i = i + 1
            time.sleep(1)
        else:
            break
    print(chineseDisplay("分析完毕"))
    amount = len(downloadlist)
    print(chineseDisplay("图片数量: %d"%amount))
    
    ARCHIVE_LOCATION = IMG_LOCATION + "/" + containerId[6:] + "/"
    if os.path.exists(ARCHIVE_LOCATION) == False:
        os.mkdir(ARCHIVE_LOCATION)
        
    for x in range(1,amount+1):
        print(chineseDisplay("下载图片: %d"%x))
        downloadUrl = downloadlist[x-1]
        data = download(downloadUrl)
        filename = str(x).zfill(len(str(amount)))
        filetype = downloadUrl[-3:]
        if data == None:
            print(chineseDisplay("图片 %s 下载失败"%downloadUrl))
            continue
        f = open(ARCHIVE_LOCATION + filename + "." + filetype,'wb')
        f.write(data)
        f.close()
        
    print(chineseDisplay("图片下载完成, 路径是 %s"%ARCHIVE_LOCATION.encode("utf-8")))
    os.system("pause")
        