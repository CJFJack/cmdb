获取离职人员API接口
===========================

*接口地址*
- https://cmdb.cy666.com/api_clean_user/get_not_active_user/

*HTTP请求方式*
- GET

*示例*

```
url = 'https://cmdb.cy666.com/api_clean_user/get_not_active_user/'

headers = {
    'Accept': 'application/json',
    'Authorization': 'Token your_token'
}

r = requests.get(url, headers=headers)

print(r.json())
```

*返回结果*
`['yefayan', 'wangwen', 'yangjun', 'zoujiayi']`