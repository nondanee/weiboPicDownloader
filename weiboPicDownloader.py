# -*- coding: utf-8 -*-

import sys, locale
import time, os, json, re
import concurrent.futures
import requests
import argparse


try:
    reload(sys)
    sys.setdefaultencoding("utf8")
except:
    pass

is_python2 = sys.version[0] == "2"
system_encodeing = sys.stdin.encoding or locale.getpreferredencoding(True)


try:
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
except:
    pass

try:
    input = raw_input
except NameError:
    pass


parser = argparse.ArgumentParser(
    prog = "weiboPicDownloader",
    )
parser.add_argument(
    "-u", metavar = "user", dest = "user",
    help = "target a weibo user's nickname or id",
    )
parser.add_argument(
    "-us", metavar = "users", dest = "users", nargs = "+",
    help = "target weibo users' nickname or id",
    )
parser.add_argument(
    "-f", metavar = "file", dest = "file",
    help = "export user list from file",
    )
parser.add_argument(
    "-d", metavar = "directory", dest = "directory",
    help = "set picture saving path",
    )
parser.add_argument(
    "-s", metavar = "size", dest = "size",
    # choices = range(1,21),
    default = 20, type = int,
    help = "set size of thread pool",
    )
parser.add_argument(
    "-v", dest = "video", action="store_true",
    help = "download videos together",
    )
parser.add_argument(
    "-o", dest = "overwrite", action="store_true",
    help = "overwrite existing files",
    )
args = parser.parse_args()


def print_fit(string,flush=False):
    if is_python2:
        string = string.encode(system_encodeing)
    if flush == True:
        sys.stdout.write("\r"+format("","<40"))
        sys.stdout.flush()
        sys.stdout.write("\r"+string)
        sys.stdout.flush()
    else:
        sys.stdout.write(string+"\n")

def input_fit(string=""):
    if is_python2:
        return input(string.encode(system_encodeing)).decode(system_encodeing)
    else:
        return input(string)

def quit(string="bye bye"):
    print_fit(string)
    exit()

def make_dir(path):
    try:
        os.makedirs(path)
    except Exception as e:
        quit(str(e))

def confirm(message):
    while True:
        answer = input_fit("{} [Y/n] ".format(message)).strip()
        if answer == "y" or answer == "Y":
            return True
        elif answer == "n" or answer == "N":
            return False
        print_fit("unexpected answer")

def progress(done,total,percent=False):
    if percent:
        return "{}/{}({}%)".format(done,total,int(float(done)/total*100))
    else:
        return "{}/{}".format(done,total)

def requests_with_retry(url,max_retry=0,stream=False):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}
    retry = 0
    while retry <= max_retry:
        try:
            return requests.request("GET",url,headers=headers,timeout=5,stream=stream,verify=False)
        except:
            retry = retry + 1


def read_from_file(file_path):
    nicknames = []
    try:
        file = open(file_path,"r")
        for line in file:
            if is_python2:
                nicknames.append(line.strip().decode(system_encodeing))
            else:
                nicknames.append(line.strip())
        file.close()
    except Exception as e:
        quit(str(e))
    return nicknames

def nickname_to_uid(nickname):
    url = "https://m.weibo.cn/n/{}".format(nickname)
    response = requests_with_retry(url=url)
    if re.search(r'/u/\d{10}$',response.url):
        return response.url[-10:]
    else:
        return None

def uid_to_nickname(uid):
    url = "https://m.weibo.cn/api/container/getIndex?type=uid&value={}".format(uid)
    response = requests_with_retry(url=url)
    try:
        json_data = json.loads(response.text)
        return json_data["data"]["userInfo"]["screen_name"]
    except:
        return None

def get_urls(uid,video=False):
    page = 1
    total = 0
    counter = 0
    urls = []
    while True:
        url = "https://m.weibo.cn/api/container/getIndex?count={}&page={}&containerid=107603{}".format(25,page,uid)
        response = requests_with_retry(url=url,max_retry=3)
        if response == None: continue
        json_data = json.loads(response.text)
        if json_data["ok"] != 1: 
            print_fit("finish analysis {}".format(progress(counter,total)),flush=True)
            break
        if total == 0: total = json_data["data"]["cardlistInfo"]["total"]
        cards = json_data["data"]["cards"]
        for card in cards:
            if "mblog" in card:
                counter += 1
                print_fit("analysing weibos... {}".format(progress(counter,total)),flush=True)
                if "pics" in card["mblog"]:
                    for pic in card["mblog"]["pics"]:
                        if "large" in pic:
                            urls.append(pic["large"]["url"])
                elif video and "page_info" in card["mblog"] :
                    if "media_info" in card["mblog"]["page_info"]:
                        urls.append(card["mblog"]["page_info"]["media_info"]["stream_url"])
        page = page + 1
        time.sleep(1)
    
    if video:
        print_fit("\npractically get {} weibos, {} medias".format(counter,len(urls)))
    else:
        print_fit("\npractically get {} weibos, {} pictures".format(counter,len(urls)))
    return urls

def download(url,file_path,overwrite):
    if os.path.exists(file_path) and not overwrite:
        return True
    response = requests_with_retry(url=url,max_retry=0,stream=True)
    if response == None:
        return False
    else:
        file = open(file_path,"wb")
        try:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    file.write(chunk)
        except:
            file.close()
            os.remove(file_path)
            return False
        else:
            file.close()
            return True

# users
if args.user:
    if is_python2:
        users = [args.user.decode(system_encodeing)]
    else:
        users = [args.user]
elif args.users:
    if is_python2:
        users = [user.decode(system_encodeing) for user in args.users]
    else:
        users = args.users
elif args.file:
    users = read_from_file(args.file)
else:
    parser.print_help()
    quit("miss user argument, either -n or -f is acceptable")

# saving_path
if args.directory:
    saving_path = args.directory
    if os.path.exists(saving_path):
        if not os.path.isdir(saving_path):
            quit("saving path is not a directory")
    elif confirm("directory \"{}\" doesn't exist, help me create?".format(saving_path)):
        make_dir(saving_path)
    else:
        quit("do it youself :)")
else:
    saving_path = os.path.join(os.path.dirname(__file__),"weiboPic")
    if not os.path.exists(saving_path):
        make_dir(saving_path)

pool = concurrent.futures.ThreadPoolExecutor(max_workers=args.size)

for i,user in enumerate(users,1):
    print_fit("{}/{} {}".format(i,len(users),time.ctime()))
    if re.search(r"^\d{10}$",user):
        nickname = uid_to_nickname(user)
        uid = user
    else:
        nickname = user
        uid = nickname_to_uid(user)
    if nickname == None or uid == None:
        print_fit("unvalid account {}".format(user))
        print_fit("-"*30)
        continue
    print_fit("{} {}".format(nickname,uid))
    urls = get_urls(uid,args.video)
    if len(urls) == 0:
        print_fit("-"*30)
        continue
    user_album = os.path.join(saving_path,nickname)
    if not os.path.exists(user_album):
        make_dir(user_album)

    counter = 0
    while True:
        total = len(urls)
        tasks = []
        for url in urls:
            file_name = re.sub(r"^\S+/","",url)
            file_name = re.sub(r"\?\S+$","",file_name)
            file_path = os.path.join(user_album,file_name)
            tasks.append(pool.submit(download,url,file_path,args.overwrite))

        done = 0
        failed = {}
        while True:
            for index,task in enumerate(tasks):
                if task.done() == True:
                    done += 1
                    if task.result() == False:
                        if index not in failed:
                            failed[index] = ""
            
            time.sleep(0.5)
            print_fit("downloading... {}".format(progress(done,total,True)),flush=True)
            
            if done == total:
                print_fit("all tasks done {}".format(progress(done,total,True)),flush=True)
                break
            else:
                done = 0
 
        print_fit("\nsuccessfull {}, failed {}, total {}".format(total-len(failed),len(failed),total))

        urls = [urls[index] for index in failed]

        if len(urls) == 0:
            break
        elif counter < 2:
            counter += 1
            print_fit("automatic retry {}".format(counter))
        else:
            break

    for url in urls:
        print_fit("{} failed".format(url))

    print_fit("-"*30)

quit()