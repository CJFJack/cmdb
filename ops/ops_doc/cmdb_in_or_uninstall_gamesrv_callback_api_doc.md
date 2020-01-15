# CMDB 装 / 卸服回调接口 说明

- 请求地址
	- 正式环境
		
		https://cmdb.cy666.com/api_web/InOrUninstallGameSrvCallback/
		
	- 本地测试环境
    
    http://192.168.90.38:8000/api_web/InOrUninstallGameSrvCallback/
	  
	- 外网测试环境
	  
	  https://58.63.33.155:5670/api_web/InOrUninstallGameSrvCallback/
	
- 请求方式
	

post
	
- 请求json格式
```python
{
    'id': 1,
    'type': 'install'   # or uninstall
    'success': True,
    'data': '成功'
}
```

|参数|类型|说明|
|----|---|----|
|id|int|任务id|
|type|str| 回调类型： install - 装服 ；  uninstall - 卸服 |
|success|boolen|True - 成功 ； False - 失败|
|data|str|成功或者失败的描述|


- 返回结果
```python
{"resp": 1, "reason": 'ok'}
```

|参数|类型|说明|
|----|---|----|
|resp|int|1 - 回调成功 ； 0 - 回调失败|
|reason|str|回调成功或失败的原因|


- 请求实例
```python
#python 代码示例：
# -*- encoding: utf-8 -*-

import requests
import json

url = 'http://192.168.90.37:8000/api_web/InOrUninstallGameSrvCallback/'
token = '7c166721ab00350894172405c1b8bc0cce102b00' 
headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
data = {
    'id': 1,
    'type': 'install'   # or uninstall
    'success': True,
    'data': '成功'
}
res = requests.post(url, json=data, headers=headers, timeout=60, verify=False) 
if res.status_code == 200:
    r = res.json()
    print (r)
```

