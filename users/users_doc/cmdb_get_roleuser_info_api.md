# CMDB 获取运维角色分组接口 说明

- 请求地址
	- 正式环境
		
		https://cmdb.cy666.com/api_user/role_info
		
	- 本地测试环境
    
    http://192.168.90.38:8000/api_user/role_info
	  
	- 外网测试环境
	  
	  https://58.63.33.155:5670/api_user/role_info
	  
	  
	
- 请求方式
	
	GET

-  可选参数
  
  - name  可选，分组名字，使用后只返回该分组的信息，不使用则返回全部分组信息


- 返回结果
```python
{
    'data': {
        '原力运维小组':{
            'project':['超神荣耀','校花','剑雨江湖','剑雨手游','三生三世','少年H5','超神学院','超神学院','少年群侠传','少年3D'],
            'mail':['lixiaolong@forcegames.cn','liangjun@forcegames.cn'],
            'project_en': ['csry', 'xh', 'jyjh', ...],
            'user': ['lixiaolong', 'liangjun'],
        },
        '创畅外派小组':{
            'project':['骑战三国','名将分争'],
            'mail':['lixiaolong@chuangyunet.com'],
            'project_en': ['qzsg', 'mjfz'],
            'user': ['lixiaolong'],
        },
        '运维组':{
            'project':['原力内网','原力腾讯云'],
            'mail':['41816456@qq.com']
            'project_en': ['ylnw', 'yltxy'],
            'user': ['lixiaolong'],
        }
    },
    'success': True
}

```

|参数|类型|说明|
|----|---|----|
|data|json|若请求成功，则返回数据内容，若失败，则返回失败原因     -----1. project：关联项目中文名的 list    -----2. mail：角色分组内成员的邮箱的 list    -----3. project_en：关联项目英文名的list         ----4. user：角色分组内成员的拼音|
|success|boolean|请求成功或者失败   True or False|


- 请求实例
```python
#python 代码示例：
# -*- encoding: utf-8 -*-

import requests

url = 'http://192.168.90.37:8000/api_user/role_info'
token = 'your_token' 
headers={'Authorization': 'token {}'.format(token)}

# res = requests.get(url, query_param='?name=创畅外派' headers=headers) 
res = requests.get(url, headers=headers) 
if res.status_code == 200:
    r = res.json()
    print (r)
```

```shell
# 使用参数
curl -H 'Authorization: Token your_token' -k "https://cmdb.cy666.com/api_user/role_info?name=原力运维小组"

# 不使用参数
curl -H 'Authorization: Token your_token' -k "https://cmdb.cy666.com/api_user/role_info"
```

