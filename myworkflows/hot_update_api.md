热更新API文档
=========================== 

这篇文档详细介绍了热更新的流程以及CMDB系统和运维管理机系统的数据交互API方式，以及对接新的项目热更新需要配置的地方和注意事项。

[TOC]

## 热更新流程
整个热更新的流程如下图所示
![热更新流程图](https://ws1.sinaimg.cn/large/005B3DIrgy1fljoreinw7j30p50hwdh3.jpg "热更新流程图")

### 前端页面如何获取版本接收机的热更新目录文件?
每次进入到热更新页面，前端js会生成一个uuid，选择了项目和地区(比如三生三世， 大陆-cn)以及版本号以后，点击获取文件列表时，页面发送一个请求到cmdb，接着cmdb根据项目和地区以及本次的uuid会给改项目对应的版本接收机的**celery file-pull-worker** 发送拷贝整个版本号的目录到一个新的地方。

*对于后端热更新，这里以三生三世大陆版本号为004200000为例:*
在192.168.40.8上，相当于执行了如下命令
`cp -r /data/version_update/server/ssss/cn/004200000/reloadfiles /data/hot_backup/hot_server/ssss/cn/350cf0ef-c12e-4bcc-d0df-369a09a4a357/004200000`

需要注意的是/data/version_update/server/ssss 这里的**ssss**的目录是链接到原目录**x**

相当于`ln -s /data/version_update/server/x /data/version_update/server/ssss`
**ssss**对应三生三世游戏项目在cmdb中的英文名。

### cmdb和运维管理机执行热更新流程
 - 1 CMDB对通过项目和版本接收机的配置文件，找到改项目对应的版本接收机的地址，然后对版本接收机的**celery file-push-worker** 发送推送热更新文件的命令
 - 相应的版本接收机收到执行热更新文件推送命令后，推送热更新文件到对应的机器中(需要cmdb配置好项目的rsync地址以及版本接收机写好rsync的密码文件和600权限的问题)
 - 2 版本接收机推送文件成功后调用cmdb的API接口告诉cmdb文件推送成功，可以进行下一步
 - 3 cmdb收到API推送文件成功的请求后，调用运维管理机的API接口，发送命令让运维管理机执行热更新命令
 - 4 运维管理机收到cmdb的热更新请求后，调用本地的celery worker异步执行热更新命令，然后调用cmdb的接口告诉运维管理机已经开始执行
 - 5 运维管理机celery worker执行热更新完成以后，再一次调用cmdb的接口，通知cmdb本次热更新执行完成

 
## CMDB和运维管理机的API数据交互内容和格式

### 前端热更新

CMDB发送如下数据格式给运维管理机
```
{
    'ops_manager': 1,
    'update_type': 'hot_client',
    'client_type': 0 or 1,
    'data': [
        {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 't1'},
        {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'test_r1'},
        {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 's1'},
        {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'r1'}
    ],
    'uuid': 'xxx', 'version': '003100000',
    'update_file_list': [
        {'file_name': 'a.txt', 'file_md5': abe347d3fdff45f1078102c4637852a5},
        {'file_name': 'b.txt', 'file_md5': 5724c05c650550ac8034129ad7a4d915}
    ]
}
```

更新完成后，运维管理机发送如下数据格式给cmdb
```
{
    'update_type': 'hot_client',
    'data': [
        {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 't1', 'status': True},
        {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'test_r1', 'status': True},
        {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 's1', 'status': True},
        {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 'r1', 'status': False}
    ],
    'uuid': 'xxx',
    'version': '003100000'
}
```

### 后端热更新

CMDB发送如下数据格式给运维管理机
```
{
    'update_type': 'hot_client',
    'update_server_list': {
        "game": {
            "10.1.1.1": ['qq_1', 'qq_2'],
            "10.1.1.2": ['qq_3', 'qq_4'],
        },
        "cross": {
            "192.168.1.1": ['cross_1', 'corss_2'],
            "192.168.1.3": ['cross_3', 'corss_4'],
        },
        "cross_center": {
            "172.17.26.12": ['center_1', 'center_2'],
            "172.17.26.15": ['center_4', 'center_6'],
        }
    },
    'uuid': 'xxx',
    'version': '003100000',
    'update_file_list': [
        {'file_name': 'a.txt', 'file_md5': abe347d3fdff45f1078102c4637852a5},
        {'file_name': 'b.txt', 'file_md5': 5724c05c650550ac8034129ad7a4d915}
    ]
    'erlang_cmd_list': ['erlang_cmd1', 'erlang_cmd2']
}

```

由于一个IP上会有多个游戏服，管理机在每个IP执行完成后，会调用一次API接口告诉该IP的游戏服热更新情况，同时cmdb更新该IP上的游戏服热更新数据。当所有的IP都执行完成后，运维管理机会最后一次调用cmdb的API接口，告诉本次所有的后端热更新的游戏服以及更新完成。

基于单个IP的运维管理机发送给cmdb的数据格式
```
{
    "ip": {
        "10.1.1.1": {
            "update_data": {
                "qq_1": {"data": "更新失败,不执行erl命令", "status": False},
                "qq_2": {"data": "更新失败,不执行erl命令", "status": False},
            },
            "erl_data": {
                "qq_1": {"data": "更新失败,不执行erl命令", "status": False},
                "qq_2": {"data": "更新失败,不执行erl命令", "status": False},
            }
        }
    },
    "uuid": 'xxxx',
    "update_type": "hot_server",
    "version": 'xxxxx',
}
```

所有的游戏服热更新完成以后最后一次发送给cmdb的数据格式
```
{
    "final_result": True,
    "final_data": "全部完成",
    "uuid": 'xxxx',
    "update_type": "hot_server",
    "version": 'xxxxx',
}
```


## 热更新对接新项目需要配置的地方

### cmdb需要配置的地方
 - 地区对应的英文名，一个地区可能会对应多个英文名(大陆-cn, cn_new)，在cmdb的rsync.py的配置文件中
 ```
 RSYNC_MAP = {
    'ssss': {
        'hot_client': {
            '大陆': ['cn'],
        },
        'hot_server': {
            '大陆': ['cn'],
        }
    },
    'snqxz': {
        'hot_client': {
            '大陆': ['cn'],
            '台湾': ['tw'],
            '越南': ['vn'],
        },
        'hot_server': {
            '大陆': ['cn'],
            '台湾': ['tw'],
            '越南': ['vn'],
        }
    }
 }
 ```
 - rsync推送的配置文件，在rsync.py的配置文件中
 ```
 RSYNC_MANAGERS = [
    {
        "project": "ssss", "area": "大陆", "ip": "123.207.124.150",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/ssss.password", "port": 10022
    },
    {
        "project": "snqxz", "area": "台湾", "ip": "203.66.5.37",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/snqxz_taiwan.password", "port": 10022
    },
    {
        "project": "snqxz", "area": "越南", "ip": "122.201.11.130",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/snqxz_yuenan.password", "port": 10022
    },
    {
        "project": "snqxz", "area": "大陆", "ip": "122.227.23.166",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/snqxz_dalu.password", "port": 10022
    }
 ]
 ```
 - 热更新文件拉取和推送的配置 在rsync.py的配置文件中
 ```
 # 项目英文名到celery任务队列的对应关系
 PROJECT_CELERY_QUEUE_MAP = {
     'file_push8': ['jyjh', 'snqxz', 'ssss', 'csxy'],
 }
 ```


### 版本接收机需要配置的地方
 - 部署file-pull-worker 和file-push-worker这两个celery
 - 配置好该版本接收机上游戏项目对应的rsync密码文件，并且**600权限**
 - 如果版本目录不是和cmdb项目的英文名称相同，需要创建一个软连接
 `ln -s /data/version_update/server/x /data/version_update/server/ssss`


### 运维管理机需要配置的地方
 - cmdb推送热更新文件的rsync模块配置(需要同步告诉cmdb)



