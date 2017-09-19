# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 01:38:07 2017

@author: nondanee
"""

import os
import sys
import locale
import time
import json
import re
import ssl
import urllib2
import concurrent.futures

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
    
def open_and_read(url,max_retry):
    retry = 0
    request = urllib2.Request(url = url, headers = {'User-Agent' : USER_AGENT})
    while True:
        try:            
            response = urllib2.urlopen(request,timeout = 5)
            return response.read()
        except Exception as e:
            retry = retry + 1
            if retry > max_retry:
                return

def get_img_urls(containerid,page):
    url = "https://m.weibo.cn/api/container/getIndex?count=25&page=%s&containerid=%s"%(page,containerid)
    data = open_and_read(url = url,max_retry = 3)
    if data == None:
        return []

    jsondata = json.loads(data)
    if len(jsondata["cards"]) == 0:
        return

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
    if urlback == url:
        return
    else:
        uid = urlback[27:]
        return "107603" + uid
        
def get_containerid(account_type):
    input_tips = ["请输入用户ID:","请输入用户名:","请输入用户昵称:"]
    error_info = ["用户ID无效\n","无法找到该用户\n","无法找到该用户\n"]
    functions = [uid_to_containerid,username_to_containerid,nickname_to_containerid]
    input_string = raw_input_fit(input_tips[account_type])
    input_string = re.sub("\s","",input_string)
    if input_string == "":
        return
    containerid = functions[account_type](input_string)
    if containerid == None:
        print_fit(error_info[account_type])
        return
    else:
        return containerid 

def download_and_save(url,user_path,index,amount):
    file_type = url[-3:]
    file_name = str(index + 1).zfill(len(str(amount))) + "." + file_type   
    file_path = os.path.join(user_path,file_name) 

    data = open_and_read(url = url,max_retry = 3)
    if data == None:
        return index,0
    else:
        f = open(file_path,"wb")
        f.write(data)
        f.close()
        return index,1
        
        
def get_task(urls,miss):
    task = []
    for index in miss:
        task.append(urls[index])
    return task

def main():
    while True:
        print_fit("请输入图片要保存的地址:")
        home_path = os.path.realpath(raw_input_fit())
        print_fit("选择的目录为 %s"%home_path.encode("utf-8")) 
        if os.path.exists(home_path) == True:
            break
        confirm = raw_input_fit("该目录不存在, 是否创建?(Y/n):")
        confirm = re.sub("\s","",confirm)
        if confirm == "y" or confirm == "Y" or confirm == "":
            try:
                os.makedirs(home_path)
            except:
                print_fit("目录创建失败, 请尝试手动创建, 或者更改目录\n")
            else:
                print_fit("目录已创建")
                break
        else:
            print_fit("请手动创建, 或者更改目录\n")
                
    while True:
        print_fit("请输入要下载的账号类型:\n[1]用户ID\n[2]用户名\n[3]用户昵称(建议)")
        choice = raw_input_fit("(1/2/3):")
        try:
            choice = int(choice)
        except:
            choice = 3
        if choice not in [1,2,3]:
            choice = 3
        containerid = get_containerid(choice - 1)
        if containerid != None:
            break
    
    user_path = os.path.join(home_path,containerid[6:]) 
    if os.path.exists(user_path) == False:
        os.mkdir(user_path)
            
    i = 1
    urls = []
    while True:
        print_fit("分析微博中: %d"%i)
        more = get_img_urls(containerid,i)
        if more != None:
            urls.extend(more)
            i = i + 1
            time.sleep(1)
        else:
            break
    
    print_fit("分析完毕")
    amount = len(urls)
    print_fit("图片数量: %d"%amount)
    
    max_workers = raw_input_fit("设置最大下载线程数(1-20):")
    try:
        max_workers = int(max_workers)
    except:
        max_workers = 20
    if max_workers > 20:
        max_workers = 20
    elif max_workers < 1:
        max_workers = 1
    print_fit("最大下载线程数为 %d"%max_workers)
            
#    pool = concurrent.futures.ThreadPoolExecutor(max_workers = max_workers)
#    futures = []
#    for x in xrange(0,amount):
#        futures.append(pool.submit(download_and_save, urls[x],user_path,x,amount))
#    concurrent.futures.wait(futures)

    miss = range(0,amount)  
    while True:
        task = get_task(urls,miss)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers = max_workers)
        results = executor.map(download_and_save,task,[user_path]*len(task),miss,[amount]*len(task))
        
        miss = []
        for result in results:
            if result[1] == 1:
                print_fit("已下载图片 %d/%d"%(result[0] + 1,amount))
            elif result[1] == 0:
                miss.append(result[0])
        
        print_fit("下载成功 %d, 下载失败 %d"%(amount-len(miss),len(miss)))
        
        if len(miss) != 0:
            confirm = raw_input_fit("是否继续尝试?(Y/n):")
            confirm = re.sub("\s","",confirm)
            if confirm == "y" or confirm == "Y" or confirm == "":
                continue
            else:
                break
        else:
            break
            
    for index in miss:
        print_fit("图片 %s 下载失败 %s"%(index + 1,urls[index].encode("utf-8")))
    
    print_fit("下载结束, 路径是 %s"%user_path.encode("utf-8"))
    sys.stdin.read()
    exit()
    
if __name__ == "__main__":
    main()
