# CMDB 修改开服时间回调API 说明



- 请求地址
    - 正式环境-外网
      
	    https://58.63.33.155:5656/api/ModSrvOpenTimeCallBack/
	    
	- 正式环境-内网
		
		https://cmdb.cy666.com/api/ModSrvOpenTimeCallBack/
    
    - 测试环境-内网
      
        http://192.168.90.38:8000/api/ModSrvOpenTimeCallBack/
        
    - 测试环境-外网
    
        https://58.63.33.155:5670/api/ModSrvOpenTimeCallBack/
    
- 请求方式
	
	post	

- 请求json格式
```python
{
	"uuid": "xxx-xxx-xxxxx",
    "sid": "331910", # web区服id
    "result": True or False,
    "msg": "xxx",
}
```

| 参数   | 类型   | 说明                    |
| ------ | ------ | ----------------------- |
| uuid   | str    | 任务唯一标识            |
| sid    | str    | web区服id，如：331910   |
| result | boolen | 修改结果：True or False |
| msg    | str    | 修改成功或者失败的备注  |


- 返回结果
```python
{'success': True, 'msg': 'cmdb回调成功'}
```

|参数|类型|说明|
|----|---|----|
|success|boolen|接收状态；True：成功；False：失败|
|msg|str|回调成功或失败的原因|


- 请求实例
```python
#python 代码示例：
# -*- encoding: utf-8 -*-

import requests
import json

url = 'http://127.0.0.1:8000/api/ModSrvOpenTimeCallBack/'
token = 'c6e7724396561cfd9004718330fc8a6dcbaf6409'
headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
data = {
	"uuid": "xxx-xxx-xxxxx",
    "sid": "331910",
    "result": True or False,
    "msg": "xxx",
}
res = requests.post(url, json=data, headers=headers, timeout=60, verify=False)
if res.status_code == 200:
    r = res.json()
    print (r)
```

