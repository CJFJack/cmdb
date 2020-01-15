# CMDB 修改开服时间 API 说明



- 请求地址
    - 正式环境-外网
      
	    https://58.63.33.155:5656/api_web/ModifySrvOpenTimeSchedule.Create/
	    
	- 正式环境-内网
		
		https://cmdb.cy666.com/api_web/ModifySrvOpenTimeSchedule.Create/
    
    - 测试环境
      
        http://192.168.90.37:8000/api_web/ModifySrvOpenTimeSchedule.Create/
    
- 请求方式
	
	post	

- 请求json格式
```python
{
    "project": "cyh5s7",
    "area": "cn",
    "srv_id": "1600001",  # web区服id
    "open_time": "1581419600",
}
```

| 参数      | 类型 | 说明                                 |
| --------- | ---- | ------------------------------------ |
| project   | str  | 游戏项目英文名，如：cyh5s7           |
| area      | str  | 地区英文名，如：cn                   |
| srv_id    | str  | web区服id，如：1600001               |
| open_time | str  | 修改开服时间，时间戳，如：1581419600 |


- 返回结果
```python
{'success': True, 'msg': 'cmdb接收成功'}
```

|参数|类型|说明|
|----|---|----|
|success|boolen|接收状态；True：成功；False：失败|
|msg|str|接收成功或失败的原因|


- 请求实例
```python
#python 代码示例：
# -*- encoding: utf-8 -*-

import requests
import json

url = 'http://127.0.0.1:8000/api_web/ModifySrvOpenTimeSchedule.Create/'
token = '431b65c0a00dfa00399a8e36c47f54ad5d3686d5'
headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
data = {
    "project": "cyh5s7",
    "area": "cn",
    "srv_id": "1600001",  # web区服id
    "open_time": "1581419600",
}
res = requests.post(url, data=data, headers=headers, timeout=60, verify=False)
if res.status_code == 200:
    r = res.json()
    print (r)
```

