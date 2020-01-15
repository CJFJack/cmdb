# -*- encoding: utf-8 -*-
from myworkflows.utils import *
from myworkflows.models import *
from myworkflows.views import failure_declare_finish
from myworkflows.views import get_yl_network_administrator
from myworkflows.views import get_machine_administrator
from django.contrib.auth.models import User
from tasks import *
from cmdb.logs import WXMsgReceiveLog
from api_wechat.wx_callback_whitelist import wx_whitelist_ip
import operator


def get_yl_network_administrator(first_name=False):
    """获取原力网络管理员"""
    yl_network_administrator = SpecialUserParamConfig.objects.filter(param='YL_NETWORK_ADMINISTRATOR')
    if yl_network_administrator:
        if first_name:
            yl_network_administrator = yl_network_administrator[0].get_user_first_name_list()
        else:
            yl_network_administrator = yl_network_administrator[0].get_user_list()
    else:
        yl_network_administrator = []
    return yl_network_administrator


def get_wx_callback_ip():
    """获取微信服务器回调cmdb的服务器IP"""
    success = True
    msg = 'ok'
    try:
        token = check_valid_wx_token()
        if token is None:
            result = get_weixin_api_token()
            if result['success']:
                token = result['data']
            else:
                return {'success': False, 'msg': result['msg']}

        url = 'https://qyapi.weixin.qq.com/cgi-bin/getcallbackip?access_token=' + token

        r = requests.get(url)
        if r.status_code == 200:
            res = r.json()
            msg = res['ip_list']
            """对比"""
            eq = operator.eq(msg, wx_whitelist_ip)
            if not eq:
                send_weixin_message.delay(touser='chenjiefeng', content='微信服务器白名单IP发生变化！')
        else:
            raise Exception(str(r.status_code))
    except Exception as e:
        success = False
        msg = str(e)
    finally:
        return {'success': success, 'msg': msg}


def workflow_approve_receive_wx_callback(task_id, event_key, from_user):
    """
    根据收到的微信回调信息，审批工单
    1.根据 task_id 提取到 wse_id
    2.根据 event_key 获取审批结果
    3.根据 from_user 获取审批人
    4.根据 wse_id，event_key，from_user 将工单流程进入下一个节点
    5.如果工单审批后到达最后一个节点：完成，则采取相应的操作
    """
    log = WXMsgReceiveLog()
    wse_log = WorkflowApproveLog()
    try:
        wse_id = task_id.split('-')[1]
        wse = WorkflowStateEvent.objects.get(pk=wse_id)
        user = User.objects.get(first_name=from_user)
        if event_key == 'yes':
            transition = wse.state.transition.get(condition='同意')
        elif event_key == 'no':
            transition = wse.state.transition.get(condition='拒绝')
        else:
            raise Exception('未知的审批选项{}'.format(event_key))

        # 获取本轮审批有权限审批的user object列表
        approve_user_list = [u for u in wse.users.all()]
        # 转化流程状态
        wse_log.logger.info(
            '第1节点： 审批人：{}，审批意见：{}，工单标题：{}，wse_id：{}，is_current：{}'.format(user.username, transition.condition,
                                                                          wse.title, wse.id, wse.is_current))
        msg, success, new_wse = do_transition(wse, transition, user)
        wse_log.logger.info(
            '第8节点： 审批人：{}，审批意见：{}，工单标题：{}，wse_id：{}，is_current：{}'.format(user.username, transition.condition,
                                                                          wse.title, wse.id, wse.is_current))

        # 如果审批成功
        if success:
            # 审批完成后更新企业微信任务卡片按钮状态
            touser = [u.first_name for u in wse.users.all()]
            if touser:
                update_wx_taskcard_status(touser, wse)
                wse_log.logger.info(
                    '第9节点： 审批人：{}，审批意见：{}，工单标题：{}，wse_id：{}，is_current：{}'.format(user.username, transition.condition,
                                                                                  wse.title, wse.id, wse.is_current))

            # 从审批人列表中排除当前审批人
            approve_user_list.remove(user)
            # 如果前一审批节点有多个审批人，则把最新审批结果通知到除当前审批人之外的审批人
            if approve_user_list:
                # 邮件通知
                to_list = [x.email for x in approve_user_list]
                subject = wse.content_object.title + '#审批结果'
                content = '你的小伙伴： {}，已经 {} 工单申请#{}'.format(user.username, transition.condition,
                                                           wse.content_object.title)
                # print(to_list, subject, content)
                send_mail.delay(to_list, subject, content)
                # 都要发送qq弹框提醒
                users = ','.join([x.first_name for x in approve_user_list])
                send_qq.delay(users, subject, subject, content, '')
                # 发送wx弹框提醒
                wx_users = '|'.join([x.first_name for x in approve_user_list])
                send_weixin_message.delay(touser=wx_users, content=content)

            # 批完成后把sor中的users审批用户复制到wse的users审批用户中
            sor = get_sor(new_wse.state, new_wse.content_object)
            if sor:
                users = tuple(sor.users.all())
                new_wse.users.add(*users)

            if transition.condition == '同意':
                wse_users = new_wse.users.all()

                if wse_users:
                    if isinstance(new_wse.content_object, ClientHotUpdate) or \
                            isinstance(new_wse.content_object, ServerHotUpdate):
                        # 邮件通知
                        to_list = [x.email for x in wse_users if not x.profile.hot_update_email_approve]
                        if to_list:
                            subject, content = make_email_notify(True)
                            send_mail.delay(to_list, subject, content)

                        # 邮件审批
                        approve_list = [x.email for x in wse_users if x.profile.hot_update_email_approve]
                        if approve_list:
                            subject, content = make_email(new_wse)
                            send_mail.delay(approve_list, subject, content)

                    # wifi工单达到运维后发送给网络管理员
                    elif isinstance(new_wse.content_object, Wifi) and new_wse.state.name == '运维':
                        users = ','.join(
                            [x.first_name for x in User.objects.filter(username__in=get_yl_network_administrator()) if
                             x.is_active])
                        wx_users = '|'.join(
                            [x.first_name for x in User.objects.filter(username__in=get_yl_network_administrator()) if
                             x.is_active])
                        if users:
                            send_qq.delay(users, '你有一个wifi申请或网络问题申报工单需要处理', '你有一个wifi申请或网络问题申报工单需要处理',
                                          '链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)',
                                          'http://192.168.100.66/myworkflows/approve_list/')
                        # send_weixin_message.delay(touser=wx_users,
                        #                           content='你有一个wifi申请或网络问题申报工单需要处理' + '链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)' +
                        #                                   'http://192.168.100.66/myworkflows/approve_list/')

                    else:
                        # 邮件通知
                        subject, content = make_email_notify(True)
                        to_list = [x.email for x in wse_users]
                        if to_list:
                            send_mail.delay(to_list, subject, content)

                        # 都要发送qq弹框和wechat消息提醒
                        users = ','.join([x.first_name for x in wse_users])
                        wx_users = '|'.join(
                            [x.first_name for x in wse_users if not x.organizationmptt_set.first().wechat_approve])
                        data = get_qq_notify()
                        if users:
                            send_qq.delay(
                                users, data['window_title'], data['tips_title'], data['tips_content'],
                                data['tips_url'])
                        # 如果是版本更新单，就发送微信文字提醒
                        if isinstance(new_wse.content_object, VersionUpdate):
                            if wx_users:
                                data = get_wx_notify()
                                send_weixin_message.delay(touser=wx_users, content=data)

                    # 如果不是版本更新单，发送企业微信审批
                    if not isinstance(new_wse.content_object, VersionUpdate):
                        touser = '|'.join(
                            [u.first_name for u in wse_users if u.organizationmptt_set.first().wechat_approve])
                        if touser:
                            result = get_wx_task_card_data(touser, new_wse)
                            if result['success']:
                                send_task_card_to_wx_user.delay(touser, result['data'])

                else:
                    # 自动执行前端热更新
                    if isinstance(new_wse.content_object, ClientHotUpdate) and new_wse.state.name == '完成':
                        # 工单完成以后，修改工单的状态
                        content_object = new_wse.content_object
                        content_object.status = '4'
                        content_object.save()
                        ws_notify()

                        # 如果当前项目和地区没有锁，则找到下一个更新去执行
                        status_list = [x.ops.status for x in
                                       content_object.clienthotupdatersynctask_set.all()]
                        if len(list(set(status_list))) == 1 and '0' in status_list:
                            # do_hot_client.delay(new_wse.id)
                            msg, next_hot_update = get_next_hot_update(
                                content_object.project, content_object.area_name)
                            if next_hot_update:
                                if next_hot_update.status == '4':
                                    do_hot_update(next_hot_update)
                            else:
                                """更新任务没有自动执行原因字段"""
                                content_object.no_auto_execute_reason = msg
                                content_object.save(update_fields=['no_auto_execute_reason'])
                                # 发送邮件告警
                                # to_list = [x.email for x in content_object.project.related_user.all()]
                                to_list = list(set([x.email for x in content_object.project.get_relate_role_user()]))
                                subject = '热更新审批完成后没有自动执行'
                                content = '项目:{} 地区:{}，热更新:{} 没有自动执行,请查看原因'.format(
                                    content_object.project.project_name, content_object.area_name,
                                    content_object.title)
                                send_mail.delay(to_list, subject, content)
                        else:
                            # 热更新审批完成后没有触发执行
                            # 需要发送告警给相应的运维负责人
                            # users = ','.join([x.first_name for x in new_wse.content_object.project.related_user.all()])
                            users = ','.join(
                                [x.first_name for x in new_wse.content_object.project.get_relate_role_user()])
                            # wx_users = '|'.join([x.first_name for x in new_wse.content_object.project.related_user.all()])
                            wx_users = '|'.join(
                                [x.first_name for x in new_wse.content_object.project.get_relate_role_user()])
                            window_title = '项目地区锁:热更新审批完成后不能自动执行'
                            tips_title = '项目地区锁:热更新审批完成后不能自动执行'
                            tips_content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行'.format(
                                content_object.project.project_name, content_object.area_name,
                                content_object.title)
                            tips_url = 'https://192.168.100.66/myworkflows/hot_server_list/'
                            send_qq.delay(
                                users, window_title, tips_title, tips_content, tips_url)
                            send_weixin_message.delay(
                                wx_users, tips_title + tips_content + tips_url)

                            # 发送邮件告警
                            # to_list = [x.email for x in content_object.project.related_user.all()]
                            to_list = list(set([x.email for x in content_object.project.get_relate_role_user()]))
                            subject = '项目地区锁:热更新审批完成后不能自动执行'
                            content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行'.format(
                                content_object.project.project_name, content_object.area_name,
                                content_object.title)
                            send_mail.delay(to_list, subject, content)

                            """更新任务没有自动执行原因字段"""
                            content_object.no_auto_execute_reason = tips_content
                            content_object.save(update_fields=['no_auto_execute_reason'])

                    # 自动执行后端热更新
                    if isinstance(new_wse.content_object, ServerHotUpdate) and new_wse.state.name == '完成':
                        # 工单完成以后，修改工单的状态
                        content_object = new_wse.content_object
                        content_object.status = '4'
                        content_object.save()
                        ws_notify()

                        # 加载热更新的区服数据到redis中
                        # load_to_redis(new_wse.content_object)

                        # 如果当前项目和地区没有锁，则直接发送到任务队列里面
                        status_list = [x.ops.status for x in
                                       content_object.serverhotupdatersynctask_set.all()]
                        if len(list(set(status_list))) == 1 and '0' in status_list:
                            msg, next_hot_update = get_next_hot_update(
                                content_object.project, content_object.area_name)
                            if next_hot_update:
                                if next_hot_update.status == '4':
                                    do_hot_update(next_hot_update)
                            else:
                                """更新任务没有自动执行原因字段"""
                                content_object.no_auto_execute_reason = msg
                                content_object.save(update_fields=['no_auto_execute_reason'])
                                # 发送邮件告警
                                # to_list = [x.email for x in content_object.project.related_user.all()]
                                to_list = list(set([x.email for x in content_object.project.get_relate_role_user()]))
                                subject = '热更新审批完成后没有自动执行'
                                content = '项目:{} 地区:{}，热更新:{} 没有自动执行,请查看原因: {}'.format(
                                    content_object.project.project_name, content_object.area_name,
                                    content_object.title, msg)
                                send_mail.delay(to_list, subject, content)
                        else:
                            # 热更新审批完成后没有触发执行
                            # 需要发送告警给相应的运维负责人
                            # users = ','.join([x.first_name for x in new_wse.content_object.project.related_user.all()])
                            users = ','.join(
                                [x.first_name for x in new_wse.content_object.project.get_relate_role_user()])
                            # wx_users = '|'.join([x.first_name for x in new_wse.content_object.project.related_user.all()])
                            wx_users = '|'.join(
                                [x.first_name for x in new_wse.content_object.project.get_relate_role_user()])
                            window_title = '项目地区锁:热更新审批完成后不能自动执行'
                            tips_title = '项目地区锁:热更新审批完成后不能自动执行'
                            tips_content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行'.format(
                                content_object.project.project_name, content_object.area_name,
                                content_object.title)
                            tips_url = 'https://192.168.100.66/myworkflows/hot_server_list/'
                            send_qq.delay(
                                users, window_title, tips_title, tips_content, tips_url)
                            send_weixin_message.delay(
                                wx_users, tips_title + tips_content + tips_url)

                            # 发送邮件告警
                            # to_list = [x.email for x in content_object.project.related_user.all()]
                            to_list = list(set([x.email for x in content_object.project.get_relate_role_user()]))
                            subject = '项目地区锁:热更新审批完成后不能自动执行'
                            content = '项目:{} 地区:{} 已经上锁，热更新:{} 不能自动执行'.format(
                                content_object.project.project_name, content_object.area_name,
                                content_object.title)
                            send_mail.delay(to_list, subject, content)

                            """更新任务没有自动执行原因字段"""
                            content_object.no_auto_execute_reason = tips_content
                            content_object.save(update_fields=['no_auto_execute_reason'])

                    # 添加服务器权限接口
                    if isinstance(new_wse.content_object, ServerPermissionWorkflow) and new_wse.state.name == '完成':
                        # api_add_server_permission(new_wse)
                        workflow_add_server_permission.delay(new_wse.id)

                    # 自动添加svn接口
                    if isinstance(new_wse.content_object, SVNWorkflow) and new_wse.state.name == '完成':
                        add_svn_workflow.delay(new_wse.id)

                    # 版本更新单发送qq/wx弹窗提醒
                    if isinstance(new_wse.content_object, VersionUpdate) and new_wse.state.name == '完成':
                        # project_related_ops = new_wse.content_object.project.related_user.all()
                        project_related_ops = new_wse.content_object.project.get_relate_role_user()
                        data = get_version_update_notify(new_wse.title)
                        users = ','.join([x.first_name for x in project_related_ops if x.is_active])
                        send_qq.delay(users, data['window_title'], data['tips_title'], data['tips_content'],
                                      data['tips_url'])
                        wx_users = '|'.join([x.first_name for x in project_related_ops if x.is_active])
                        send_weixin_message.delay(touser=wx_users,
                                                  content=data['tips_title'] + ',' + data['tips_content'] + ',' +
                                                          data['tips_url'])

                    # 自动添加mysql权限
                    if isinstance(new_wse.content_object, MysqlWorkflow) and new_wse.state.name == '完成':
                        add_mysql_permission.delay(new_wse.id)

                    # 执行根据项目删除服务器权限和SVN权限
                    if isinstance(new_wse.content_object, ProjectAdjust) and new_wse.state.name == '完成':
                        content_object = new_wse.content_object
                        # proj_id = content_object.raw_project_group.project.id if content_object.raw_project_group else None
                        if content_object.delete_serper:
                            if content_object.serper_projects is not None:
                                clean_project_serper.delay(new_wse.id, json.loads(content_object.serper_projects))
                        if content_object.delete_svn:
                            if content_object.svn_projects is not None:
                                for proj_id in json.loads(content_object.svn_projects):
                                    clean_svn_workflow.delay(new_wse.id, proj_id)

                        # 如果都没有勾选清除svn或者服务器权限的，改为已处理状态
                        if not content_object.delete_serper and not content_object.delete_svn:
                            content_object.status = '0'
                            content_object.save()

                        # 调整人员所属部门
                        if content_object.new_department_group is not None:
                            org = OrganizationMptt.objects.get(user_id=content_object.applicant_id)
                            org.parent = content_object.new_department_group
                            org.save()

                    # 服务器申请工单完成后发送通知给相关人员
                    if isinstance(new_wse.content_object, Machine) and new_wse.state.name == '完成':
                        machine_administrator_list = [u.first_name for u in
                                                      User.objects.filter(username__in=get_machine_administrator())]
                        users = ','.join(machine_administrator_list)
                        if users:
                            send_qq.delay(users, '你有一个服务器申请工单', '你有一个服务器申请工单',
                                          '链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)',
                                          'http://192.168.100.66/myworkflows/approve_list/')
                        wx_users = '|'.join(machine_administrator_list)
                        if wx_users:
                            send_weixin_message.delay(touser=wx_users, content='你有一个服务器申请工单' + '你有一个服务器申请工单' +
                                                                               '链接:请登录CMDB处理(只能使用谷歌或者火狐浏览器)' +
                                                                               'http://192.168.100.66/myworkflows/approve_list/')
                            # 发送是否已构买任务卡片给相关人员
                            result = get_wx_task_card_data(wx_users, wse, purchase=True)
                            if result['success']:
                                send_task_card_to_wx_user.delay(wx_users, result['data'])

                    # 申请Cy-work的wifi工单完成后，自动添加mac地址
                    if isinstance(new_wse.content_object, Wifi) and new_wse.state.name == '完成':
                        if new_wse.content_object.name == 'Cy-work':
                            applicant_first_name = new_wse.content_object.applicant.first_name
                            touser = '|'.join([u.first_name for u in wse.users.all()])
                            add_mac.delay(applicant_first_name, new_wse.content_object.mac, new_wse.content_object.id,
                                          touser=touser)
                        else:
                            """发送选择工单是否已处理的微信任务卡片"""
                            if wse.approve_user:
                                touser = '|'.join([u.first_name for u in wse.users.all()])
                                result = get_wx_task_card_data(touser, new_wse, handle=True)
                                if result['success']:
                                    send_task_card_to_wx_user.delay(touser, result['data'])

                    # 电脑故障申报/办公电脑和配件申请完成后，都要发送选择工单是否已处理的微信任务卡片
                    if (isinstance(new_wse.content_object, FailureDeclareWorkflow) or isinstance(new_wse.content_object,
                                                                                                 ComputerParts)) and \
                            new_wse.state.name == '完成':
                        if wse.approve_user:
                            touser = '|'.join([u.first_name for u in wse.users.all()])
                            result = get_wx_task_card_data(touser, new_wse, handle=True)
                            if result['success']:
                                send_task_card_to_wx_user.delay(touser, result['data'])

            else:
                """判断是否为取消工单操作, 0为非取消，走正常拒绝流程，1为取消，修改is_cancel状态"""
                to_list = new_wse.creator.email if User.objects.get(id=new_wse.creator.id).is_active else ''
                if to_list:
                    to_list = [to_list]
                    subject, content = make_email_notify(False)
                    send_mail.delay(to_list, subject, content)

                # 发送qq弹框提醒
                users = new_wse.creator.first_name if User.objects.get(id=new_wse.creator.id).is_active else ''

                window_title = "你的申请被拒绝"
                tips_title = "你的申请被拒绝"
                tips_content = "链接:请登录CMDB查看(只能使用谷歌或者火狐浏览器)"
                tips_url = "http://192.168.100.66/myworkflows/approve_list/"
                send_qq.delay(users, window_title, tips_title, tips_content, tips_url)
                # 发送wx弹框提醒
                wx_users = new_wse.creator.first_name if User.objects.get(id=new_wse.creator.id).is_active else ''
                send_weixin_message.delay(touser=wx_users, content=tips_title + tips_content + tips_url)

                # 前端热更新或者后端热更新工单拒绝以后
                # 需要把PRIORITY改为3，也就是暂停的级别
                # 这么做是为了防止阻塞后面正常审批完成的工单执行
                if isinstance(new_wse.content_object, ClientHotUpdate) or isinstance(new_wse.content_object,
                                                                                     ServerHotUpdate):
                    content_object = new_wse.content_object
                    content_object.priority = '3'
                    content_object.save()

            msg = '审批成功'
            log.logger.info('%s - %s: 审批结果:%s %s' % (wse.title, user.username, msg, success))

        else:
            log.logger.error('%s - %s: 审批结果:%s %s' % (wse.title, user.username, msg, success))

    except Exception as e:
        log.logger.error('%s - %s: 审批结果: %s' % (wse.title, user.username, str(e)))


def workflow_handle_receive_wx_callback(task_id, event_key, from_user):
    """
    根据收到的微信回调信息，更改工单的处理状态
    1.根据 task_id 提取到 wse_id
    2.根据 event_key 获取处理结果
    3.根据 from_user 获取审批人
    4.根据 wse_id，event_key，from_user 更改工单的处理状态
    """
    log = WXMsgReceiveLog()
    try:
        wse_id = task_id.split('-')[1]
        wse = WorkflowStateEvent.objects.get(pk=wse_id)
        user = User.objects.get(first_name=from_user)
        if event_key == 'is_handle':
            if isinstance(wse.content_object, FailureDeclareWorkflow) or isinstance(wse.content_object,
                                                                                    Wifi) or isinstance(
                    wse.content_object, ComputerParts):
                wse.content_object.status = 0
                wse.content_object.save()
                # 更新是否已处理微信任务卡状态
                touser = get_yl_network_administrator(first_name=True)
                update_wx_taskcard_status(touser, wse, handle=True)

            elif isinstance(wse.content_object, Machine):
                wse.content_object.status = 0
                wse.content_object.save()
                machine_administrator_list = [u.first_name for u in
                                              User.objects.filter(username__in=get_machine_administrator()) if
                                              u != user]
                touser = machine_administrator_list
                # 更新是否已构买微信任务卡状态
                update_wx_taskcard_status(touser, wse, purchase=True)

            log.logger.info('%s - %s: 处理结果: %s' % (wse.title, user.username, '更改工单处理状态为已处理'))
            # 工单已处理后通知网络组负责人
            org = OrganizationMptt.objects.get(name='网络管理组')
            if org:
                send_weixin_message(touser=org.get_leader_firstname(), content='')
        else:
            raise Exception('未知的处理选项{}'.format(event_key))
    except Exception as e:
        log.logger.error('%s - %s: 处理结果: %s' % (wse.title, user.username, str(e)))
