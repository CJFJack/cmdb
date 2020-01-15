# CMDB 区服管理操作回调接口 说明

- 请求地址
	- 正式环境
		
		https://cmdb.cy666.com/api/GameServerActionCallback/
		
	- 本地测试环境
    
    http://192.168.90.38:8000/api/GameServerActionCallback/
	  
	- 外网测试环境
	  
	  https://58.63.33.155:5670/api/GameServerActionCallback/
	
- 请求方式
	

post
	
- 请求json格式
```python
{
    'uuid': 'xxxx-x-x-xxxx-xxx',
    'project': 'jyjh',
    'srv_id': 'cross_yy_4',
    'action_type': 'stop',
    'result': 1                 # 1:成功   0:失败,
    'msg': '成功'
}
```

|参数|类型|说明|
|----|---|----|
|uuid|str|任务唯一标识|
|project|str| 项目英文名                                                   |
|srv_id|str|cmdb区服id|
|action_type|str|操作类型，可选： start、stop、restart、clean，分别代表开服、关服、重启、清档|
|result|int|处理结果：  1 - 成功      0 - 失败|
|msg|str|成功或者失败的原因|


- 返回结果
```
{'success': False, 'msg': '失败原因'}
```

|参数|类型|说明|
|----|---|----|
|success|boolen|执行状态；True：成功；False：失败|
|msg|str|执行成功或失败的原因|


- 请求实例
```python
#python 代码示例：
# -*- encoding: utf-8 -*-

import requests
import json

url = 'http://192.168.90.37:8000/api/GameServerActionCallback/'
token = '7c166721ab00350894172405c1b8bc0cce102b00' 
headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
data = {
    'uuid': 'xxxx-x-x-xxxx-xxx',
    'project': 'jyjh',
    'srv_id': 'cross_yy_4',
    'action_type': 'stop',
    'result': 1                 # 1:成功   0:失败,
    'msg': '成功'
}
res = requests.post(url, json=data, headers=headers, timeout=60, verify=False) 
if res.status_code == 200:
    r = res.json()
    print (r)
```

