import urllib
import requests
from bs4 import BeautifulSoup
import redis


r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class SpiderProxy(object):
    """从http://www.xicidaili.com/wt 取代理ip"""
    headers = {
        "Host": "www.xicidaili.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "http://www.xicidaili.com/nn/1",
    }

    def __init__(self, session_url):
        self.req = requests.session()
        self.req.get(session_url)

    def get_pagesource(self, url):
        '''取得html pagesource'''
        html = self.req.get(url, headers=self.headers)
        return html.content

    def get_all_proxy(self, url):
        ''' 取得所有1-n页上的代理IP'''
        data = []
        for i in range(6, 9):
            html = self.get_pagesource(url + str(1))
            soup = BeautifulSoup(html, "lxml")
            table = soup.find('table', id="ip_list")
            for row in table.findAll("tr"):
                cells = row.findAll("td")
                tmp = []
                for item in cells:
                    tmp.append(item.find(text=True))
                try:
                    tmp2 = tmp[1:2][0]
                    tmp3 = tmp[2:3][0]
                    tmp4 = tmp[5:6][0]
                    data.append({tmp4: tmp2 + ":" + tmp3})
                except Exception as e:
                    pass
        print(data)
        return data


class IsActivePorxyIP(object):
    """类组合用gevent 异步并发验证 代理IP是不是可以用 """

    def __init__(self, session_url):
        self.proxy = SpiderProxy(session_url)
        self.is_active_proxy_ip = []

    def probe_proxy_ip(self, proxy_ip):
        """代理检测"""
        proxy = urllib.request.ProxyHandler(proxy_ip)
        opener = urllib.request.build_opener(proxy)
        urllib.request.install_opener(opener)
        try:
            html = urllib.request.urlopen('http://baidu.com')
            # print html.read()
            if html:
                self.is_active_proxy_ip.append(proxy_ip)
                print("proxy+1")
                return True
            else:
                return False
        except Exception as e:
            return False


if __name__ == '__main__':
    session_url = 'http://www.xicidaili.com/nn/1'
    url = 'http://www.xicidaili.com/nn/'

    p_isactive = IsActivePorxyIP(session_url)
    proxy_ip_lst = p_isactive.proxy.get_all_proxy(url)
    print(len(proxy_ip_lst))
    i = 1
    for proxy_ip in proxy_ip_lst:
        p_isactive.probe_proxy_ip(proxy_ip)
        (key, value), = proxy_ip.items()
        r.set(i, value)
        i = i +1