服务器权限接口文档
===========================

[TOC]

## 删除用户某个机器的永久服务器权限
删除用户某个机器的永久服务器权限，cmdb会将该用户的该机器权限设置为过期

- 请求方法: http GET
- 请求url: https://cmdb.cy666.com/api/delUserHost

### 请求参数
- username 用户拼音 字符串
- host 主机标识符(通过主机标识符找到唯一的主机匹配) 字符串

### 示例

删除用户`qiuyiming`的主机标识符为`jyjh_vng_172.16.11.15`的**永久**服务器权限:

`curl -X GET 'http://192.168.56.101/api/delUserHost?username=qiuyiming&host=jyjh_vng_172.16.11.15' -H 'Authorization: Token c6e7724396561cfd9004718330fc8a6dcbaf6409'`

返回结果:
`{"success": true, "msg": ""}`

## 添加服务器权限
- 请求方法：http GET
- 请求url: https://cmdb.cy666.com/api/addUserHost

### 请求参数
- username 用户拼音 字符串
- host 主机标识符(通过主机标识符找到唯一的主机匹配) 字符串
- temporary 临时或者永久权限
> 0永久 1临时
- start_time 开始时间(**使用时间戳**)  字符串
- end_time 结束时间(**使用时间戳**) 字符串
- is_root 是否root
> 0普通用户 1root用户

### 关于临时和永久权限
- 如果**temporary**为*0*，也就是**永久权限**，可以不传**start_time**和**end_time**参数，如果传了，也没有关系，系统会将这两个参数设置为**None**
- 如果**temporary**为*1*, 也就是**临时权限**, 需要传递**start_time**和**end_time**参数，不然会提示需要这两个时间参数，并且返回False


### 示例
添加一个永久权限的记录, 这里没有把*start_time*和*end_time*传递过去
`curl -X GET -k 'https://cmdb.cy666.com/api/addUserHost?username=yanwenchi&host=chuangyu_fszhc_14.17.103.21&temporary=0&is_root=0' -H 'Authorization: Token you_token'`

返回结果:
`{"success": true, "msg": ""}`


添加一个临时权限的记录，这里需要传递*start_time*和*end_time*参数
`curl -X GET -k 'https://cmdb.cy666.com/api/addUserHost?username=yanwenchi&host=chuangyu_fszhc_14.17.103.21&temporary=1&is_root=0&start_time=1375063206.926&end_time=1375099591.118' -H 'Authorization: Token you_token' `

返回结果:
`{"success": true, "msg": ""}`
