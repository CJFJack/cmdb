获取项目的svn仓库信息API文档
=======================

该API用于获取CMDB项目信息的SVN仓库名

API请求规范
----------------------

*接口地址*

- https://cmdb.cy666.com/api_svn/project_svn/

*HTTP请求方式*

- GET

*请求参数*
- 无

*示例*

1 使用curl

```
 curl -H 'Authorization: Token your_token' -k "https://cmdb.cy666.com/api_svn/project_svn/"
```

2 使用python requests

```
try:
    url = 'https://cmdb.cy666.com/api_svn/project_svn/'
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Token c6e7724396561cfd9004718330fc8a6dcbaf6409'
    }

    r = requests.get(url, headers=headers, timeout=15, verify=False)
    print(r.json())
except Exception as e:
    pass
```

*返回结果*

```
{'reason': {'超神学院': {'tengwentao@chuangyunet.com': 'csxy'}, '校花的贴身高手': {'liuhongnian@chuangyunet.com': 'sysn'}, '网络管理项目': {'zhangwenhui@chuangyunet.com': 'sa'}, '三生2D手游': {'zhangshengjie@chuangyunet.com': 'syss2d'}, '手游少年3D': {'yangda@chuangyunet.com': '3dsn'}, '乱世龙魂': {'hezhilong@chuangyunet.com': 'sgqyz'}, '超神荣耀': {'tengwentao@chuangyunet.com': 'csry'}, '法务': {'lihuiqiong@chuangyunet.com': 'forensic'}, 'web后台项目': {'houyongfeng@chuangyunet.com': 'web'}, '少年群侠传': {'tangchunbin@chuangyunet.com': 'qqjy'}, '后端公共项目': {'houyongfeng@chuangyunet.com': 'server'}, '手游剑雨': {'caisiwei@chuangyunet.com': 'syjy'}, '手游前端2D引擎仓库': {'jieyulong@chaungyunet.com': 'client2dengine'}, '手游3D引擎': {'jieyulong@chaungyunet.com': 'cyengine3d'}, '猎人3D': {'lichao@chuangyunet.com': 'lr3d'}, '少年H5': {'tangchunbin@chuangyunet.com': 's7yy'}, '运营公共项目': {'chenfen@chuangyunet.com': 'yunying'}, '测试部门项目': {'yangkuan@chuangyunet.com': 'test'}, '三生3D手游': {'dingqianwei@chuangyunet.com': 'syss3d'}, 'UIUE规范库': {'chencaixia@chuangyunet.com': 'uiue'}, '三生三世': {'lichao@chuangyunet.com': 'ssss'}, 'OA信息化': {'yangxin@chuangyunet.com': 'oa_web'}, '机械纪元': {'zhangwenhui@chuangyunet.com': 'jxjy'}, '页游客户端文档项目': {'hezhilong@chuangyunet.com': 'client'}, '前端通用逻辑组件': {'zengxusheng@chuangyunet.com': 'commonlibs'}, '剑雨江湖': {'zhangshengjie@chuangyunet.com': 'jyjh'}, '热血群英传': {'hezhilong@chuangyunet.com': '3gh5'}, '雏蜂项目': {'tengwentao@chuangyunet.com': 'bee'}, '运维相关': {'zhangwenhui@chuangyunet.com': 'yunwei'}}, 'resp': 0}
```

reason的数据结构:
```
{
    "项目中文名1": {"项目负责人邮件1", "svn_repo1"},
    "项目中文名2": {"项目负责人邮件2", "svn_repo2"},
}
```

其中, `{'resp': 0}` 0代表操作成功， 1代表失败