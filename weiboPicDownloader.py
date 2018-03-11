# -*- coding: utf-8 -*-

import sys, locale
import time, os, json
import concurrent.futures
import requests
import argparse


try:
    reload(sys)
    sys.setdefaultencoding('utf8') 
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
    "-n", metavar = "nickname", dest = "nickname",
    help = "target a weibo user's nickname",
    )
parser.add_argument(
    "-f", metavar = "file", dest = "file",
    help = "use a nickname list from file",
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


def requests_with_retry(url,max_retry=0):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}
    retry = 0
    while retry <= max_retry:
        try:
            return requests.request("GET",url,headers=headers,timeout=5,verify=False)
        except:
            retry = retry + 1


def read_from_file(file_path):
    nicknames = []
    try:
        file = open(file_path,"r")
        for line in file:
            nicknames.append(line.strip().decode(system_encodeing))
    except Exception as e:
        quit(str(e))
    return nicknames

def nickname_to_containerid(nickname):
    url = "https://m.weibo.com/n/{}".format(nickname)
    response = requests_with_retry(url=url)
    if url == response.url:
        return None
    else:
        return "107603" + response.url[-10:]

def get_urls(containerid):
    page = 1
    total = 0
    counter = 0
    urls = []
    while True:
        url = "https://m.weibo.cn/api/container/getIndex?count={}&page={}&containerid={}".format(25,page,containerid)
        response = requests_with_retry(url=url,max_retry=3)
        if response == None: continue
        json_data = json.loads(response.text)
        if json_data["ok"] != 1: 
            print_fit("finish analysis {}".format(progress(counter,total)),flush=True)
            break
        if total == 0: total = json_data["data"]["cardlistInfo"]["total"]
        cards = json_data["data"]["cards"]
        for card in cards:
            counter += 1
            print_fit("analysing weibos... {}".format(progress(counter,total)),flush=True)
            if "mblog" in card:
                if "pics" in card["mblog"]:
                    for pic in card["mblog"]["pics"]:
                        if "large" in pic:
                            urls.append(pic["large"]["url"])
        page = page + 1
        time.sleep(1)
        
    print_fit("\npractically get {} weibos, {} pictures".format(counter,len(urls)))
    return urls

def download_image(url,file_path):
    response = requests_with_retry(url=url,max_retry=0)
    if response == None:
        return False
    else:
        f = open(file_path,"wb")
        f.write(response.content)
        f.close()
        return True

# nicknames
if args.nickname:
    nicknames = [args.nickname.decode(system_encodeing)]
elif args.file:
    nicknames = read_from_file(args.file)
else:
    parser.print_help()
    quit("miss nickname argument, either -n or -f is acceptable")

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

for nickname in nicknames:
    containerid = nickname_to_containerid(nickname)
    if containerid == None:
        print_fit("unvalid account {}".format(nickname))
        continue
    print_fit("{} {}".format(nickname,containerid[6:]))
    urls = get_urls(containerid)
    if len(urls) == 0:
        continue
    user_album = os.path.join(saving_path,nickname)
    if not os.path.exists(user_album):
        make_dir(user_album)

    while True:
        total = len(urls)
        tasks = []
        for url in urls:
            file_name = url.split("/")[-1]
            file_path = os.path.join(user_album,file_name)
            tasks.append(pool.submit(download_image,url,file_path))

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
        elif not confirm("retry for failures?"):
            break

    print_fit("-"*30)

quit()