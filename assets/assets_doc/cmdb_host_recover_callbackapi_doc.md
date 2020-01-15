# CMDB 主机回收回调接口 说明

- 请求地址
	- 正式环境
		https://cmdb.cy666.com/api/HostRecoverCallBack/
	- 本地测试环境
	    http://192.168.90.38:8000/api/HostRecoverCallBack/
	- 外网测试环境
        https://58.63.33.155:5670/api/HostRecoverCallBack/

- 请求方式
	post

- 请求json格式
```
{
    "uuid": "xxx-xxx-xxxxx",
    "ip": "10.10.10.10",
    "result": True,      # or False
    "msg": "xxx",
}
```

|参数|类型|说明|
|----|---|----|
|uuid|str|任务标识|
|ip|str|主机电信ip|
|result|bool|执行结果：True or Flase|
|msg|str|结果信息|


- 返回结果
```
{'success': False, 'msg': '失败原因'}
```

|参数|类型|说明|
|----|---|----|
|success|boolen|执行状态；True：成功；False：失败|
|msg|str|执行成功或失败的原因|


- 请求实例
```
#python 代码示例：
# -*- encoding: utf-8 -*-

import requests
import json

url = 'http://192.168.90.37:8000/api/HostRecoverCallBack/'
token = '7c166721ab00350894172405c1b8bc0cce102b00' 
headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
data = {
    "uuid": "xxx-xxx-xxxxx",
    "ip": "10.10.10.10",
    "result": True,      # or False
    "msg": "xxx",
}
res = requests.post(url, json=data, headers=headers, timeout=60, verify=False) 
if res.status_code == 200:
    r = res.json()
    print (r)
```
