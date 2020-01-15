数据库实例接口文档
================

[TOC]

## 说明
这边文档是关于如何调用cmdb的api对cmdb数据库mysql实例的增删改

## 字段描述

- project 归属项目 关联到项目
    > 用项目的英文名
- area 地区 字符串类型
- purpose 用途 字符串类型
- host 地址 字符串类型
- port 端口 字符串类型
- user 用户 字符串类型
- password 密码 字符串类型
- white_list 白名单 字符串类型(json list格式)
>如果没有白名单的mysql实例,white_list传`None`即可

`host`和`port`字段的组合为**唯一**。


## 添加mysql实例

*接口地址*

- https://cmdb.cy666.com/api_mysql/Instance.Create/

*HTTP请求方式*

- POST

*请求参数*

```
pdata = {
        "project": 'snsy',
        "area": '大陆',
        "purpose": '测试',
        "host": "192.168.56.101",
        "port": '3307',
        "user": 'mysql',
        "password": 'mypassword',
        "white_list": ['192.168.56.101', '192.168.100.181'],   # list格式
        # "white_list": None,    # 如果没有的话
    }
```

*示例*

```
def mysql_create():
    """测试mysql实例创建
    """

    url = 'http://192.168.56.101/api_mysql/Instance.Create/'

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Token your_token'
    }

    pdata = {
        "project": 'snsy',
        "area": '大陆',
        "purpose": '测试',
        "host": "192.168.56.101",
        "port": '3307',
        "user": 'mysql',
        "password": 'mypassword',
        "white_list": ['192.168.56.101', '192.168.100.181']   # list格式
        # "white_list": None,    # 如果没有的话
    }

    r = requests.post(url, headers=headers, json=json.dumps(pdata))

    print(r.json())
```

*返回结果*

`{'resp': 1, 'reason': {'project': 'snsy', 'port': '3307', 'area': '大陆', 'id': 1, 'user': 'mysql', 'password': 'mypassword', 'purpose': '测试', 'host': '1.1.1.1'}}`

其中, **resp**为**1**代表成功, **reason**返回你创建时的实例参数

## 修改mysql实例

*接口地址*

- https://cmdb.cy666.com/api_mysql/Instance.Modify/

*HTTP请求方式*

- POST

*请求参数*

- `old_instance`表示你要查找过滤出来的**唯一**的实例，接口不要求你一定要传哪些参数，但是要求能通过这些参数获取到**唯一的**mysql实例。
    > 示例 old_instance = {'host': '192.168.56.101'} 表示获取cmdb的mysql实例中通过host为192.168.56.101的**唯一**记录，如果没有或者有多个记录，将会返回相应的错误
- `new_instance`表示你要更新的字段内容
    > 示例 new_instance = {'user': 'root2', 'area': 'hk', 'password': 'redhat'}。表示将通过**old_instance**获取到的唯一的实例，更新用户字段为root2, 地区字段为hk, password字段为redhat

*示例*

```
def mysql_modify():
    """修改mysql实例
    """

    url = 'http://192.168.56.101/api_mysql/Instance.Modify/'

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Token your_token'
    }

    old_instance = {'host': '192.168.56.101', 'port': 3307}
    new_instance = {
        'user': 'root2', 'area': 'hk', 'password': 'redhat',
        # "white_list": None,    # 如果没有的话
    }

    payload = {'old_instance': old_instance, 'new_instance': new_instance}

    r = requests.post(url, headers=headers, json=json.dumps(payload))

    print(r.json())
```

*返回结果*

`{'reason': {'port': '3307', 'user': 'root2', 'id': 1, 'area': 'hk', 'purpose': '测试', 'password': 'redhat', 'project': 'snsy', 'host': '192.168.56.101'}, 'resp': 1}`

其中, **resp**为**1**代表成功, **reason**返回修改后的实例字段参数


## 删除mysql实例

*接口地址*

- https://cmdb.cy666.com/api_mysql/Instance.Delete/

*HTTP请求方式*

- POST

*请求参数*

```
pdata = {
        "host": "192.168.56.101",
        "port": '3307',
    }
```

*示例*

```
def mysql_delete():
    """删除mysql实例
    """

    url = 'http://192.168.56.101/api_mysql/Instance.Delete/'

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Token your_token'
    }

    pdata = {
        "host": "192.168.56.101",
        "port": '3307',
    }

    r = requests.post(url, headers=headers, json=json.dumps(pdata))

    print(r.json())
```

*返回结果*

`{'resp': 1, 'reason': 'delete ok'}`

其中, **resp**为**1**代表成功


## 获取mysql实例

*接口地址*

- https://cmdb.cy666.com/api_mysql/Instance.List/

*HTTP请求方式*

- POST

*请求参数*

api不会强制要求是使用哪些查询参数，只会根据你提供的查询参数来获取实例，如果有，则返回，没有，返回空的list

*示例*

```
def mysql_list():
    """查询mysql实例
    """

    url = 'http://192.168.56.101/api_mysql/Instance.List/'

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Token your_token'
    }

    pdata = {
        "host": "192.168.56.101",
    }

    r = requests.post(url, headers=headers, json=json.dumps(pdata))

    print(r.json())
```

*返回结果*

`{'reason': [{'purpose': '测试', 'port': '3306', 'project': 'ssss', 'id': 1, 'password': 'redhat', 'area': 'vng', 'host': '192.168.56.101', 'user': 'root'}, {'purpose': '测试', 'port': '3307', 'project': 'snsy', 'id': 4, 'password': 'mypassword', 'area': '大陆', 'host': '192.168.56.101', 'user': 'mysql'}], 'resp': 1}`

其中, **resp**为**1**代表成功