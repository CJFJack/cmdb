# --encoding=utf-8
from django.conf.urls import url
from users.views import *
from django.views.generic.base import TemplateView

urlpatterns = [
    # Examples:
    url(r'^group_permission/$', group_permission, name='分组和权限'),
    url(r'^user_permission/$', user_permission, name='用户和权限'),
    url(r'^api_permission/$', api_permission, name='API权限'),
    # url(r'^group/$', group, name='group'),
    # url(r'^user/$', user, name='user'),
    # url(r'^list_group/$', list_group, name='list_group'),
    # url(r'^add_group/$', add_group, name='add_group'),
    url(r'^save_group_permission/$', save_group_permission, name='保存分组和权限'),
    url(r'^save_user_permission/$', save_user_permission, name='保存用户和权限'),
    url(r'^get_group_permission/$', get_group_permission, name='获取分组的权限'),
    url(r'^get_org_section_permission/$', get_org_section_permission, name='获取新组织架构节点的权限'),
    url(r'^get_user_permission/$', get_user_permission, name='获取用户的权限'),
    url(r'^group_info/$', group_info, name='分组的用户'),
    url(r'^data_group_info/$', data_group_info, name='分组用户数据'),
    url(r'^group_section/$', group_section, name='部门管理分组页面'),
    url(r'^data_group_section/$', data_group_section, name='部门管理分组数据'),
    url(r'^data_user_list/$', data_user_list, name='用户列表数据'),
    url(r'^data_group_list/$', data_group_list, name='分组列表数据'),
    url(r'^add_or_edit_user/$', add_or_edit_user, name='增加或者修改用户'),
    url(r'^add_or_edit_group/$', add_or_edit_group, name='增加或者修改分组'),
    url(r'^add_or_edit_group_section/$', add_or_edit_group_section, name='增加或者修改部门管理分组'),
    url(r'^del_user/$', del_user, name='删除用户'),
    url(r'^del_group/$', del_group, name='删除分组'),
    url(r'^del_group_section/$', del_group_section, name='删除部门管理分组'),
    url(r'^get_data_user/$', get_data_user, name='根据id获取用户信息'),
    url(r'^get_data_group/$', get_data_group, name='根据id获取分组信息'),
    url(r'^get_data_group_section/$', get_data_group_section, name='根据id获取部门管理分组信息'),
    url(r'^passwd_data_user/$', passwd_data_user, name='修改用户密码'),
    # url(r'^data_groups_info/$', data_groups_info, name='data_groups_info'),
    url(r'^user_list/$', user_list, name='user_list'),
    url(r'^group_list/$', group_list, name='分组列表'),
    url(r'^list_ldap_groups/$', list_ldap_groups, name='ldap部门下拉列表'),
    url(r'^list_group_leaf/$', list_group_leaf, name='叶子结点部门'),
    url(r'^list_group_section/$', list_group_section, name='展示部门管理分组'),
    url(r'^list_group_section_all/$', list_group_section_all, name='展示全部的部门管理分组'),
    url(r'^list_department_group_all/$', list_department_group_all, name='展示全部的部门管理分组'),
    url(r'^add_group_user/$', add_group_user, name='给分组添加用户'),
    url(r'^del_group_user/$', del_group_user, name='删除分组用户'),
    url(r'^new_passwd/$', new_passwd, name='新的密码'),
    url(r'^reset_password/$', reset_password, name='新的密码'),
    # url(r'^add_user/$', add_user, name='add_user'),
    # url(r'^get_user/$', get_user, name='get_user'),
    # url(r'^edit_user/$', edit_user, name='edit_user'),
    # url(r'^del_user/$', del_user, name='del_user'),
    url(r'^clean/$', clean, name='clean'),
    url(r'^do_clean/$', do_clean, name='执行清除用户'),
    url(r'^get_not_active_user/$', get_not_active_user, name='获取离职人员API文档'),

    url(r'^user_profile$', user_profile, name='用户设置'),
    url(r'^set_email_approve/$', set_email_approve, name='开始邮件审批的功能'),
    url(r'^set_wechat_approve/$', set_wechat_approve, name='开始微信审批的功能'),
    url(r'^group_users_api/$', group_users_api, name='部门用户API文档'),

    url(r'^user_svn_serper_projects/$', user_svn_serper_projects, name='获取用户的svn和服务器权限的项目'),
    url(r'^get_group_org/$', get_group_org, name='获取组织架构'),

    url(r'^user_desert/(?P<user_id>[0-9]+)/$', UserDesertView.as_view(), name='user_desert'),  # 员工离职
    url(r'^create_recover_assets_list/$', create_recover_assets_list, name='create_recover_assets_list'),  # 资产回收列表
    url(r'^organization/$', OrganizationView.as_view(), name='organization'),
    url(r'^list_new_organization/$', list_new_organization, name='list_new_organization'),
    url(r'^organization/(?P<org_id>[0-9]+)/$', OrganizationEditView.as_view(), name='organization_edit'),
    url(r'^organization_delete/(?P<org_id>[0-9]+)/$', organization_delete, name='organization_delete'),
    url(r'^organization_user_add/$', organization_user_add, name='organization_user_add'),
    url(r'^organization_section_add/$', organization_section_add, name='organization_section_add'),

    url(r'^organization_frame_description/$', TemplateView.as_view(template_name=
                                                                   'users_organization_frame_description.html'),
        name='organization_frame_description'),  # 组织架构描述
    url(r'^org_edit_href/$', TemplateView.as_view(template_name='users_edit_href.html'),
        name='org_edit_href'),
    url(r'^new_department_permission/$', NewDepartmentPermView.as_view(), name='new_department_permission'),
    # 新部门权限设置页面
    url(r'^permission_change_record/$', permission_change_record, name='permission_change_record'),  # 员工权限变更记录
    url(r'^edit_ent_qq/$', edit_ent_qq, name='edit_ent_qq'),  # 编辑企业qq信息
    url(r'^edit_ent_email/$', edit_ent_email, name='edit_ent_email'),  # 编辑企业邮箱信息
    url(r'^change_svn_passwd/$', change_svn_passwd, name='change_svn_passwd'),  # 修改svn密码
    url(r'^get_user_clean_page/(?P<user_id>[0-9]+)/$', get_user_clean_page, name='get_user_clean_page'),  # 获取清理员工权限页面
    url(r'^downloads/$', downloads, name='导出用户列表'),
    url(r'^user_research_result/$', user_research_result, name='用户搜索结果列表页面'),
    url(r'^cmdb_user_add_api/$', cmdb_user_add_api, name='开通cmdb账号API接口文档'),
    url(r'^add_vpn_user/$', add_vpn_user, name='开通openvpn帐号'),
    url(r'^modify_vpn_user/$', modify_vpn_user, name='修改openvpn帐号密码'),
    url(r'^users_change_record/$', users_change_record, name='用户变更（新增/修改/删除/清理权限）记录表'),
    url(r'^change_ldap_passwd/$', change_ldap_passwd, name='修改ldap密码'),
    url(r'^organization_tree/$', organization_tree, name='获取组织架构树'),
    url(r'^role_group/$', role_group, name='角色分组页面'),
    url(r'^data_role_group/$', data_role_group, name='角色分组数据'),
    url(r'^add_or_edit_role_group/$', add_or_edit_role_group, name='增加或者修改角色分组'),
    url(r'^get_role_group_data/$', get_role_group_data, name='获取角色分组数据'),
    url(r'^del_role_group/$', del_role_group, name='删除角色分组数据'),
    url(r'^list_role_group/$', list_role_group, name='下拉展示角色分组'),
    url(r'^cmdb_get_role_user_info_api/$', cmdb_get_role_user_info_api, name='cmdb获取角色分组信息api文档'),
    url(r'^batch_user_desert_page/$', batch_user_desert_page, name='批量离职'),
    url(r'^recently_clean_user/$', recently_clean_user, name='最近清除权限的用户'),
    url(r'^data_user_change_record/$', data_user_change_record, name='用户变更记录数据'),
    url(r'^open_ent_qq/$', open_ent_qq, name='开通企业QQ'),
    url(r'^open_ent_email/$', open_ent_email, name='开通企业邮箱'),
    url(r'^users_share_info_template/$', UsersShareInfoTemp.as_view(), name='用户入职信息模板'),
]
