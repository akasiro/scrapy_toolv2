from requests.api import request
from urllib.parse import urljoin
import time,requests,json,os
from bs4 import BeautifulSoup
from config import *
class html_downloader():
    def __init__(self,china = True, world = False,
                 qiyeurl = QIYE_URL, xiciurl =XICI_URL):
        self.qiyeurl = qiyeurl
        self.xiciurl = xiciurl
        self.china = china
        self.world = world

        self.ip_pool = self.refresh_ip_pool()
        self.ip_buffer = set()
        self.ip_error = {}
        self.header_pool = self.refresh_header_pool()

        self.ip_pool_refresh_time = 0

    def refresh_ip_pool(self):
        if self.world:
            iplist = list(set(self.get_ip_list1() + self.get_ip_list2()))
        else:
            if self.china:
                iplist = list(set(self.get_ip_list1()+self.get_ip_list2()))
            else:
                iplist = self.get_ip_list1()
        pool = set(iplist)
        return pool

    # 使用qiye的IProxy程序获取ip池
    def get_ip_list1(self):
        if self.world:
            country = ''
        else:
            if self.china:
                country = '/?county=国内'
            else:
                country = '/?county=国外'
        try:
            r = requests.get(urljoin(self.qiyeurl, country))
            ip_list = ['{}:{}'.format(ipport[0], ipport[1]) for ipport in json.loads(r.text)]
        except:
            ip_list = []
        return ip_list

    #从西刺代理直接爬取获取ip池
    def get_ip_list2(self):
        try:
            web_data = requests.get(self.xiciurl, headers=DEFAULT_HEADER)
            soup = BeautifulSoup(web_data.text, 'html.parser')
            ips = soup.find_all('tr')
            ip_list = []
            for i in range(1, len(ips)):
                ip_info = ips[i]
                tds = ip_info.find_all('td')
                ip_list.append(tds[1].get_text() + ":" + tds[2].get_text())
        except:
            ip_list = []
        return ip_list

    def pick_ip(self):
        time_now = time.time()
        if len(self.ip_buffer) > 0:
            temp_ip = self.ip_buffer.pop()
        elif len(self.ip_pool - set(self.ip_error.keys())) == 0:
            # refresh error proxy 把一个小时前不能使用的ip过期
            self.ip_error = {k: v for k, v in self.ip_error.items() if v < time_now + 3600}
            #  防止进入无限循环
            try:
                self.ip_error.popitem()
            except:
                pass
            self.ip_pool = self.refresh_ip_pool()
            self.ip_pool_refresh_time +=1
            (time_now,temp_ip) = self.pick_ip()
        else:
            temp_ip= self.ip_pool.pop()
        return (time_now,temp_ip)
    def ip2proxies(self,ip):
        proxies = {'http': 'http://{}'.format(ip),'https': 'https://{}'.format(ip)}
        return proxies

    def refresh_header_pool(self):
        pool = [{'User-Agent':i} for i in USER_AGENT]
        return pool

    def pick_headers(self):
        if len(self.header_pool) == 0:
            self.header_pool = self.refresh_header_pool()
        tempheaders = self.header_pool.pop()
        return tempheaders

    def request_proxy(self,url,
                      method = 'get', timeout = (DEFAULT_MAX_CONNECT_TIME,DEFAULT_MAX_READ_TIME),
                      max_iter_time = DEFAULT_MAX_ITER_TIME,
                      data=None, cookies=None, files=None,
                    auth=None, allow_redirects=True,
                    hooks=None, stream=None, verify=None, cert=None, json=None):
        send_kwargs = {
            'url': url, 'method': method, 'data': data,
            'cookies': cookies, 'files': files, 'auth': auth, 'timeout': timeout,
            'allow_redirects': allow_redirects, 'hooks': hooks, 'stream': stream,
            'verify': verify, 'cert': cert, 'json': json}

        response = None
        iter_time = 0

        while iter_time < max_iter_time and self.ip_pool_refresh_time <2:
            (time_now, temp_ip) = self.pick_ip()
            send_kwargs['proxies'] = self.ip2proxies(temp_ip)
            send_kwargs['headers'] = self.pick_headers()
            try:
                response = request(**send_kwargs)
                if response.status_code == 200:
                    self.ip_buffer.add(temp_ip)
                    break
                else:
                    self.ip_error.update({temp_ip:time_now})
            except:
                self.ip_error.update({temp_ip:time_now})
        self.ip_pool_refresh_time  = 0
        return response

if __name__ == "__main__":
    t0 = time.time()
    print(t0)
    hd = html_downloader(world =True)
    print(len(hd.ip_pool))
    t1 = time.time()
    print(t1)
    print(t1-t0)
    url = ['https://www.indiegogo.com/projects/zero-reinventing-the-translator-for-everyone/coll',
           'https://www.indiegogo.com/projects/tyrian-gazette/hmco',
           'https://www.indiegogo.com/projects/jawbreakers-god-k1ng-graphic-novel/hmco',
           'https://www.indiegogo.com/projects/camect-world-s-smartest-most-private-camera-hub/hmco',
           'https://www.indiegogo.com/campaign_collections/staff-picks']
    t = time.time()
    for i in url:
        res = hd.request_proxy(i)
        print(res.status_code)
        t2 = time.time()
        print(t2)
        print('time:  {}'.format(t2-t))
        t = t2

