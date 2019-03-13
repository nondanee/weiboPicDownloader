# -*- coding: utf-8 -*-

from functools import reduce
import sys, locale, platform
import time, os, json, re
import concurrent.futures
import requests
import argparse

try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except:
    pass

is_python2 = sys.version[0] == '2'
system_encoding = sys.stdin.encoding or locale.getpreferredencoding(True)

if platform.system() == 'Windows':
    if platform.version() >= '10.0.14393':
        os.system('')
    else:
        import colorama
        colorama.init()

try:
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
except:
    pass

parser = argparse.ArgumentParser(
    prog = 'weiboPicDownloader'
)
group = parser.add_mutually_exclusive_group(required = True)
group.add_argument(
    '-u', metavar = 'user', dest = 'users', nargs = '+',
    help = 'specify nickname or id of weibo users'
)
group.add_argument(
    '-f', metavar = 'file', dest = 'files', nargs = '+',
    help = 'import list of users from files'
)
parser.add_argument(
    '-d', metavar = 'directory', dest = 'directory',
    help = 'set picture saving path'
)
parser.add_argument(
    '-s', metavar = 'size', dest = 'size',
    default = 20, type = int,
    help = 'set size of thread pool'
)
parser.add_argument(
    '-r', metavar = 'retry', dest = 'retry',
    default = 2, type = int,
    help = 'set maximum number of retries'
)
parser.add_argument(
    '-i', metavar = 'interval', dest = 'interval',
    default = 1, type = float,
    help = 'set interval for feed requests'
)
parser.add_argument(
    '-c', metavar = 'cookie', dest = 'cookie',
    help = 'set cookie if needed'
)
parser.add_argument(
    '-v', dest = 'video', action = 'store_true',
    help = 'download videos together'
)
parser.add_argument(
    '-o', dest = 'overwrite', action = 'store_true',
    help = 'overwrite existing files'
)

def nargs_fit(parser, args):
    flags = parser._option_string_actions
    short_flags = [flag for flag in flags.keys() if len(flag) == 2]
    long_flags = [flag for flag in flags.keys() if len(flag) > 2]
    short_flags_with_nargs = set([flag[1] for flag in short_flags if flags[flag].nargs])
    short_flags_without_args = set([flag[1] for flag in short_flags if flags[flag].nargs == 0])
    validate = lambda part : (re.match(r'-[^-]', part) and (set(part[1:-1]).issubset(short_flags_without_args) and '-' + part[-1] in short_flags)) or (part.startswith('--') and part in long_flags)

    greedy = False
    for index, arg in enumerate(args):
        if arg.startswith('-'):
            valid = validate(arg)
            if valid and arg[-1] in short_flags_with_nargs:
                greedy = True
            elif valid:
                greedy = False
            elif greedy:
                args[index] += ' '
    return args

def print_fit(string, pin = False):
    if is_python2:
        string = string.encode(system_encoding)
    if pin == True:
        sys.stdout.write('\r\033[K')
        sys.stdout.write(string)
        sys.stdout.flush()
    else:
        sys.stdout.write(string + '\n')

def input_fit(string = ''):
    if is_python2:
        return raw_input(string.encode(system_encoding)).decode(system_encoding)
    else:
        return input(string)

def merge(*dicts):
    result = {}
    for dictionary in dicts: result.update(dictionary)
    return result

def quit(string = ''):
    print_fit(string)
    exit()

def make_dir(path):
    try:
        os.makedirs(path)
    except Exception as e:
        quit(str(e))

def confirm(message):
    while True:
        answer = input_fit('{} [Y/n] '.format(message)).strip()
        if answer == 'y' or answer == 'Y':
            return True
        elif answer == 'n' or answer == 'N':
            return False
        print_fit('unexpected answer')

def progress(part, whole, percent = False):
    if percent:
        return '{}/{}({}%)'.format(part, whole, int(float(part) / whole * 100))
    else:
        return '{}/{}'.format(part, whole)

def request_fit(method, url, max_retry = 0, cookie = None, stream = False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.80 Mobile Safari/537.36',
        'Cookie': cookie
    }
    return requests.request(method, url, headers = headers, timeout = 5, stream = stream, verify = False)

def read_from_file(path):
    try:
        with open(path, 'r') as f:
            return [line.strip().decode(system_encoding) if is_python2 else line.strip() for line in f]
    except Exception as e:
        quit(str(e))

def nickname_to_uid(nickname):
    url = 'https://m.weibo.cn/n/{}'.format(nickname)
    response = request_fit('GET', url, cookie = token)
    if re.search(r'/u/\d{10}$', response.url):
        return response.url[-10:]
    else:
        return

def uid_to_nickname(uid):
    url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}'.format(uid)
    response = request_fit('GET', url, cookie = token)
    try:
        return json.loads(response.text)['data']['userInfo']['screen_name']
    except:
        return

def get_resources(uid, video, interval):
    page = 1
    size = 25
    amount = 0
    total = 0
    empty = 0
    aware = 1
    resources = []

    while empty < aware:
        try:
            url = 'https://m.weibo.cn/api/container/getIndex?count={}&page={}&containerid=107603{}'.format(size, page, uid)
            response = request_fit('GET', url, cookie = token)
            assert response.status_code != 418
            json_data = json.loads(response.text)
        except AssertionError:
            print_fit('punished by anti-scraping mechanism (#{})'.format(page), pin = True)
            empty = aware
        except Exception:
            pass
        else:
            empty = empty + 1 if json_data['ok'] == 0 else 0
            if total == 0 and 'cardlistInfo' in json_data['data']: total = json_data['data']['cardlistInfo']['total']
            cards = json_data['data']['cards']
            for card in cards:
                if 'mblog' in card:
                    mark = {'mid': card['mblog']['mid'], 'bid': card['mblog']['bid'], 'text': card['mblog']['text']}
                    amount += 1
                    if 'pics' in card['mblog']:
                        for index, pic in enumerate(card['mblog']['pics'], 1):
                            if 'large' in pic:
                                resources.append(merge({'url': pic['large']['url'], 'index': index, 'type': 'photo'}, mark))
                    elif video and 'page_info' in card['mblog'] :
                        if 'media_info' in card['mblog']['page_info']:
                            media_info = card['mblog']['page_info']['media_info']
                            streams = [media_info[key] for key in ['mp4_720p_mp4', 'mp4_hd_url', 'mp4_sd_url', 'stream_url'] if key in media_info and media_info[key]]
                            if streams:
                                resources.append(merge({'url': streams.pop(0), 'type': 'video'}, mark))
            print_fit('{} {}(#{})'.format('analysing weibos...' if empty < aware else 'finish analysis', progress(amount, total), page), pin = True)
            page += 1
        finally:
            time.sleep(interval)

    print_fit('\npractically get {} weibos, {} {}'.format(amount, len(resources), 'resources' if video else 'pictures'))
    return resources

def format_name(item):
    url = item['url']
    name = re.sub(r'^\S+/', '', url)
    name = re.sub(r'\?\S+$', '', name)
    return name

def download(url, path, overwrite):
    if os.path.exists(path) and not overwrite: return True
    try:
        response = request_fit('GET', url, stream = True)
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size = 512):
                if chunk:
                    f.write(chunk)
    except Exception:
        if os.path.exists(path): os.remove(path)
        return False
    else:
        return True


args = parser.parse_args(nargs_fit(parser, sys.argv[1:]))

if args.users:
    users = [user.decode(system_encoding) for user in args.users] if is_python2 else args.users
elif args.files:
    users = [read_from_file(path.strip()) for path in args.files]
    users = reduce(lambda x, y : x + y, users)
users = [user.strip() for user in users]

if args.directory:
    base = args.directory
    if os.path.exists(base):
        if not os.path.isdir(base): quit('saving path is not a directory')
    elif confirm('directory "{}" doesn\'t exist, help to create?'.format(base)):
        make_dir(base)
    else:
        quit('do it youself :)')
else:
    base = os.path.join(os.path.dirname(__file__), 'weiboPic')
    if not os.path.exists(base): make_dir(base)

token = 'SUB={}'.format(args.cookie) if args.cookie else None
pool = concurrent.futures.ThreadPoolExecutor(max_workers = args.size)

for number, user in enumerate(users, 1):
    
    print_fit('{}/{} {}'.format(number, len(users), time.ctime()))
    
    if re.search(r'^\d{10}$', user):
        nickname = uid_to_nickname(user)
        uid = user
    else:
        nickname = user
        uid = nickname_to_uid(user)

    if not nickname or not uid:
        print_fit('invalid account {}'.format(user))
        print_fit('-' * 30)
        continue

    print_fit('{} {}'.format(nickname, uid))
    
    try:
        resources = get_resources(uid, args.video, args.interval)
    except KeyboardInterrupt:
        quit()

    album = os.path.join(base, nickname)
    if resources and not os.path.exists(album): make_dir(album)

    retry = 0
    while resources and retry <= args.retry:
        
        if retry > 0: print_fit('automatic retry {}'.format(retry))

        total = len(resources)
        tasks = []
        done = 0
        failed = {}
        cancel = False

        for resource in resources:
            path = os.path.join(album, format_name(resource))
            tasks.append(pool.submit(download, resource['url'], path, args.overwrite))

        while done != total:
            try:
                done = 0
                for index, task in enumerate(tasks):
                    if task.done() == True:
                        done += 1
                        if task.cancelled(): continue
                        elif task.result() == False: failed[index] = ''
                    elif cancel:
                        if not task.cancelled(): task.cancel()
                time.sleep(0.5)
            except KeyboardInterrupt:
                cancel = True
            finally:
                if not cancel:
                    print_fit('{} {}'.format(
                        'downloading...' if done != total else 'all tasks done',
                        progress(done, total, True)
                    ), pin = True)
                else:
                    print_fit('waiting for cancellation... ({})'.format(total - done), pin = True) 

        if cancel: quit()
        print_fit('\nsuccess {}, failure {}, total {}'.format(total - len(failed), len(failed), total))

        resources = [resources[index] for index in failed]
        retry += 1

    for resource in resources: print_fit('{} failed'.format(resource['url']))
    print_fit('-' * 30)

quit('bye bye')