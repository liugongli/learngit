import requests


proxies = {"http": "http://113.68.64.176:1042"}
rep = requests.get('http://172.18.247.86:7888/consumer/groupList.query', proxies=proxies).json()
print(rep)




