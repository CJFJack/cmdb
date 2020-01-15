服务器权限申请使用文档
=========================== 

[TOC]

开发人员想要登录公司的服务器，需要申请相应的权限，权限具有时效性，分为永久权限和临时权限(最长时间为一个月),经过各个环节审批完成后，运维部会处理你的服务器权限申请请求，并且告知处理结果。

### key的格式要求

标准的key格式:

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC+tHc4hZ56FVbGp2Q72n7godyzIEu26Q84C8AhdtkBc6aMkMi05NeAgZu5nck7m5gsDQH7nA/A/P11m2XPjbEsYzjILAitSMfz74iyQCl2PTlTcAwSQR0KwhitMERK5dSOCINU29TnVXSrgBlLrTkpykIaBG5uvAl17sDw6zLwq57jV6hm9407NuV1Ok8GfIn26AdWUGQX5qZkTT4ULwrIuwYJ47rdh28s1JsNC6vK0dKsQn5CJ1emzJEFhUzQH1LLnH3CumAtpk9sC7Vd9KDHT4TB2nwVFmu+IMjPGfNaTJIhj9BLLTcrUav82afrv6A4FFGWVUmRd+SCnMlVJ6o7 yanwenchi
```

第一段 `ssh-rsa` 说明key的生成算法
中间段 `AAAA....6o7` 说明key的内容
最后一段 `yanwenchi` 说明key的备注

**要求最后一段内容和你的cmdb上的拼音名相同**，不然系统会提示key的格式不对。
这么做是统一规范好各个key

申请的服务器可以从两种情况下获取：
>根据服务器的IP
>根据游戏服，比如剑雨江湖qq1服来找到该服务器

### 根据服务器IP

根据IP添加多个服务器:

![根据IP添加多个服务器](http://192.168.100.66/workflow_doc/serper_ip.png "根据IP添加多个服务器")

### 根据游戏服

根据游戏服添加多个服务器

![根据游戏服添加多个服务器](http://192.168.100.66/workflow_doc/serper_game.png "根据游戏服添加多个服务器")