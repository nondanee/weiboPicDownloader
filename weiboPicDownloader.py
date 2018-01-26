# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 01:38:07 2017

@author: nondanee
"""

import os, sys, locale
import json, re, time
import concurrent.futures
import requests

try:
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
except:
    pass

try:
    reload(sys)
    sys.setdefaultencoding('utf8') 
except:
    pass

try:
    input = raw_input
except NameError:
    pass

IS_PYTHON2 = sys.version[0] == "2"
SYSTEM_ENCODE = sys.stdin.encoding or locale.getpreferredencoding(True)
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
PIC_AMOUNT = 0
SAVE_PATH = ""

def print_fit(string,flush=False):
    if IS_PYTHON2:
        string = string.encode(SYSTEM_ENCODE)
    if flush == True:
        sys.stdout.write("\r"+string)
        sys.stdout.flush()
    else:
        sys.stdout.write(string+"\n")


def raw_input_fit(string=""):
    if IS_PYTHON2:
        return input(string.encode(SYSTEM_ENCODE)).decode(SYSTEM_ENCODE)
    else:
        return input(string)

def requests_retry(url,max_retry=0):
    retry = 0
    while True:
        if retry > max_retry: 
            return
        try:
            response = requests.request("GET",url,headers={"User-Agent":USER_AGENT},timeout=5,verify=False)
            return response
        except:
            retry = retry + 1

def get_img_urls(containerid):
    page = 1
    amount = 0
    total = 0
    urls = []
    while True:
        url = "https://m.weibo.cn/api/container/getIndex?count={}&page={}&containerid={}".format(25,page,containerid)
        response = requests_retry(url=url,max_retry=3)
        if response == None: continue
        json_data = json.loads(response.text)
        if json_data["ok"] != 1: break
        total = json_data["data"]["cardlistInfo"]["total"]
        cards = json_data["data"]["cards"]
        for card in cards:
            amount = amount + 1
            print_fit("分析微博中... {}".format(amount),flush=True)
            if "mblog" in card:
                if "pics" in card["mblog"]:
                    for pic in card["mblog"]["pics"]:
                        if "large" in pic:
                            urls.append(pic["large"]["url"])
        page = page + 1
        time.sleep(1)
        
    print_fit("\n分析完毕, 微博总数 {}, 实际获得 {}".format(total,amount))
    return urls

def uid_to_containerid(uid):
    if re.search(r'^\d{10}$',uid):
        return "107603" + uid       

def nickname_to_containerid(nickname):
    url = "https://m.weibo.com/n/{}".format(nickname)
    response = requests_retry(url=url)    
    uid_check = re.search(r'(\d{16})',response.url)
    if uid_check:
        return "107603" + uid_check.group(1)[-10:]

def get_containerid(account_type):
    input_tips = ["请输入用户ID: ","请输入用户昵称: "]
    error_info = ["用户ID无效\n","无法找到该用户\n"]
    functions = [uid_to_containerid,nickname_to_containerid]
    input_string = raw_input_fit(input_tips[account_type]).strip()
    if input_string == "":
        return
    containerid = functions[account_type](input_string)
    if containerid == None:
        print_fit(error_info[account_type])
        return
    else:
        return containerid 

def download_and_save(url,index):
    file_type = url[-3:]
    file_name = str(index + 1).zfill(len(str(PIC_AMOUNT))) + "." + file_type   
    file_path = os.path.join(SAVE_PATH,file_name) 

    response = requests_retry(url=url)
    if response == None:
        return index,0
    else:
        f = open(file_path,"wb")
        f.write(response.content)
        f.close()
        return index,1
        
def get_task(urls,miss):
    task = []
    for index in miss:
        task.append(urls[index])
    return task

def main():
    while True:
        home_path = os.path.realpath(raw_input_fit("请输入图片存储位置: "))
        print_fit("选择的目录为 {}".format(home_path))
        if os.path.exists(home_path) == True:
            break
        confirm = raw_input_fit("该目录不存在, 是否创建?(Y/n): ").strip()
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
        print_fit("请输入要下载的账号类型:\n[1]用户ID [2]用户昵称")
        choice = raw_input_fit("(1/2): ")
        try:
            choice = int(choice)
        except:
            choice = 2
        if choice not in [1,2]:
            choice = 2
        containerid = get_containerid(choice - 1)
        if containerid != None:
            break  

    global SAVE_PATH
    SAVE_PATH = os.path.join(home_path,containerid[6:]) 
    if os.path.exists(SAVE_PATH) == False:
        os.mkdir(SAVE_PATH)

    urls = get_img_urls(containerid)
    
    global PIC_AMOUNT
    PIC_AMOUNT = len(urls)
    print_fit("图片数量 {}".format(PIC_AMOUNT))
    
    max_workers = raw_input_fit("设置下载线程数(1-20): ")
    try:
        max_workers = int(max_workers)
    except:
        max_workers = 20
    if max_workers > 20:
        max_workers = 20
    elif max_workers < 1:
        max_workers = 1

    miss = range(0,PIC_AMOUNT)  
    while True:
        task = get_task(urls,miss)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers = max_workers)
        results = executor.map(download_and_save,task,miss)
        
        miss = []
        for result in results:
            index = result[0]
            status = result[1]
            if status == 0: miss.append(index)
            print_fit("已处理 {dealt}/{amount}, 下载失败 {failed}/{amount}".format(dealt=index+1,failed=len(miss),amount=PIC_AMOUNT),flush=True)
                
        if len(miss) != 0:
            confirm = raw_input_fit("是否继续尝试?(Y/n): ").strip()
            if confirm == "y" or confirm == "Y" or confirm == "":
                continue
            else:
                break
        else:
            print_fit("全部完成")
            break
            
    for index in miss:
        print_fit("图片 {} 下载失败 {}".format(index + 1,urls[index]))
    
    print_fit("下载结束, 路径是 {}".format(SAVE_PATH))
    sys.stdin.read()
    exit()
    
if __name__ == "__main__":
    main()
