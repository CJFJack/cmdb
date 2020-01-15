# CMDB 游戏区服下架 API 说明

- [新增区服下架计划](#新增区服下架计划)
- [删除区服下架计划](#删除区服下架计划)


### <span id="新增区服下架计划">新增区服下架计划</span> ###
- 请求地址
    - 正式环境-外网
        
	    https://58.63.33.155:5656/api_web/GameServerOff.Create/
	    
	- 正式环境-内网
		
	https://cmdb.cy666.com/api_web/GameServerOff.Create/
    	
    - 测试环境
        
        http://192.168.90.37:8000/api_web/GameServerOff.Create/
    
- 请求方式
	
post
	
- 请求json格式
```python
{
    "project": "jyjh",
    "area": "cn",
    "srv_id": '["31241", "31051"]',                # web区服id
    "off_time": "1581419600",
    "web_callback_url": "https://xxxxxx/",
}
或
{
    "project": "jyjh",
    "area": "vn",
    "srv_flag" : '["cross_vng_6", "vng_1"]',         # cmdb区服id
    "off_time": "1581419600",
    "web_callback_url": "https://xxxxxx/",
}
```

|参数|类型|说明|
|----|---|----|
|project|str|游戏项目英文名 或 中文名，如：jyjh 或 剑雨江湖|
|area|str|地区英文名，如：cn|
|srv_id|list|web区服id列表，如：["31241", "31051"]|
|srv_flag|list|cmdb区服id列表，如：["cross_vng_6", "vng_1"]|
|off_time|str|下线时间，时间戳，如：1581419600|
|web_callback_url|str|web回调地址|


- 返回结果
```
{'success': True, 'msg': 'ok'}
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

url = 'http://127.0.0.1:8000/api_web/GameServerOff.Create/'
token = '7c166721ab00350894172405c1b8bc0cce102b00'
headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
#data = {
#    "project": "jyjh",
#    "area": "vn",
#    "srv_flag" : '["cross_vng_6", "vng_1"]',      # cmdb区服id
#    "off_time": "1581419600",
#    "web_callback_url": "https://xxxxxx/",
#}
data = {
    "project": "jyjh",
    "area": "vn",
    "srv_id": '["31241", "31051"]',            # web区服id
    "off_time": "1581419600",
    "web_callback_url": "http://xxxxxx/",
}
res = requests.post(url,
                    data=data,
                    headers=headers,
                    timeout=60,
                    verify=False)
if res.status_code == 200:
    r = res.json()
    print (r)
```





### <span id="删除区服下架计划">删除区服下架计划</span> ###

- 请求地址
    - 正式环境-外网
        
        https://58.63.33.155:5656/api_web/GameServerOff.Delete/
        
    - 正式环境-内网
        
    https://cmdb.cy666.com/api_web/GameServerOff.Delete/
        
    - 测试环境
        
        http://192.168.90.37:8000/api_web/GameServerOff.Delete/
    
- 请求方式
    
post
    
- 请求json格式
```python
{
    "project": "jyjh",
    "area": "cn",
    "srv_id": '["31241", "31051"]',                # web区服id
    "off_time": "1581419600",
    "web_callback_url": "https://xxxxxx/",
}
或
{
    "project": "jyjh",
    "area": "vn",
    "srv_flag" : ["cross_vng_6", "vng_1"],         # cmdb区服id
    "off_time": "1581419600",
    "web_callback_url": "https://xxxxxx/",
}
```

|参数|类型|说明|
|----|---|----|
|project|str|游戏项目英文名 或 中文名，如：jyjh 或 剑雨江湖|
|area|str|地区英文名，如：cn|
|srv_id|list|web区服id列表，如：["31241",  "31051"]|
|srv_flag|list|cmdb区服id列表，如：["cross_vng_6", "vng_1"]|
|off_time|str|下线时间，时间戳，如：1581419600|
|web_callback_url|str|web回调地址|


- 返回结果
```
{'success': True, 'msg': 'ok'}
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

url = 'http://127.0.0.1:8000/api_web/GameServerOff.Delete/'
token = '7c166721ab00350894172405c1b8bc0cce102b00'
headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
#data = {
#    "project": "jyjh",
#    "area": "vn",
#    "srv_flag" : '["cross_vng_6", "vng_1"]',      # cmdb区服id
#    "off_time": "1581419600",
#    "web_callback_url": "https://xxxxxx/",
#}
data = {
    "project": "jyjh",
    "area": "vn",
    "srv_id": '["31241", "31051"]',            # web区服id
    "off_time": "1581419600",
    "web_callback_url": "http://xxxxxx/",
}
res = requests.post(url,
                    data=data,
                    headers=headers,
                    timeout=60,
                    verify=False)
if res.status_code == 200:
    r = res.json()
    print (r)
```
