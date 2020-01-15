# CMDB 获取版本更新计划接口 说明

- 说明：获取审核完成的版本更新单
	
- 请求地址
	
	- 正式环境
		
		https://cmdb.cy666.com/api/VersionUpdatePlan/
		
  - 本地测试环境
    
	  http://192.168.90.38:8000/api/VersionUpdatePlan/
	  
	- 外网测试环境
	  
	  https://58.63.33.155:5670/api/VersionUpdatePlan/
	
- 请求方式
	

post
	
- 请求json格式
```python
{
    ‘update_date’: '2019-10-31'    # 非必选，不传则获取审核完成且开始时间为当天的版本更新单
}
```

|参数|类型|必选|说明|
|----|---|----|----|
|update_date|str|否|日期|


- 返回结果
```python
{
	'success': True,
	'data': [{
		'end_time': '2019-10-31 10:00:00',
		'project': '剑雨手游BT',
		'applicant': '陈捷丰',
		'area': '大陆',
        'title': '剑雨BT版本更新20191031'
		'start_time': '2019-10-31 12:00:00'
	}, {
		'end_time': '2019-10-31 12:00:00',
		'project': '剑雨江湖',
		'applicant': '陈捷丰',
		'area': '大陆',
        'title': '剑雨页游版本更新20191031'
		'start_time': '2019-10-31 09:00:00'
	}]
}
```

|参数|类型|说明|
|----|---|----|
|success|boolean|执行状态；True：成功；False：失败|
|data|list|由版本更新计划字典组成的列表，字典中参数说明：<br>  - start_time: 开始时间<br>  - end_time: 结束时间<br>  - project: 项目<br>  - area: 地区<br>  - applicant: 申请人<br>  - title: 申请单标题|


- 请求实例
```python
# python 代码示例：
# -*- encoding: utf-8 -*-

import requests
import json

url = 'http://192.168.90.38:8000/api/VersionUpdatePlan/'
token = 'xxxxxx-xxx-xxx-xxxxxx-xxxxxx' 
headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
data = {}
res = requests.post(url, json=data, headers=headers, timeout=60, verify=False) 
if res.status_code == 200:
    r = res.json()
    print (r)
```

