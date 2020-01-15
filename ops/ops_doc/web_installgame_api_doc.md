web装 / 卸服计划同步到cmdb API文档
======================

[TOC]

## 说明
web同步新装服和卸载服请求到cmdb。

目前只能使用**https**的**POST**请求

API采用**token**认证方式，因此需要在**请求头**中添加token认证 `Authorization: Token replace_token_here`，后面会有example。

## 返回值
API调用完成后，统一返回如下**json**:
`{"status": 1, "data": "json", "message": "ok"}`

- status int (0|1)
>1表示操作成功 0表示操作失败
- message string
>记录本次操作后返回的字符串信息, status非成功时必须有。
- data json
>如果有其他额外的信息，使用本字段

## 需要的字段
- project 字符串 新服游戏 
> web传**游戏英文名**。
- area 地区 字符串
> 游戏服的地区，目前有: 大陆，越南，台湾，韩国，新马泰
- pf_id 平台id 整型

- pf_name 平台名称 字符串

- srv_num 区服id 整型

- srv_name 区服名 字符串

- unique_srv_id 区服唯一ID 字符串

- server_version 后端版本号 字符串

- client_version 前端版本号 字符串 

  > 可选

- client_dir 前端目录 字符串

  > 可选

- open_time 开服时间 整型 时间戳

- status 状态
> 0未处理 1已处理 2已装服,修改开服时间未处理 -1已申请
- qq_srv_id 开平台区服ID 整型
> 可选，默认0
- srv_type 服务器组 整型
> 可选，默认1
- srv_farm_id 服务器群组ID 整型
> 可选，默认0
- srv_farm_name 服务器群组英文名 字符串
> 可选，默认default

其中，**project**, **area**, **pf_id**, **srv_num**或者
**project**, **area**, **pf_name**, **srv_num**
这**两种组合**的**四个字段**合起来是唯一的。

## 代码示例

### 新装区服

*接口地址*
- https://cmdb.cy666.com/api_web/InstallGameServer.Create/

*HTTP请求方式*

- POST

*请求参数*

POST请求的时候将**list转为json**

```python
pdata = [
    {
        "project": "ssss", "area": "大陆", "pf_id": "178",
        "pf_name": "178pop", "srv_num": "256", "srv_name": "双线一服",
        "server_version": "xxxx", "client_version": "xxxx", "client_dir": "xxxx",                 "open_time": "1531447135", "status": "0",
        "qq_srv_id": "100", "srv_type": "1", "srv_farm_id": "0",
        "srv_farm_name": "default", "unique_srv_id": "20000"
    },
    {
        "project": "csxy", "area": "大陆", "pf_id": "70",
        "pf_name": "xinghuiorg", "srv_num": "1000", "srv_name": "测试一服",
        "server_version": "xxxx", "client_version": "xxxx", "client_dir": "xxxx",                 "open_time": "1531447135", "status": "0",
        "qq_srv_id": "100", "srv_type": "1", "srv_farm_id": "0",
        "srv_farm_name": "default2", "unique_srv_id": "20001"
    }
]
```

*示例*
```python
def add_install_gameserver():
    """添加开服计划接口
    """

    url = 'https://cmdb.cy666.com/api_web/InstallGameServer.Create/'

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Token replace_token_here'
    }

    pdata = [
        {
            "project": "ssss", "area": "大陆", "pf_id": "178",
            "pf_name": "178pop", "srv_num": "256", "srv_name": "双线一服",
            "server_version": "xxxx", "client_version": "xxxx", "client_dir": "xxxx",                 "open_time": "1531447135", "status": "0",
            "qq_srv_id": "100", "srv_type": "1", "srv_farm_id": "0",
            "srv_farm_name": "default", "unique_srv_id": "20000"
        },
        {
            "project": "csxy", "area": "大陆", "pf_id": "70",
            "pf_name": "xinghuiorg", "srv_num": "1000", "srv_name": "测试一服",
            "server_version": "xxxx", "client_version": "xxxx", "client_dir": "xxxx",                 "open_time": "1531447135", "status": "0",
            "qq_srv_id": "100", "srv_type": "1", "srv_farm_id": "0",
            "srv_farm_name": "default2", "unique_srv_id": "20001"
        }
    ]

    r = requests.post(url, headers=headers, json=json.dumps(pdata))

    print(r.json())
```

*返回结果*

`{'message': '', 'status': 1, 'data': ''}`

*注意事项*

由于是批量增加多个开服计划，API如果在针对每个开服计划的创建过程中出现了异常，那么，本次所有的这一批开服计划都不能正确的添加到运维系统中。只有全部的开服计划都成功的创建，才代表这一批开服计划已经全部创建，才会**commit**。不然，运维系统会将本次的操作**rollback**





### 卸载区服（暂时弃用）

卸载一个或者多个区服

*接口地址*
- https://cmdb.cy666.com/api_web/InstallGameServer.Delete/

*HTTP请求方式*

- POST

*请求参数*

POST请求的时候将**list转为json**

```python
pdata = [
    {
        "project": "ssss", "area": "大陆", "pf_id": "178", srv_num": "256"
    },
    {
        "project": "csxy", "area": "大陆", "pf_name": "xinghuiorg", srv_num": "1000"
    }
]
```

根据**project**, **area**, **pf_id**, **srv_num**或者**project**, **area**, **pf_name**, **srv_num**这四个字段组成的联合索引可以获取到唯一的区服，API找到这些区服后会进行删除操作。全部的操作没有异常，就会**commit**，否则，本次操作就会**rollback**。

*示例*
```python
def delete_install_gameserver():
    """删除开服计划接口
    """

    url = 'https://cmdb.cy666.com/api_web/InstallGameServer.Delete/'

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Token replace_token_here'
    }

    pdata = [
        {
            "project": "ssss", "area": "大陆", "pf_id": "178", srv_num": "256"
        },
        {
            "project": "csxy", "area": "大陆", "pf_name": "xinghuiorg", srv_num": "1000"
        }
    ]

    r = requests.post(url, headers=headers, json=json.dumps(pdata))

    print(r.json())
```

*返回结果*

`{'message': '', 'status': 1, 'data': ''}`






### 修改一个或多个开服计划（暂时弃用）

这个接口用来修改**一个或者多个**区服的开服计划数据

*接口地址*
- https://cmdb.cy666.com/api_web/InstallGameServer.Modify/

*HTTP请求方式*

- POST

*能修改到的字段*
`'open_time', 'qq_srv_id', 'srv_type', 'srv_farm_id', 'srv_farm_name'`

*请求参数*
- filter_server: 字典，用来过滤出要修改的**一个或者多个区服**
- new_data: 字典，用来修改根据`filter_server`获取到的**一个或者多个区服**

`filter_server`是过滤区服的字段，你可以根据你想要过滤的区服，传入相应的数据来过滤出一个或者多个区服，这些都取决于你想要修改哪些满足`filter_server`条件的区服

```
pdata = [
            {
                'filter_server': {"project": "ssss", "area": "大陆", "pf_id": "178", "srv_num": "256"},
                "new_data": {'open_time': '1532424765'}
            },
            {
                'filter_server': {"project": "csxy", "area": "大陆", "pf_id": "90", "srv_num": "9000"},
                "new_data": {'srv_farm_name': 'defaultx'}
            },
        ]
```

*示例1*

修改`{"project": "ssss", "area": "大陆", "pf_id": "178", "srv_num": "256"}`的**开服时间**和`{"project": "csxy", "area": "大陆", "pf_id": "90", "srv_num": "9000"}`的**srv_farm_name**

```
def modify_install_gameserver():
    """修改开服计划
    """

    url = 'https://cmdb.cy666.com/api_web/InstallGameServer.Delete/'

    headers = {
        'Accept': 'application/json',
        'Content-type': 'application/json',
        'Authorization': 'Token replace_token_here'
    }

    pdata = [
        {
            'filter_server': {"project": "ssss", "area": "大陆", "pf_id": "178", "srv_num": "256"},
            "new_data": {'open_time': '1532424765'}
        },
        {
            'filter_server': {"project": "csxy", "area": "大陆", "pf_id": "90", "srv_num": "9000"},
            "new_data": {'srv_farm_name': 'defaultx'}
        },
    ]

    r = requests.post(url, headers=headers, json=pdata)

    print(r.json())
```

*返回结果*

`{'data': '', 'status': 1, 'message': 2}`

操作成功后,`status`为1， `message`返回本次修改了多少个区服

全部的操作没有异常，就会**commit**，否则，本次操作就会**rollback**。