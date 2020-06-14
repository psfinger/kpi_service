import random
import requests
import json
import threading
import time

#一连接多请求

#URL = 'http://portal.buaiti.com:3000/service'
URL = 'http://localhost:3000/service'
MAX_SLEEP_TIME = 1
WRITE_THREAD_NUM = 1
READ_THREAD_NUM = 1


class call_request:
    def __init__(self, url='http://portal.buaiti.com:3000/service', headers={'Content-Type': 'application/json'}):
        self.url = url
        self.headers = headers

    def call_get(self, sys_name, kpi_id, thread_id, request_cnt, s):
        url = self.url + '/' + sys_name + '/' + kpi_id
        print('thread' + str(thread_id) + '_' + sys_name + '_get' + str(request_cnt) + ':')
        r = s.get(url, headers=self.headers)
        if r.status_code == requests.codes.ok:
            print(r.text)
        else:
            r.raise_for_status()

    def call_get_all(self, sys_name, thread_id, request_cnt, s):
        url = self.url + '/' + sys_name + '/kpis'
        print('thread' + str(thread_id) + '_' + sys_name + '_get' + str(request_cnt) + ':')
        r = s.get(url, headers=self.headers)
        if r.status_code == requests.codes.ok:
            print(r.text)
        else:
            print(thread_id+'error')
            r.raise_for_status()

    def call_put(self, sys_name, thread_id, request_cnt, s):
        kpi = 'loop_test' + str(thread_id)
        #url = self.url + '/' + sys_name + '/' + kpi
        url = self.url + '/' + sys_name + '/kpix'
        #data = {'kpi': kpi, 'group': ['test'], 'data': [[random.randint(0, 10000)]]}
        data = {'kpi': "kpix", 'group': ['test'], 'data': [[request_cnt]]}
        print('thread' + str(thread_id) + '_' + sys_name + '_get' + str(request_cnt) + ':')
        r = s.put(url, data=json.dumps(data), headers=self.headers)
        if r.status_code == requests.codes.ok:
            print(r.text)
        else:
            r.raise_for_status()


def loop_put(thread_id, sleep_time):
    request_cnt = 0
    s = requests.Session()
    while True:
        request_cnt += 1
        req = call_request(URL)
        req.call_put('mivs', thread_id, request_cnt, s)
        time.sleep(random.randint(1, sleep_time)/100)


def loop_get(thread_id, sleep_time):
    request_cnt = 0
    s = requests.Session()
    while True:
        request_cnt += 1
        req = call_request(URL)
        req.call_get_all('mivs', thread_id, request_cnt, s)
        time.sleep(random.randint(1, sleep_time)/100)


def thread(write_num, read_num, sleep_time):
    write_threads = []
    read_threads = []
    for i in range(0, write_num):
        t = threading.Thread(target=loop_put, args=(i, sleep_time))
        write_threads.append(t)
    print("write_threads:")
    print(write_threads)

    for i in range(0, read_num):
        t = threading.Thread(target=loop_get, args=(i, sleep_time))
        read_threads.append(t)
    print("read_threads:")
    print(read_threads)

    for t in write_threads:
        t.start()

    for t in read_threads:
        t.start()

    for t in write_threads:
        t.join()

    print("start read")
    for t in read_threads:
        t.join()


if __name__ == '__main__':

    thread(WRITE_THREAD_NUM, READ_THREAD_NUM, MAX_SLEEP_TIME)
    # requests.delete('http://portal.buaiti.com:3000/service/mivs/kpis')
