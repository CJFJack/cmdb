# CMDB 项目下架回调接口 说明

- 请求地址
	- 正式环境
		https://cmdb.cy666.com/api/GameServerOffCallBack/
	- 本地测试环境
	    http://192.168.90.37:8000/api/GameServerOffCallBack/
	- 外网测试环境
        http://58.63.33.155:5659/api/GameServerOffCallBack/

- 请求方式
	post

- 请求json格式
```
{
    "uuid": "xxx-xxx-xxxxx",
    "sid": "31512",
    "result": True or False,
    "msg": "xxx",
}
```

|参数|类型|说明|
|----|---|----|
|uuid|str|任务标识|
|sid|int|web区服id|
|result|bool|下架结果：True or Flase|
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

url = 'http://192.168.90.37:8000/api/GameServerOffCallBack/'
token = '7c166721ab00350894172405c1b8bc0cce102b00' 
headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
data = {
    "uuid": "xxx-xxx-xxxxx",
    "sid": "31511",
    "result": True,
    "msg": "xxx",
}
res = requests.post(url, json=data, headers=headers, timeout=60, verify=False) 
if res.status_code == 200:
    r = res.json()
    print (r)
```
