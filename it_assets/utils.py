# -*- encoding: utf-8 -*-

from it_assets.models import *

from collections import Counter

from datetime import datetime

from django.db.models import Count
import os
import xlrd


def format_smodels(smodel_str):
    """将smodel的字符串形式修改为json字典
    eg.
    'i5-6400,i5-6400,i3-2341' ==>
    [
        {'smodel': 'i5-6400', 'number': 2},
        {'smodel': 'i3-2341', 'number': 1},
    ]
    """

    if smodel_str:
        list_smodel = smodel_str.split(',')
        return [{'smodel': k, 'number': v} for k, v in Counter(list_smodel).items()]
    else:
        return None


def get_stock_qty(ctype_obj, smodel):
    """
    获取某个列管资产的型号的库存数量
    如果有，返回数量值
    如果没有，返回None
    """

    ctype_status_smodel_obj = ctype_obj.objects.filter(status=0, smodel=smodel)

    if ctype_status_smodel_obj:
        return ctype_status_smodel_obj[0].number
    else:
        return None


def log_sub_assets(list_obj_numer, event, log_user, pos_obj, user, assets=None):
    """列管资产入库

    如果列管资产是和固定资产一起入库的，需要记录固定资产
    """
    for x in list_obj_numer:
        LogAssets.objects.create(
            event=event, assets=assets, content_object=x['obj'],
            etime=datetime.now(), log_user=log_user, pos=pos_obj, user=user)


def create_or_get_part_model(ctype, smodel_str, company_obj):
    """创建一个新的配件
    然后返回这个obj
    """
    list_smodel_number = format_smodels(
        smodel_str)  # ===> [{'smodel': '8G', 'number': 2}, {'smodel': '16G', 'number': 1}]

    if list_smodel_number:
        for x in list_smodel_number:
            part_model = PartModel.objects.filter(ctype=ctype, smodel=x['smodel'], company=company_obj)
            if part_model:
                x['obj'] = part_model[0]
            else:
                part_model = PartModel.objects.create(ctype=ctype, smodel=x['smodel'], company=company_obj)
                x['obj'] = part_model
    else:
        list_smodel_number = []

    return list_smodel_number


def get_or_create_part_model(ctype, smodel, supplier, company_obj, brand=''):
    """判断是否有ctype和smodel的配件

    如果有，返回obj
    不然，创建这个配件，然后返回obj
    """

    part_model = PartModel.objects.filter(ctype=ctype, smodel=smodel, supplier=supplier, company=company_obj,
                                          brand=brand)

    if part_model:
        return part_model[0]
    else:
        part_model = PartModel.objects.create(ctype=ctype, smodel=smodel, supplier=supplier, company=company_obj,
                                              brand=brand)
        return part_model


def create_or_update_part_model_status(part_model, **kwargs):
    """根据part_model和一些数据来创建PartModelStatus

    如果表中有记录，增加数量
    不然，创建该对象
    """

    part_model_status = PartModelStatus.objects.filter(
        part_model=part_model, status=kwargs['status'], pos=kwargs['pos'], user=kwargs['user'])

    if part_model_status:
        part_model_status = part_model_status[0]
        part_model_status.number += int(kwargs['number'])
        part_model_status.save()
    else:
        part_model_status = PartModelStatus.objects.create(
            part_model=part_model, status=kwargs['status'], number=kwargs['number'], pos=kwargs['pos'],
            user=kwargs['user'])

    return part_model_status


def create_or_update_assets_with_part_model(part_model, assets, number):
    """更新或者新建固定资产和配件的关系表
    """
    """
    assets_part_model = AssetsPartModel.objects.filter(assets=assets, part_model=part_model)

    if assets_part_model:
        assets_part_model = assets_part_model[0]
        assets_part_model.number += int(number)
    else:
        assets_part_model = AssetsPartModel.objects.create(assets=assets, part_model=part_model, number=number)
    """

    # 直接循环插入数据
    for i in range(int(number)):
        AssetsPartModel.objects.create(assets=assets, part_model=part_model, number=1)


def get_max_assets_number(company_code, identifier):
    """根据company code 和标识
    GZCY DZ
    GZCY SJ
    GZCY YP
    来获取当前最大的资产编号
    然后在其基础上 + 1
    """

    prefix = identifier

    assets = Assets.objects.filter(assets_number__icontains=prefix).order_by('-assets_number')
    assets_number = [int(x.assets_number[-8:]) for x in Assets.objects.filter(assets_number__icontains=prefix)]
    assets_number = list(set(assets_number))
    assets_number.sort()
    max_assets_number = assets_number[-1:][0]

    # 当前的时间年
    current_year = str(datetime.now().year)

    if assets:
        # year_number = assets[0].assets_number[-8:]    # 20170013

        # 当前资产的时间年
        assets_year = str(max_assets_number)[0:4]

        if current_year == assets_year:
            current_max_number = str(max_assets_number)[-4:]  # 0013
            max_number = current_year + str(int(current_max_number) + 1).zfill(4)  # 20170014
        else:
            max_number = current_year + '0001'  # 20180001
    else:
        max_number = current_year + '0001'  # 20170001

    return prefix + max_number


def get_company_status_number(company, status_code):
    """获取某个公司下某个状态的所有的资产数量
    """

    assets_number = Assets.objects.filter(company=company, status=status_code).count()

    part_model_status_number = PartModelStatus.objects.filter(part_model__company=company, status=status_code).count()

    return assets_number + part_model_status_number


def get_all_assets():
    """获取所有公司的所有的资产总数

    数据格式:
    [
        {
            'company': '广州创娱',
            'data': [
                {
                    'status': '库存', 'panel': 'panel panel-primary',
                    'number': 100, 'url': '/it_assets/detail/company/广州创娱/status/库存',
                },
                {
                    'status': '领用', 'panel': 'panel panel-green',
                    'number': 100, 'url': '/it_assets/detail/company/广州创娱/status/领用',
                },
                ...
            ]
        },
        {
            'company': '海南创娱',
            'data': [
                {
                    'status': '库存', 'panel': 'panel panel-primary',
                    'number': 100, 'url': '/it_assets/detail/company/海南创娱/status/库存',
                },
                {
                    'status': '领用', 'panel': 'panel panel-green',
                    'number': 100, 'url': '/it_assets/detail/company/海南创娱/status/领用',
                },
                ...
            ]
        },
        ...

    ]
    """
    assets_data = []

    all_company = CompanyCode.objects.all()
    all_status = dict(Assets.STATUS).items()

    for company in all_company:
        company_data = {}
        company_data['company'] = company.name
        data = []
        for status_code, status in all_status:
            data_status = {}
            data_status['status'] = status
            if status == '库存':
                panel = 'panel-primary'
            elif status == '领用':
                panel = 'panel-green'
            elif status == '外借':
                panel = 'panel-yellow'
            elif status == '回收':
                panel = 'panel-warning'
            elif status == '清理':
                panel = 'panel-danger'
            elif status == '损毁':
                panel = 'panel-red'
            data_status['panel'] = panel
            data_status['url'] = '/it_assets/detail/company/%s/' % (company.name)
            number = get_company_status_number(company, status_code)
            data_status['number'] = number
            data.append(data_status)
        company_data['data'] = data
        assets_data.append(company_data)

    return assets_data


def get_assets_detail():
    """根据公司名获取公司所有状态下的资产的数据模板
    格式如下:
    [
        {'title': '库存', 'status_code': 0, 'class': 'bar-example'},
        {'title': '领用', 'status_code': 1, 'class': 'bar-example'},
        {'title': '清理', 'status_code': 2, 'class': 'bar-example'},
    ]
    """
    all_status = dict(Assets.STATUS).items()

    data = []

    for status_code, status in all_status:
        info = {}
        info['title'] = status
        info['status_code'] = status_code
        info['class'] = 'bar-example'
        data.append(info)

    return data


def get_assets_detail_data(status_code, company_name):
    """根据公司名和状态获取数据
    格式:
    [
        {'name': '主机', 'number': 20},
        {'name': '显示器', 'number': 20},
        {'name': '绘画板', 'number': 20},
    ]
    """

    data = []

    company = CompanyCode.objects.get(name=company_name)

    assets_data = list(Assets.objects.values('name').filter(
        company=company, status=status_code).annotate(number=Count('name')))

    part_model_data = []

    all_part_model = PartModelStatus.objects.filter(part_model__company=company, status=status_code)

    for part_model in all_part_model:
        part_model_data_info = {}
        part_model_data_info['number'] = part_model.number
        part_model_data_info['name'] = part_model.part_model.ctype + '-' + part_model.part_model.smodel
        part_model_data.append(part_model_data_info)

    data.extend(assets_data)
    data.extend(part_model_data)

    return data


def get_upload_sell_off_data(file):
    fpath = os.path.join(os.getcwd(), 'it_assets/upload/', file.name)
    with open(fpath, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    readbook = xlrd.open_workbook(fpath)
    sheet1 = readbook.sheet_by_name('sheet1')
    nrows = sheet1.nrows
    assets_list = []
    for i in range(1, nrows):
        cell = sheet1.cell_value(i, 0)
        assets_list.append(cell)
    return assets_list


def save_uploaded_file(f, file_path, save_filename):
    """
    Handle file upload
    """
    fpath = os.path.join(os.getcwd(), file_path, save_filename)
    with open(fpath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def read_excel_table_data(f):
    """读取excel中的表格内容"""
    data = xlrd.open_workbook(f)
    table = data.sheet_by_name(u'Sheet1')
    thead = table.row_values(0)
    rows = table.nrows
    tbody = []
    for i in range(1, rows):
        tr = table.row_values(i)
        tbody.append(tr)
    return {'thead': thead, 'tbody': tbody}


def batch_alter_assets_info(table_data, alter_type, old_index, new_index, record_obj, user):
    """
    批量修改资产信息，并记录结果及资产变更记录
    alter_type:
        1 - 修改公司主体
        2 - 修改资产状态
        3 - 修改仓库区域
    """
    result = 1
    current_value = ''
    new_value = ''
    for table_td in table_data[1:]:
        assets_number = table_td[0]
        assets_obj = Assets.objects.filter(assets_number=assets_number)
        if not assets_obj:
            remark = '资产编号不存在'
        else:
            old_value = table_td[old_index]
            new_value = table_td[new_index]
            if alter_type == 1:
                event = 11
                new_company_obj = CompanyCode.objects.filter(name=new_value)
                current_value = assets_obj[0].company.name
                if not new_company_obj:
                    remark = '修改后公司主体不存在'
                    result = 0
                else:
                    new_company_obj = new_company_obj[0]
                    if current_value == new_value:
                        remark = '公司主体已经是 {}，无需修改'.format(current_value)
                        result = 0
                    else:
                        assets_obj.update(**{'company': new_company_obj})
                        result = 1
                        remark = '修改成功'
                        """记录资产变更记录"""
                        LogAssets.objects.create(
                            event=event, assets=assets_obj[0], part_model=None, etime=datetime.now(),
                            log_user=user, pos=assets_obj[0].pos, user=assets_obj[0].user,
                            pre_configuration=current_value, current_configuration=new_value)
            elif alter_type == 2:
                if new_value in ('变卖', '损毁'):
                    if new_value == '变卖':
                        status = 6
                        event = 12
                    elif new_value == '损毁':
                        status = 4
                        event = 5
                    current_value = assets_obj[0].get_status_display()
                    if current_value == new_value:
                        result = 0
                        remark = '资产状态已经是 {}，无需修改'.format(current_value)
                    else:
                        pre_user = assets_obj[0].user
                        user_department = user.organizationmptt_set.first().get_ancestors_except_self()
                        assets_obj.update(
                            **{'status': status, 'user': user.username, 'auth_user_id': user.id, 'using_department': user_department,
                               'belongs_to_new_organization': user_department})
                        result = 1
                        remark = '修改成功'
                        """记录资产变更记录"""
                        LogAssets.objects.create(
                            event=event, assets=assets_obj[0], part_model=None, etime=datetime.now(),
                            log_user=user, pos=assets_obj[0].pos, user=user.username, pre_user=pre_user,
                            pre_configuration=current_value, current_configuration=new_value)
                else:
                    result = 0
                    remark = '目前只支持批量变卖资产'
            elif alter_type == 3:
                event = 13
                new_wr_obj, created = AssetsWarehousingRegion.objects.get_or_create(name=new_value, defaults={'name': new_value})
                current_value = assets_obj[0].warehousing_region.name if assets_obj[0].warehousing_region else ''
                if current_value == new_value:
                    remark = '仓库区域已经是 {}，无需修改'.format(current_value)
                    result = 0
                else:
                    assets_obj.update(**{'warehousing_region': new_wr_obj})
                    result = 1
                    remark = '修改成功'
                    """记录资产变更记录"""
                    LogAssets.objects.create(
                        event=event, assets=assets_obj[0], part_model=None, etime=datetime.now(),
                        log_user=user, pos=assets_obj[0].pos, user=assets_obj[0].user,
                        pre_configuration=current_value, current_configuration=new_value)
            else:
                raise Exception('未知的修改类型')

        """记录变更结果"""
        AssetsBatchAlterRecordDetail.objects.create(record=record_obj, assets_number=assets_number, result=result,
                                                    remark=remark, old_value=current_value, new_value=new_value)
