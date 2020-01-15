# WEB 同步挂维护信息到 CMDB 接口 说明



- 请求地址
    - 正式环境-外网
      
	    https://58.63.33.155:5656/api_web/RecvWebMaintenanceInfo/
	    
	- 正式环境-内网
		
		https://cmdb.cy666.com/api_web/RecvWebMaintenanceInfo/
    
    - 测试环境-内网
      
        http://192.168.90.388000/api_web/RecvWebMaintenanceInfo/
        
    - 测试环境-外网
    
        https://58.63.33.155:5670/api_web/RecvWebMaintenanceInfo/
    
- 请求方式
	
	post	

- 请求json格式
```python
{
    'project': 'jysybt',
    'area': 'cn',
    'maintenance_type': 3,          #  1：合服  2：迁服  3：版本更新  -1：其他
    'srv_id_list': '15000001,15000002,16000001,16000001,500001'
}
```

| 参数             | 类型 | 说明                                               |
| ---------------- | ---- | -------------------------------------------------- |
| project          | str  | 项目英文简称                                       |
| area             | str  | 地区英文简称                                       |
| maintenance_type | int  | 1：合服  <br>2：迁服  <br>3：版本更新 <br>-1：其他 |
| srv_id_list           | str  | 区服id，有多个时以英文逗号隔开                     |




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

url = 'http://127.0.0.1:8000/api_web/RecvWebMaintenanceInfo/'
token = '431b65c0a00dfa00399a8e36c47f54ad5d3686d5'
headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
post_data = {
    'project': 'jysybt',
    'area': 'cn',
    'maintenance_type': 3,          #  1：合服  2：迁服  3：版本更新  -1：其他
    'srv_id_list': '15000001,15000002,16000001,16000001,500001'
}
res = requests.post(url, json=post_data, headers=headers, timeout=60, verify=False)
if res.status_code == 200:
    r = res.json()
    print (r)
```

