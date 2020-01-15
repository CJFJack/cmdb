CMDB区服列表API接口规范
===========================

[TOC]


## 运维管理机状态api

###状态说明
- '0' 空闲
- '1' 装服     **运维管理机**可以修改
- '2' CMDB热更新     **CMDB**可以修改
- '3' 运维管理机热更新     **运维管理机**可以修改
- '4' 合服    **运维管理机**可以修改
- '5' 迁移    **运维管理机**可以修改
- '6' 版本更新    **运维管理机**可以修改
- '7' 关平台    **运维管理机**可以修改

根据**项目**和**地区**来修改一个或者多个运维管理机的状态

**end_time**可以传，如果传表示该操作的预估结束时间，如果不传，表示时间未知.

###修改例子
装服的过程中加锁:
`curl -H 'Authorization: Token your_token' -k "https://192.168.100.66/api/lockOpsManager?project=snqxsz&area=大陆&status=1&end_time=1502940820"`

返回结果:
`{"resp": 1, "reason": "ok"}`

装服完成以后修改解锁:
`curl -H 'Authorization: Token your_token' -k "https://192.168.100.66/api/unlockOpsManager?project=snqxz&area=大陆&status=1"`

返回结果:
`{"resp": 1, "reason": "ok"}`

###返回码
- 1 ok
- 12 游戏项目英文名不存在
- 11 内部未知错误
- 20 没有匹配到运维管理机
- 21 status状态错误 


## 说明
各个项目上需要将各自的区服列表汇总到CMDB中，用于以后的更新和相关的操作。接口全部采用http GET请求，返回码和返回结果查看每个api的相应的返回对照表

## 区服表字段说明

- **project_type** 游戏项目类型 整型字段
> 0手游  1页游

- **project** 游戏项目，关联到cmdb的项目
- **srv_status** 游戏服状态
> 0 正常 4 关闭平台 **默认是0**

- **room** 机房，关联到cmdb的机房

- **host** 主机，关联到cmdb的主机

- **game_type** 游戏类型  关联到区服类型表

- **pf_name** 平台名 字符串类型 比如*37， qq*

- **srv_id** 区服id  字符串类型 比如*liebao_10003*

- **srv_name** 区服名 字符串类型 比如*双线一服*

- **ip** 外网ip地址 字符串类型 比如*58.63.33.154*

- **merge_id** 合服id 关联到自身表的srv_id字段 **如果没有合服，为None, 默认是None**

- **merge_time** 合服时间 datetime类型 同上面的一样，**如果没有合服，为None, 默认是None**

- **client_version**  前端版本号 字符串类型

- **server_version** 后端版本号  字符串类型

- **cdn_root_url** CDN根路径  字符串类型

- **cdn_dir CDN**目录  字符串类型

- **open_time** 开服时间，时间戳，字符串类型

- **area_name** 游戏区域, 字符串类型

###说明
**project**, **srv_id**, **area_name**这三个字段联合唯一

## 1.1增加区服列表(增开新服后调用此接口)
*接口地址*

- https://cmdb.cy666.com/api/newSrvCallBack

*HTTP请求方式*

- GET

*请求参数*

| 参数名         | 是否必须  | 类型    |   例子              |  
| ----           | --------- | ------  |-------------------- |  
| project_type   |   是      | int     |      1              |  
| game           |   是      | string  |   snqxz(项目英文名) |  
| srv_status     |   否      | int     |  0(正常) 4(关闭平台)|  
| room           |   是      | string  |   qq云(机房名称)    |  
| host           |   是      | string  | snqxz_boke_10.1.1.1 |  
| game_type      |   是      | int     |      1              |  
| pf_name        |   是      | string  |      37             |  
| srv_id         |   是      | string  |      37_012         |  
| srv_name       |   是      | string  |      双线1服        |  
| ip             |   是      | string  |      192.168.1.1    |  
| client_version |   是      | string  |      0001311        |  
| server_version |   是      | string  |      1937133        |  
| cdn_root_url   |   是      | string  |res.qxz.zhi-ming.com |  
| cdn_dir        |   是      | string  |       qq_s1         |  
| merge_id       |   否      | string  |       37_010        |  
| merge_time     |   否      | string  |时间戳(1381419600)   |  
| open_time      |   是      | string  |时间戳(1381419600)   |  
| area_name      |   是      | string  |         大陆        |  

*示例*
新增一个游戏服，没有合服
```
curl -H 'Authorization: Token YOU_TOKEN' -k "https://cmdb.cy666.com/api/newSrvCallBack?project_type=1&game=snqxz&game_type=1&pf_name=37&srv_id=37_012&srv_name=双线1服&ip=192.168.1.1&client_version=0001311&server_version=1937133&cdn_root_url=res.qxz.zhi-ming.com&cdn_dir=qq_s1&room=qq机房&host=snqxz_boke_10.1.1.1&open_time=1381419600&area_name=大陆"
```

返回结果:
`{"resp": 1, "reason": "ok", "count": 1}`



新增一个游戏服，带合服id和合服时间**通常用于第一次添加过来使用**
```
curl -H 'Authorization: Token YOU_TOKEN' -k "https://cmdb.cy666.com/api/newSrvCallBack?project_type=1&game=snqxz&game_type=1&pf_name=37&srv_id=37_013&srv_name=双线1服&ip=192.168.1.2&client_version=0001311&server_version=1937133&cdn_root_url=res.qxz.zhi-ming.com&cdn_dir=qq_s1&merge_id=37_012&merge_time=1381419600&room=qq机房&host=snqxz_boke_10.1.1.1&open_time=1381419600&area_name=大陆"
```

返回结果:
`{"resp": 1, "reason": "ok", "count": 1}`

#####返回码对照表
| resp  | reason               |
| ----  | -----------------    |
| 1     |  操作成功            |  
| 4     |  参数传递错误        |  
| 14    |  主服id不存在        |  
| 12    |  游戏项目英文名不存在|  
| 13    |  区服id记录有重复    |  
| 11    |  API内部错误         |  
| 15    |  机房名不存在        |  
| 16    |  游戏服不唯一        |  


##1.2 更新服务器参数配置（前端更新）接口（页游）
根据游戏和cdn_root_url和cdn_dir来更新前端版本号

*查询参数*
- game
- cdn_root_url
- cdn_dir
- area_name

*更新参数*
-client_ver

*接口地址*

- https://cmdb.cy666.com/api/updateClientPara

*HTTP请求方式*

- GET

*请求参数*

| 参数名         | 是否必须  | 类型    |   例子                |  
| ----           | --------- | ------  |--------------------   |  
| game           |   是      | string  |   jyjh(项目英文名)    |  
| area_name      |   是      | string  |   大陆                |  
| cdn_root_url   |   是      | string  |  cdn8.jyjh.yaowan.com |  
| cdn_dir        |   是      | string  |      qq_r1            |  
| client_ver     |   是      | string  |  new_client_version   |  

*示例*
`curl -H 'Authorization: Token your_token' -k "https://cmdb.cy666.com/api/updateClientPara?game=jyjh&client_ver=a_new_version34&cdn_root_url=cdn8.jyjh.yaowan.com&cdn_dir=qq_s1&area_name=大陆"`

返回结果
`{"resp": 1, "reason": "", "count": 51}`

#####返回码对照表
| resp  | reason               |
| ----  | -----------------    |
| 1     |  操作成功            |  
| 4     |  参数传递错误        |  
| 8     |  游戏服找不到        |  
| 12    |  游戏项目英文名不存在|  
| 11    |  API内部错误         |  


##1.3 更新服务器参数配置（后端更新）接口（页游）
###1.3.1 GET请求
*查询参数*
- game
- area_name
- pf_select_type
- pf_list
- srv_select_type
- srv_list
- old_version_no

*更新参数*
-server_ver

*接口地址*

- https://cmdb.cy666.com/api/updateSrvPara

*HTTP请求方式*

- GET

*示例*
1 更新剑雨江湖所有平台的后端版本
`curl -H 'Authorization: Token your_token' -k "http://cmdb.cy666.com/api/updateSrvPara?game=jyjh&pf_select_type=all&server_ver=001server&area_name=大陆"`

2 更新剑雨江湖lmqq平台的后端版本
`curl -H 'Authorization: Token your_token' -k "http://cmdb.cy666.com/api/updateSrvPara?game=jyjh&pf_select_type=include&pf_list=lmqq&server_ver=002server&area_name=大陆"`

###1.3.2 POST请求
*查询参数*
- game
- area_name
- srv_list

*更新参数*
-server_ver

*接口地址*

- https://cmdb.cy666.com/api/updateSrvPara

*HTTP请求方式*

- POST

*示例*
**更新剑雨江湖台湾地区区服id为gm99_1,gm99_2,gm99_6这三个服的后端版本为2333**
`curl -X POST -k http://cmdb.cy666.com/api/updateSrvPara -H 'Authorization: Token your_token' -H 'Content-Type: application/json' -d '{"game": "jyjh", "server_ver": "2333", "area_name": "台湾", "srv_list": "gm99_1,gm99_2,gm99_6"}'`

返回结果
`{"reason": "ok", "count": 3, "resp": 1}`


#####返回码对照表
| resp  | reason               |
| ----  | -----------------    |
| 1     |  操作成功            |  
| 4     |  参数传递错误        |  
| 12    |  游戏项目英文名不存在|  
| 11    |  API内部错误         |  

## 1.4 删除某个服的数据接口
*查询参数*
- game
- srv_id
- area_name

*接口地址*

- https://cmdb.cy666.com/api/delSrvRelateInfo

*HTTP请求方式*

- GET

*示例*
`curl -H 'Authorization: Token your_token' -k "http://cmdb.cy666.com/api/delSrvRelateInfo?game=jyjh&srv_id=ywqq_113&area_name=大陆"`

#####返回码对照表
| resp  | reason               |
| ----  | -----------------    |
| 1     |  操作成功            |  
| 4     |  参数传递错误        |  
| 14    |  游戏服没有找到      |  
| 16    |  游戏服不唯一        |  
| 12    |  游戏项目英文名不存在|  
| 11    |  API内部错误         |  

## 1.5 修改服务器相关信息接口
修改单个服

*查询参数*
- game
- srv_id
- area_name

*更新参数*
- srv_status    可选
- ip    可选
- cdn_root_url    绑定#1
- cdn_dir    绑定#1
- client_version    绑定#1
- room    可选 机房名称
- game_type    可选 区服类型代号
- host    可选  主机唯一标识符
- pf_name    可选
- srv_name    可选
- server_version    可选
- merge_id    可选
- merge_time    时间戳，可选
- open_time    时间戳，可选

*接口地址*

- https://cmdb.cy666.com/api/modifySrvRelateInfo

*HTTP请求方式*

- GET

*关闭平台后调用接口修改区服状态为关闭平台*
`curl -H 'Authorization: Token your_token' -k "http://cmdb.cy666.com/api/modifySrvRelateInfo?game=jyjh&pf_name=ywqq&srv_id=ywqq_113&area_name=大陆&srv_status=4`

*示例*
`curl -H 'Authorization: Token your_token' -k "http://cmdb.cy666.com/api/modifySrvRelateInfo?game=jyjh&pf_name=ywqq&srv_id=ywqq_113&area_name=大陆&ip=192.168.1.1`

`curl -H 'Authorization: Token your_token' -k "http://cmdb.cy666.com/api/modifySrvRelateInfo?game=jyjh&pf_name=lmqq&srv_id=lmqq_109&area_name=大陆&ip=192.168.1.1&cdn_root_url=cdn.jyjh.yaowan.com&cdn_dir=qq_r2&client_version=0001client`

**说明**
如果要修改某个区服的合服id为空,也就是把该服有被合服改为未合服的情况，只需要传递**merge_id**为**数字0**即可，merge_time不需要传递，会自动设置为None值.

例如:
剑雨江湖越南地区vng_150服原来的合服id是vng_140，现在要把vng_150设置为没有合服，也就是主服的情况,只需要设置merge_id为0即可
` curl -H 'Authorization: Token your_token' -k "http://cmdb.cy666.com/api/modifySrvRelateInfo?game=jyjh&srv_id=vng_150&area_name=越南&merge_id=0"`

#####返回码对照表
| resp  | reason               |
| ----  | -----------------    |
| 1     |  操作成功            |  
| 4     |  参数传递错误        |  
| 14    |  游戏服没有找到      |  
| 16    |  游戏服不唯一        |  
| 12    |  游戏项目英文名不存在|  
| 11    |  API内部错误         |  
| 20    |  区服类型没有找到    |  


## 1.6 根据条件批量修改cdn地址接口
*查询参数*
- game
- area_name
- old_cdn_root_url    绑定#1
- old_cdn_dir    绑定#1
- srv_list

*更新参数*
- new_cdn_root_url
- new_cdn_dir
- client_version

**说明**
old_cdn_root_url, old_cdn_dir和srv_list为互斥的关系，每次请求过来只能传一个，如果都传，则会以**old_cdn_root_url,old_cdn_dir**作为过滤的条件，srv_list的参数将会忽略

*接口地址*

- https://cmdb.cy666.com/api/batchModifyCdn

*HTTP请求方式*

- GET

*示例*
根据old_cdn_root_url和old_cdn_dir过滤
`curl -H 'Authorization: Token your_token' -k "http://cmdb.cy666.com/api/batchModifyCdn?game=jyjh&area_name=大陆&old_cdn_root_url=cdn6.jyjh.yaowan.com&old_cdn_dir=qq_r1&new_cdn_root_url=cdn7.jyjh.yaowan.com&new_cdn_dir=qq_r1&client_version=new_client_version"`

根据srv_list过滤
`curl -H 'Authorization: Token your_token' -k "http://cmdb.cy666.com/api/batchModifyCdn?game=jyjh&area_name=大陆&srv_list=qq_1,qq_2&new_cdn_root_url=cdn7.jyjh.yaowan.com&new_cdn_dir=qq_r1&client_version=new_client_version"`

#####返回码对照表
| resp  | reason               |
| ----  | -----------------    |
| 1     |  操作成功            |  
| 4     |  参数传递错误        |  
| 19    |  解析cdn出错         |  
| 12    |  游戏项目英文名不存在|  
| 11    |  API内部错误         |  


## 1.7合服完成回调接口
*查询参数*
- game
- srv_id
- merge_id
- merge_time
- area_name

将查询得到的唯一srv_id指向主服merge_id查询得到的唯一主服

*接口地址*

- https://cmdb.cy666.com/api/mergeSrvCallBack

*HTTP请求方式*

- GET

*示例*
`curl -H 'Authorization: Token your_token' -k "http://cmdb.cy666.com/api/mergeSrvCallBack?game=jyjh&merge_id=ywqq_1&merge_time=1502790997&srv_id=ywqq_145&area_name=大陆`

#####返回码对照表
| resp  | reason               |
| ----  | -----------------    |
| 1     |  操作成功            |  
| 4     |  参数传递错误        |   
| 12    |  游戏项目英文名不存在|  
| 14    |  游戏服没有找到      |  
| 16    |  游戏服不唯一        |  
| 11    |  API内部错误         |  

## 1.7 查询区服列表接口

该接口通过查找，返回区服列表的srv_id 列表

**CMDB只会返回状态是正常，并且没有合服的区服**

*接口地址*

- https://cmdb.cy666.com/api/gameservers

*HTTP请求方式*

- GET

*示例*

查找剑雨江湖大陆YY的所有区服
`curl -H 'Authorization: Token your_token' -k "https://cmdb.cy666.com/api/gameservers?project=jyjh&area_name=大陆YY"`

##### 返回结果
```
{"resp": 1, "reason": ["2144_1", "2144_228", "2144_629", "2144_814", "2144_818", "2144_819", "2217_1", "2217_236", "2217_361", "2345_1", "2345_135", "2345_282", "2345_327", "2345_419", "2345_437", "2345_441", "2345_444", "2345_448", "2345_449", "2345_450", ..... ], "count": 654
```
