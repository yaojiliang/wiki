'''
模拟高并发发送请求

'''

import random
from threading import Thread
import requests

# 线程事件函数　- 随机向8000或者8001发送请求
def get_request():
    url = 'http://127.0.0.1:8000/test/'
    url2 = 'http://127.0.0.1:8001/test/'
    get_url = random.choice([url,url2])
    html=requests.get(get_url).text
    print(html)

t_list=[]
for i in range(30):
    t = Thread(target=get_request)
    t_list.append(t)
    t.start()

for t in t_list:
    t.join()



