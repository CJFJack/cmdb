# cmdb热更新对接新项目
<br/>
### 1. cmdb添加项目数据
https://cmdb.cy666.com/assets/game_project_list/

### 2. cmdb添加项目相关主机、运维管理机、区服数据
https://cmdb.cy666.com/assets/hostAPI/

https://cmdb.cy666.com/assets/ops_manager_list/

https://cmdb.cy666.com/myworkflows/game_server_list_api/

### 3. 热更新模板
进入“游戏项目管理 - 项目列表 ”，找到对应项目，点击“热更新模板”，选中所需前端或者后端热更新模板（模板图片可以向左向右翻滚），最后点击“保存”

PS：若现有模板不能满足项目需求，请联系运维开发添加

<strong>以下为运维开发注意事项</strong>：

- 我的申请页面、申请工单汇总页面
  - 前端：默认使用 common_client_hot_update_myworkflow.html 作为申请页模板，如果需要特殊处理，则新建 项目英文名+_client_hot_update_myworkflow.html 做修改
  - 后端：默认使用 common_server_hot_update_myworkflow.html 作为申请页模板，如果需要特殊处理，则新建 项目英文名+_server_hot_update_myworkflow.html 做修改

- 审批页面
  - 前端：默认使用 common_client_hot_update_workflow_approve.html 作为申请页模板，如果需要特殊处理，则新建 项目英文名+_client_hot_update_workflow_approve.html 做修改
  - 后端：默认使用 common_server_hot_update_workflow_approve.html 作为申请页模板，如果需要特殊处理，则新建 项目英文名+_server_hot_update_workflow_approve.html 做修改

### 4.cmdb 通过web获取cdn目录接口信息设置

https://cmdb.cy666.com/webapi/web_get_cdn_list_api/

### 5. cmdb编辑项目与celery queue的对应关系（拉取、推送更新文件）

https://cmdb.cy666.com/myworkflows/project_celery_queue_map/

PS：

1. 若项目热更新不涉及cmdb触发拉取或者推送更新文件的操作，则不需要添加

2. 如果项目使用新的celery worker拉取和推送更新文件，则需要将新的celery queue名称和tasks.py使用的函数名（包括推送和拉取）通知运维开发进行配置

   相关配置在celeryconfig.py中添加相应配置，tasks.py中也需要添加相应celery执行拉取和推送任务的函数

3. 相关配置在celeryconfig.py中添加相应配置，tasks.py中也需要添加相应celery执行拉取和推送任务的函数

### 6. cmdb配置运维管理机的rsync信息、是否启用代理等

https://cmdb.cy666.com/assets/ops_manager_list/

PS：若项目热更新不涉及cmdb触发拉取或者推送更新文件的操作，则不需要配置

### 7. 修改tasks.py中的do_hot_update函数
运维开发注意事项：根据热更新类型（前、后端）及不同项目，需要选择是否需要使用rsync推送更新文件，如果需要推送则不用修改