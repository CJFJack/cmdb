CMDB 主机API接口规范
===========================
[TOC]

## 说明
CMDB提供了关于查询主机，增加主机，修改主机的api接口，接口统一采用POST的请求方式和token认证，需要在POST的请求头信息添加如下:

```
headers = {
    'Accept': 'application/json',
    'Authorization': 'Token login_token'
}
```

并且统一返回json格式的数据。最终返回的json格式为:

```
{"reason": data, "resp": 1}
```
**resp** 为1时，表示请求能正确处理， **data**为返回的内容
**resp** 不是时，表示请求有异常，查看**data**的内容获取异常的详细

## 注意事项:
**每次请求完成以后，先查看status_code的值，如果是200，然后查看resp**
**host查询的查看方式不同，具体详见获取服务器列表注意事项**


## host表字段说明

- status 状态标识 整型字段
> 0未初始化  1可用  2停用  3新机器  4已归还

- host_class 机器归属 整型字段
> 0公司内网  1公司自有外网机器  2游戏合作商提供

- belongs_to_game_project 所在项目 关联项目表
> 用项目的英文名，目前不接收中文名称

- belongs_to_room 所在机房 关联机房表
> 用机房的机房名

- machine_type 机器类型 整型字段
> 0云主机  1物理机

- belongs_to_business 业务类型 关联业务类型表
> 用业务类型的名字

- platform 平台或者提供商标识 字符串类型

- internal_ip 局域网IP 字符串类型
> 可以为空

- telecom_ip 电信ip 字符串类型
> 可以为空 唯一约束

- unicom_ip 联通ip 字符串类型
> 可以为空 唯一约束

- system 操作系统 整型字段
> 0linux  1windows

- is_internet 是否公网访问状态标识  整型字段
> 0完全内网机器 1公网访问不了但可上外网 2公网可访问

- sshuser 服务器SSH用户 字符串类型

- sshport 服务器SSH端口 字符串类型

- machine_model 机器型号 字符串类型

- cpu_num cpu核心数 整型字段

- cpu cpu 字符串类型

- ram ram 字符串类型

- disk disk 字符串类型

- host_comment 用途 字符串类型

- belongs_to_host 所属宿主机 字符串类型

- host_identifier 主机唯一标识符 字符串类型
  > host_identifier一般以 **项目_机房_IP**作为唯一的标识
  IP可以是电信ip，联通ip，内网ip


## 获取服务器列表
**每次请求完成以后，先查看status_code的值，如果是200，然后查看resp, resp为True,则说明有查询结果，否则没有**

*接口地址*

- https://cmdb.cy666.com/api/Host.List/

*HTTP请求方式*

- POST

*请求参数*

- keywords **可选**
> 表示要筛选的字段的值，如果没有，则返回全部的host列表
> example
```
keywords = {
    'status': 1,
    'telecom_ip': '103.231.67.56',
}
```
表示获取**状态**为可用, **电信ip**为103.231.67.56的服务器信息


*示例*

- 命令行模式
>
```
curl -X POST -k https://cmdb.cy666.com/api/Host.List/ -H 'Authorization: Token login_token' -H 'Content-Type: application/json' -d '{"keywords": {"telecom_ip": "1.1.1.1"}}'
```
返回json:
```
{"data": [{"is_internet": "\u5b8c\u5168\u5185\u7f51\u673a\u5668", "host_comment": "\u5251\u96e8\u624b\u6e38\u7248\u7f72", "host_class": "\u516c\u53f8\u5185\u7f51", "belongs_to_business": "game", "disk": "200G", "unicom_ip": "2.2.2.2", "machine_type": "\u4e91\u4e3b\u673a", "belongs_to_room": "\u5317\u4eac\u6570\u636e\u4e2d\u5fc3", "telecom_ip": "1.1.1.1", "internal_ip": "3.3.3.3", "machine_model": "pc", "cpu_num": 4, "platform": "ruike", "id": 22124, "system": "linux", "sshport": 10086, "cpu": "xen", "ram": "16G", "sshuser": "root", "belongs_to_game_project": "\u5251\u96e8\u6c5f\u6e56", "status": "\u505c\u7528", "host_identifier": "jyjh_yy_192.168.1.1"}], "resp": 1}
```
字段说明
> reason  返回的服务器list
> resp  操作成功

- python脚本 推荐使用[requests](https://docs.python-requests.org/zh_CN/latest/user/quickstart.html)库
>
```
keywords = {
    'status': 1,
    'telecom_ip': '103.231.67.56',
}

 headers = {
    'Accept': 'application/json',
    'Authorization': 'Token login_token'
}

 def get_host_info(headers, keywords=None):
    '''根据hostname和相应的字段获取host的信息'''
    url = 'https://cmdb.cy666.com/api/Host.List/'    # 修改这里的url

    if keywords:
        payload = {'keywords': keywords}
    else:
        payload = None

    r = requests.post(url, headers=headers, json=payload, verify=False)
    print(r.status_code, r.json().get('data'))
```
返回json:
```
 {'reason': [{'belongs_to_business': 'banshu',
           'belongs_to_game_project': '手游剑雨',
           'belongs_to_room': '北京数据中心',
           'cpu': 'Vcpu',
           'cpu_num': 4,
           'disk': '500G',
           'host_class': '公司自有外网机器',
           'host_comment': '剑雨手游版署',
           'id': 22029,
           'internal_ip': '192.168.67.56',
           'is_internet': '公网可访问',
           'machine_model': '云主机',
           'machine_type': '云主机',
           'platform': 'ruike',
           'ram': '8G',
           'sshport': 9022,
           'sshuser': 'root',
           'status': '可用',
           'system': 'linux',
           'telecom_ip': '103.231.67.56',
           ...
           'unicom_ip': None}],
  'resp': True}
```

## 增加服务器

*接口地址*

- https://cmdb.cy666.com/api/Host.Create/

*HTTP请求方式*

- POST

*请求参数*

- 除了**internal_ip**, **telecom_ip**, **unicom_ip**， **belongs_to_host**可以不填,其他的参数必须要填写,并且不能为空，不然会返回False
- **internal_ip**, **telecom_ip**, **unicom_ip**至少有一个有值 
> 表示要筛选的字段的值，如果没有，则返回全部的host列表
> example
```
host_info = {
    'status': 0,
    'host_class': 0,
    'belongs_to_game_project': 'jyjh',    # **项目英文名称**
    'belongs_to_room': '北京数据中心',    # **机房名**
    'machine_type': 0,
    'belongs_to_business': 'game',    # **业务类型名**
    'platform': 'ruike',
    'telecom_ip': '1.1.1.1',
    'system': 0,
    'is_internet': 0,
    'sshuser': 'root',
    'sshport': '22',
    'machine_model': 'pc',
    'cpu_num': 4,
    'cpu': 'xen',
    'ram': '16G',
    'disk': '200G',
    'host_comment': '剑雨手游版署',
    'host_identifier': 'jyjh_yy_192.168.1.1',
}
```
*示例*

- 命令行模式
>
```
curl -X POST -k https://cmdb.cy666.com/api/Host.Create/ -H 'Authorization: Token login_token' -H 'Content-Type: application/json' -d '{"status": 0, "host_class": 0, "belongs_to_game_project": "剑雨江湖", "belongs_to_room": "北京数据中心", "machine_type": 0, "belongs_to_business": "game", "platform": "ruike", "telecom_ip": "1.1.1.1", "system": 0, "is_internet": 0, "sshuser": "root", "sshport": "23", "machine_model": "pc", "cpu_num": 4, "cpu": "xen", "ram": "16G", "disk": "130G", "host_comment": "剑雨手游版署", "host_identifier": "jyjh_yy_192.168.1.1"}'
```
返回json:
```
{"reason": {"sshuser": "root", "machine_type": "\u4e91\u4e3b\u673a", "belongs_to_game_project": "\u5251\u96e8\u6c5f\u6e56", "internal_ip": null, "status": "\u505c\u7528", "disk": "130G", "system": "linux", "is_internet": "\u5b8c\u5168\u5185\u7f51\u673a\u5668", "id": 22125, "cpu_num": 4, "host_comment": "\u5251\u96e8\u624b\u6e38\u7248\u7f72", "machine_model": "pc", "belongs_to_business": "game", "telecom_ip": "1.1.1.1", "belongs_to_room": "\u5317\u4eac\u6570\u636e\u4e2d\u5fc3", "unicom_ip": null, "cpu": "xen", "ram": "16G", "host_class": "\u516c\u53f8\u5185\u7f51", "platform": "ruike", "sshport": "23", "host_identifier": "jyjh_yy_192.168.1.1"}, "resp": 1}
```
字段说明
> reason  返回添加成功的host信息
> resp  操作成功

- python脚本 推荐使用[requests](https://docs.python-requests.org/zh_CN/latest/user/quickstart.html)库
```
headers = {
    'Accept': 'application/json',
    'Authorization': 'Token login_token'
}

 host_info = {
    'status': 0,
    'host_class': 0,
    'belongs_to_game_project': 'jyjh',
    'belongs_to_room': '北京数据中心',
    'machine_type': 0,
    'belongs_to_business': 'game',
    'platform': 'ruike',
    'telecom_ip': '1.1.1.1',
    'system': 0,
    'is_internet': 0,
    'sshuser': 'root',
    'sshport': '22',
    'machine_model': 'pc',
    'cpu_num': 4,
    'cpu': 'xen',
    'ram': '16G',
    'disk': '200G',
    'host_comment': '剑雨手游版署',
    'host_identifier': 'jyjh_yy_192.168.1.1',
}

 def add_host(headers, host_info):
    '''添加host记录'''

    url = 'https://cmdb.cy666.com/api/Host.Create/'

    payload = host_info

    r = requests.post(url, headers=headers, json=payload, verify=False)

    pprint(r.json())
```
返回json:
```
{'reason': {'belongs_to_business': 'game',
          'belongs_to_game_project': 'jyjh',
          'belongs_to_room': '北京数据中心',
          'cpu': 'xen',
          'cpu_num': 4,
          'disk': '200G',
          'host_class': '公司内网',
          'host_comment': '剑雨手游版署',
          'id': 22126,
          'internal_ip': None,
          'is_internet': '完全内网机器',
          'machine_model': 'pc',
          'machine_type': '云主机',
          'platform': 'ruike',
          'ram': '16G',
          'sshport': '22',
          'sshuser': 'root',
          'status': '停用',
          'system': 'linux',
          'telecom_ip': '1.1.1.1',
          'host_identifier': 'jyjh_yy_192.168.1.1',
          'unicom_ip': None},
 'resp': 1}
```
字段说明
> reason  返回添加成功的host信息
> resp  操作成功


## 修改服务器信息
*接口地址*

- https://cmdb.cy666.com/api/Host.Modify/

*HTTP请求方式*

- POST

*请求参数*

- old_host_info **必选**
> 通过原来的服务器的字段的信息来获取cmdb中唯一的记录
有四种可选的字段
> - telecom_ip  # 唯一约束
> - unicom_ip  # 唯一约束
> - belongs_to_game_project, belongs_to_room, internal_ip  # 三个字段组合唯一
> - host_identifier # 主机唯一标识符
> example
通过**telecom_ip**获取唯一的记录
```
old_host_info = {
    'telecom_ip': '1.1.1.1',
```
通过**unicom_ip**获取唯一的记录
```
old_host_info = {
    'unicom_ip': '2.2.2.2',
```
通过**belongs_to_game_project**, **belongs_to_room**, **internal_ip**获取唯一的记录
```
old_host_info = {
    'belongs_to_game_project': '剑雨江湖',
    'belongs_to_room': '北京数据中心',
    'internal_ip': '3.3.3.3',
}
```
多个条件的情况下，通过最先匹配的获取唯一记录, 这里是**telecom_ip**
```
old_host_info = {
    'telecom_ip': '1.1.1.1',
    'unicom_ip': '2.2.2.2',
    'belongs_to_game_project': '剑雨江湖',
    'belongs_to_room': '北京数据中心',
    'internal_ip': '3.3.3.3',
}
```

- new_host_info **必选**
> 要更新的字段的值
> example
> 这里将匹配到的唯一的记录的sshuser和sshport做了更新
```
new_host_info = {
    'sshuser': 'admin',
    'sshport': '10086',
}
```
*示例*

- 命令行模式
>
```
curl -X POST -k https://cmdb.cy666.com/api/Host.Modify/ -H 'Authorization: Token login_token' -H 'Content-Type: application/json' -d '{"old_host_info": {"telecom_ip": "1.1.1.1"}, "new_host_info": {"sshuser": "admin", "sshport": 10086}}'
```
返回json:
```
{"reason": {"disk": "200G", "ram": "16G", "host_comment": "\u5251\u96e8\u624b\u6e38\u7248\u7f72", "sshport": 10086, "belongs_to_game_project": "\u5251\u96e8\u6c5f\u6e56", "internal_ip": null, "status": "\u505c\u7528", "platform": "ruike", "system": "linux", "cpu_num": 4, "is_internet": "\u5b8c\u5168\u5185\u7f51\u673a\u5668", "machine_type": "\u4e91\u4e3b\u673a", "belongs_to_room": "\u5317\u4eac\u6570\u636e\u4e2d\u5fc3", "belongs_to_business": "game", "id": 22126, "machine_model": "pc", "sshuser": "admin", "cpu": "xen", "unicom_ip": null, "host_class": "\u516c\u53f8\u5185\u7f51", "telecom_ip": "1.1.1.1"}, "resp": 1}
```
字段说明
> reason  返回修改成功的host信息
> resp  操作成功

- python脚本 推荐使用[requests](https://docs.python-requests.org/zh_CN/latest/user/quickstart.html)库
```
headers = {
    'Accept': 'application/json',
    'Authorization': 'Token login_token'
}
old_host_info = {
    'telecom_ip': '1.1.1.1',
    'unicom_ip': '2.2.2.2',
    'belongs_to_game_project': '剑雨江湖',
    'belongs_to_room': '北京数据中心',
    'internal_ip': '3.3.3.3',
}
new_host_info = {
    'sshuser': 'admin',
    'sshport': '10086',
}
payload = {'old_host_info': old_host_info, 'new_host_info': new_host_info}
r = requests.post(url, headers=headers, json=payload)
pprint(r.json())
```
返回json:
```
'reason': {'belongs_to_business': 'game',
          'belongs_to_game_project': 'jyjh',
          'belongs_to_room': '北京数据中心',
          'cpu': 'xen',
          'cpu_num': 4,
          'disk': '200G',
          'host_class': '公司内网',
          'host_comment': '剑雨手游版署',
          'id': 22126,
          'internal_ip': None,
          'is_internet': '完全内网机器',
          'machine_model': 'pc',
          'machine_type': '云主机',
          'platform': 'ruike',
          'ram': '16G',
          'sshport': 10086,
          'sshuser': 'admin',
          'status': '停用',
          'system': 'linux',
          'telecom_ip': '1.1.1.1',
          'unicom_ip': None},
 'resp': 1}
```
字段说明
> reason  返回添加成功的host信息
> resp  操作成功


## 支持
如果有bug和疑问，联系 yanwenchi@chuangyunet.com