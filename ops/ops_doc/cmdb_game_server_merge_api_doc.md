# CMDB 创建合服计划接口 说明



- 请求地址
    - 正式环境-外网
      
	    https://58.63.33.155:5656/api_web/GameServerMerge.Create/
	    
	- 正式环境-内网
		
		https://cmdb.cy666.com/api_web/GameServerMerge.Create/
    
    - 测试环境-内网
      
        http://192.168.90.38:8000/api_web/GameServerMerge.Create/
        
    - 测试环境-外网
    
        https://58.63.33.155:5670/api_web/GameServerMerge.Create/
    
- 请求方式
	
	post	

- 请求json格式
```python
{
    'data': [
        {"main_srv": "1100001", "slave_srv": "1100003,1100004", "group_id": 1, "merge_time": "1234567890", "project": "jyjh"},
        {"main_srv": "1100002", "slave_srv": "1100006,1100007,1100008", "group_id": 2, "merge_time": "1234567123", "project": "ssss"},
        ...
    ],
}
```

| 参数 | 类型 | 说明                |
| ---- | ---- | ------------------- |
| data | list | list 中存放多个字典 |

字典中各个 key 值含义如下：

- main_srv：合服的主服 sid
- slave_srv：合服的从服 sid
- group_id：合服的组ID
- merge_time：合服时间
- project：项目英文简称，如jyjh、ssss等




- 返回结果
```python
{'success': True, 'msg': 'cmdb接收成功'}
```

|参数|类型|说明|
|----|---|----|
|success|boolen|接收状态；True：成功；False：失败|
|msg|str|cmdb接收成功或失败的原因|


- 请求实例
```python
#python 代码示例：
# -*- encoding: utf-8 -*-

import requests
import json

url = 'http://127.0.0.1:8000/api_web/GameServerMerge.Create/'
token = 'c6e7724396561cfd9004718330fc8a6dcbaf6409'
headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
post_data = {
    'data': [
        {"main_srv": "1100001", "slave_srv": "1100003,1100004", "group_id": 1, "merge_time": "1234567890", "project": "jyjh"},
        {"main_srv": "1100002", "slave_srv": "1100005,1100006,1100007", "group_id": 2, "merge_time": "1234567123", "project": "ssss"},
    ],
}
res = requests.post(url, json=post_data, headers=headers, timeout=60, verify=False)
if res.status_code == 200:
    r = res.json()
    print (r)
```

