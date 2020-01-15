from django.conf.urls import url
from it_assets.views import *

urlpatterns = [
    url(r'^supplier/$', supplier, name='供应商'),
    url(r'^data_supplier/$', data_supplier, name='供应商数据'),
    url(r'^add_or_edit_supplier/$', add_or_edit_supplier, name='增加或者修改供应商'),
    url(r'^get_supplier/$', get_supplier, name='供应商数据'),
    url(r'^del_data_supplier/$', del_data_supplier, name='删除供应商数据'),

    url(r'^pos/$', pos, name='位置'),
    url(r'^data_pos/$', data_pos, name='位置数据'),
    url(r'^add_or_edit_pos/$', add_or_edit_pos, name='增加或者修改位置'),
    url(r'^get_pos/$', get_pos, name='位置数据'),
    url(r'^del_data_pos/$', del_data_pos, name='删除位置数据'),

    url(r'^log_assets/$', log_assets, name='资产变更'),

    url(r'^list_pos/$', list_pos, name='下拉展示位置'),
    url(r'^list_user/$', list_user, name='下拉展示存在的用户'),
    url(r'^list_supplier/$', list_supplier, name='下拉展示供应商'),
    url(r'^list_ctype/$', list_ctype, name='下拉展示配件类型'),
    url(r'^list_smodel/$', list_smodel, name='下拉展示资产型号'),
    url(r'^list_assets_smodel/$', list_assets_smodel, name='下拉展示资产配件的型号'),
    url(r'^list_assets_smodel_with_company/$', list_assets_smodel_with_company, name='下拉展示资产配件的型号带公司名'),
    url(r'^list_it_assets/$', list_it_assets, name='下拉展示资产编号'),
    url(r'^list_part_model_status/$', list_part_model_status, name='下拉展示配件状态'),
    url(r'^list_part_model_status_without_company/$', list_part_model_status_without_company, name='下拉展示配件状态,无公司限制'),
    url(r'^list_assets_template/$', list_assets_template, name='下拉展示资产模板'),
    url(r'^list_company_code/$', list_company_code, name='下拉展示公司代号'),
    url(r'^list_using_department/$', list_using_department, name='下拉展示使用部门'),
    url(r'^list_all_users/$', list_all_users, name='下拉展示全体用户'),
    url(r'^list_assets_name/$', list_assets_name, name='下拉展示固定资产名称'),
    url(r'^list_shell_assets_name/$', list_shell_assets_name, name='下拉展示列管资产名称'),

    url(r'^do_event/$', do_event, name='资产变更'),

    url(r'^assets_reception/$', assets_reception, name='资产领用'),
    url(r'^data_assets_reception/$', data_assets_reception, name='资产领用数据'),
    url(r'^get_assets_reception/$', get_assets_reception, name='获取资产领用数据'),
    url(r'^get_assets_change_history/$', get_assets_change_history, name='获取资产变更记录'),
    url(r'^edit_assets_reception/$', edit_assets_reception, name='编辑资产领用数据'),

    url(r'^shell_assets_reception/$', shell_assets_reception, name='列管资产领用'),
    url(r'^data_shell_assets_reception/$', data_shell_assets_reception, name='列管资产领用数据'),

    url(r'^sub_assets_reception/$', sub_assets_reception, name='列管资产领用'),
    url(r'^data_sub_assets_reception/$', data_sub_assets_reception, name='列管资产领用数据'),

    url(r'^assets_trace/$', assets_trace, name='资产领用'),
    url(r'^data_assets_trace/$', data_assets_trace, name='资产领用数据'),

    url(r'^assets_template/$', assets_template, name='资产模板'),
    url(r'^data_assets_template/$', data_assets_template, name='资产模板数据'),
    url(r'^add_or_edit_assets_template/$', add_or_edit_assets_template, name='添加资产模板'),
    url(r'^get_assets_template/$', get_assets_template, name='获取资产模板'),
    url(r'^del_data_assets_template/$', del_data_assets_template, name='删除资产模板'),

    url(r'^company_code/$', company_code, name='公司代号页面'),
    url(r'^data_company_code/$', data_company_code, name='公司代号数据'),
    url(r'^add_or_edit_company_code/$', add_or_edit_company_code, name='新增编辑公司代号数据'),
    url(r'^get_company_code/$', get_company_code, name='获取公司代号数据'),
    url(r'^del_data_company_code/$', del_data_company_code, name='删除公司代号数据'),

    url(r'^download/$', download, name='导出excel'),

    url(r'^assets_collect/$', assets_collect, name='资产图表汇总'),
    url(r'^assets_data_detail/$', assets_data_detail, name='资产详情数据'),
    url(r'^detail/company/(?P<company>\w+)', detail, name='资产详细'),

    url(r'^assets_application_form/$', assets_application_form, name='IT资产申请单'),
    url(r'^create_application_form/$', create_application_form, name='IT资产申请单'),
    url(r'^list_new_organization/$', list_new_organization, name='下拉展示新组织架构'),
    url(r'^assets_add_config/$', assets_add_config, name='主机升级配置'),
    url(r'^it_assets_amount_statistics/$', it_assets_amount_statistics, name='IT资产数量统计'),
    url(r'^assets_batch_alter/$', AssetsBatchAlterView.as_view(), name='资产信息批量修改'),
    url(r'^assets_templates_download/(\w+).xlsx/$', assets_templates_download, name='资产excel模板下载'),
    url(r'^assets_batch_alter_excel_import/$', assets_batch_alter_excel_import, name='批量修改资产信息excel导入'),
    url(r'^assets_batch_alter_record/$', assets_batch_alter_record, name='批量修改资产历史记录'),
    url(r'^data_assets_batch_alter_record/$', data_assets_batch_alter_record, name='批量修改资产历史记录数据'),
    url(r'^data_assets_batch_alter_record_detail/$', data_assets_batch_alter_record_detail, name='批量修改资产历史记录详情数据'),
    url(r'^create_bthalt_assets_excel_data/$', create_bthalt_assets_excel_data, name='生成批量修改资产结果下载数据'),
    url(r'^bthalt_assets_result_downloads/(\w+).xls/$', bthalt_assets_result_downloads, name='生成批量修改资产结果下载数据'),
    url(r'^assets_warehousing_region/$', assets_warehousing_region, name='资产仓库区'),
    url(r'^data_assets_warehousing_region/$', data_assets_warehousing_region, name='资产仓库区域数据'),
    url(r'^add_or_edit_warehousing_region/$', add_or_edit_warehousing_region, name='增加或者修改仓库区域'),
    url(r'^get_assets_warehousing_region/$', get_assets_warehousing_region, name='获取资产仓库区域'),
    url(r'^del_data_warehousing_region/$', del_data_warehousing_region, name='删除仓库区域'),
    url(r'^list_warehousing_region/$', list_warehousing_region, name='列出仓库区域'),
]
