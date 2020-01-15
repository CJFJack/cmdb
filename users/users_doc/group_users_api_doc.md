获取部门下所有用户API接口规范文档
=======================

该API用来获取CMDB所有用户的归属部门下的用户列表


API请求规范
----------------------

*接口地址*

- https://cmdb.cy666.com/api_user/group_users/

*HTTP请求方式*

- GET

*请求参数*
- 无

*示例*

1 使用curl

```
 curl -H 'Authorization: Token your_token' -k "https://cmdb.cy666.com/api_user/group_users/"
```

2 使用python requests

```
try:
    url = 'https://cmdb.cy666.com/api_user/group_users/'
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Token your_token'
    }

    r = requests.get(url, headers=headers, timeout=15, verify=False)
    print(r.json())
except Exception as e:
    pass
```

*返回结果*

```
{'resp': 0, 'reason': {'php研发部': {'houyongfeng@chuangyunet.com': ['wuweiqin', 'xiaweiqin', 'huangkaibo', 'xiaoqidun', 'tanluying']}, '管理层': {'zhengjiawei@chuangyunet.com': ['zhengjiawei']}, '商务2部': {'xuzhishang@chuangyunet.com': ['chenqiuxian', 'xuzhishang', 'wangshaowen']}, '手游前端技术部': {'zengxusheng@chuangyunet.com': ['hongliwen', 'hexin', 'zengxusheng', 'lize', 'zhangbin', 'wuzhenzhong', 'guohuo']}}}
```

reason的数据结构:
```
{
    "部门1": {"email1": ['staff1', 'staff2']},
    "部门2": {"email2": ['staff3', 'staff4']},
}
```

其中, `{'resp': 0}` 0代表操作成功， 1代表失败, `reason`里面是部门用户的list列表
