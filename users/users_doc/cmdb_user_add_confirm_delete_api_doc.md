# CMDB 开通账号 、确认入职、删除账号 API 说明

- [cmdb开通账号](#开通账号)
- [cmdb确认入职](#确认入职)
- [cmdb删除账号](#删除账号)



### <span id="开通账号">开通账号</span>

- 请求地址
	
	- 外网正式环境
		
		https://58.63.33.155:5656/api_user/user_add/
		
	- 内网正式环境
	
	  https://192.168.100.66/api_user/user_add/
	
	- 内网测试环境
	
	    http://192.168.90.37:8000/api_user/user_add/
	
- 请求方式
	post
	
- 请求json格式
```python
 {
	'username': '测试中文名字',
	'first_name': 'test_pinyin',
	'position': '运维测试工程师',
	'department': '原力互娱/运维部/网络管理组',
	'gender': 1,           # 1： 男  2： 女
	'is_qq': 0,            # 是否开通企业QQ   1： 是  0： 否
	'is_email': 0,         # 是否开通企业邮箱  0： 否  1：是，开通forcegames.cn  2：是，开通chuangyunet.com   3：是，同时开通forcegames.cn和chuangyunet.com
	'is_wifi': 0,          # 是否开通wifi    1： 是  0：否
}
```

|参数|类型|说明|
|----|---|----|
|username|str|用户中文姓名，该字段不允许重复|
|first_name|str|用户拼音，该字段不允许重复|
|position|str|职位|
|department|str|所属组织架构，如：原力互娱/运维部/网络管理组|
|gender|int|性别；1：男；2：女|
|is_qq|int|是否开通企业QQ；1：是；0：否|
|is_email|int|是否开通企业邮箱；0：否；1：是，开通 forcegames.cn；2：是，开通 chuangyunet.com；3：是，同时开通 forcegames.cn 和 chuangyunet.com|
|is_wifi|int|是否开通wifi；1：是；0：否|


- 返回结果
```python
{'success': True, 'msg': 'ok，初始密码为redhat'}
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

url = 'http://192.168.90.37:8000/api_user/user_add/'
token = '431b65c0a00dfa00399a8e36c47f54ad5d3686d5' 
headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
data = {
        'username': '测试中文名字',
        'first_name': 'test_pinyin',
        'position': '运维测试工程师',
        'department': '原力互娱/运维部/网络管理组',
        'gender': 1,          
        'is_qq': 0,            
        'is_email': 0,         
        'is_wifi': 0,        
}
res = requests.post(url, data=data, headers=headers, timeout=60, verify=False) 
if res.status_code == 200:
    r = res.json()
    print (r)
```





### <span id="确认入职">确认入职</span>

- 请求地址

  - 外网正式环境

    https://58.63.33.155:5656/api_user/user_confirm/

  - 内网正式环境
    
  https://192.168.100.66/api_user/user_confirm/
    
  - 内网测试环境
    
    http://192.168.90.37:8000/api_user/user_confirm/

- 请求方式
  
post
  
- 请求json格式

  ```python
  {
  	'first_name': 'test_pinyin',
  }
  或者
  {
      'username': '测试中文名字',
  }
  ```

  | 参数       | 类型 | 说明                                                |
  | ---------- | ---- | --------------------------------------------------- |
  | first_name | str  | 用户拼音，first_name 与 username 必须至少有一个     |
  | username   | str  | 用户中文名字，first_name 与 username 必须至少有一个 |

- 返回结果

  ```python
  {'success': True, 'msg': '确认入职成功'}
  ```

  | 参数    | 类型   | 说明                              |
  | ------- | ------ | --------------------------------- |
  | success | boolen | 执行状态；True：成功；False：失败 |
  | msg     | str    | 执行成功或失败的原因              |

- 请求实例

  ```python
  #python 代码示例：
  # -*- encoding: utf-8 -*-
  
  import requests
  import json
  
  url = 'http://192.168.90.37:8000/api_user/user_confirm/'
  token = '431b65c0a00dfa00399a8e36c47f54ad5d3686d5' 
  headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
  data = {
          'username': '测试中文名字',  
  }
  res = requests.post(url, data=data, headers=headers, timeout=60, verify=False) 
  if res.status_code == 200:
      r = res.json()
      print (r)
  ```

  

### <span id="删除账号">删除账号</span>

- 请求地址

  - 外网正式环境

    https://58.63.33.155:5656/api_user/user_delete/

  - 内网正式环境
    
  https://192.168.100.66/api_user/user_delete/
    
  - 内网测试环境
    
    http://192.168.90.37:8000/api_user/user_delete/

- 请求方式
  
post
  
- 请求json格式

  ```python
  {
  	'first_name': 'test_pinyin',
  }
  或者
  {
      'username': '测试中文名字',
  }
  ```

  | 参数       | 类型 | 说明                                                |
  | ---------- | ---- | --------------------------------------------------- |
  | first_name | str  | 用户拼音，first_name 与 username 必须至少有一个     |
  | username   | str  | 用户中文名字，first_name 与 username 必须至少有一个 |

- 返回结果

  ```python
  {'success': True, 'msg': '删除成功'}
  ```

  | 参数    | 类型   | 说明                              |
  | ------- | ------ | --------------------------------- |
  | success | boolen | 执行状态；True：成功；False：失败 |
  | msg     | str    | 执行成功或失败的原因              |

- 请求实例

  ```python
  #python 代码示例：
  # -*- encoding: utf-8 -*-
  
  import requests
  import json
  
  url = 'http://192.168.90.37:8000/api_user/user_delete/'
  token = '431b65c0a00dfa00399a8e36c47f54ad5d3686d5' 
  headers = {'Accept': 'application/json','Authorization': 'Token ' + token}
  data = {
          'username': '测试中文名字',  
  }
  res = requests.post(url, data=data, headers=headers, timeout=60, verify=False) 
  if res.status_code == 200:
      r = res.json()
      print (r)
  ```

  