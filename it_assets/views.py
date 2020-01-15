# -*- encoding: utf-8 -*-
from django.shortcuts import render_to_response, render, reverse
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
# from django.http import StreamingHttpResponse
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Q
from django.db.models import Count, Sum
from django.core.exceptions import PermissionDenied
from django.db.models.deletion import ProtectedError
from django.contrib.auth.models import User, Group
from django.views import generic

from it_assets.models import *
from users.models import GroupProfile
from it_assets.utils import *
from it_assets.exceptions import *
from it_assets.name_config import *
from it_assets.forms import UploadFileForm
from users.models import *
from functools import reduce
from django.http import FileResponse

import json
from datetime import datetime
import time
import xlwt
import os
import hashlib


def supplier(request):
    "供应商页面"
    if request.method == 'GET':
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            head = {"value": "供应商", 'username': request.user.username}
            return render(request, 'supplier.html', {'head': head})
        else:
            return render(request, '403.html')


def data_supplier(request):
    '供应商数据'
    if request.method == "GET":
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            raw_get = request.GET.dict()
            draw = raw_get.get('draw', 0)
            raw_data = Supplier.objects.all()
            recordsTotal = len(raw_data)

            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def add_or_edit_supplier(request):
    '增加或者修改供应商'
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')

        try:
            if editFlag:
                if User.objects.get(id=request.user.id).has_perm('users.edit_it_assets'):
                    s = Supplier.objects.filter(id=id)
                    s.update(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
            else:
                if User.objects.get(id=request.user.id).has_perm('users.add_it_assets'):
                    Supplier.objects.create(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
        except PermissionDenied:
            msg = '权限拒绝'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def get_supplier(request):
    '供应商数据'
    if request.method == 'POST':
        if User.objects.get(id=request.user.id).has_perm('users.edit_it_assets'):
            id = json.loads(request.body.decode('utf-8')).get('id')
            obj = Supplier.objects.get(id=id)
            edit_data = obj.edit_data()
            return JsonResponse(edit_data)
        else:
            raise PermissionDenied


def del_data_supplier(request):
    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.del_it_assets'):
            del_data = json.loads(request.body.decode('utf-8'))
            objs = Supplier.objects.filter(id__in=del_data)
            msg = ''

            try:
                with transaction.atomic():
                    objs.delete()
                success = True
            except Exception as e:
                msg = str(e)
                success = False

            return JsonResponse({'data': success, 'msg': msg})
        else:
            raise PermissionDenied


def pos(request):
    "位置"
    if request.method == 'GET':
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            head = {"value": "位置", 'username': request.user.username}
            return render(request, 'pos.html', {'head': head})
        else:
            return render(request, '403.html')


def data_pos(request):
    '供应商数据'
    if request.method == "GET":
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            raw_get = request.GET.dict()
            draw = raw_get.get('draw', 0)
            raw_data = Position.objects.all()
            recordsTotal = len(raw_data)

            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def add_or_edit_pos(request):
    '增加或者修改位置'
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')

        try:
            if editFlag:
                if User.objects.get(id=request.user.id).has_perm('users.edit_it_assets'):
                    s = Position.objects.filter(id=id)
                    s.update(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
            else:
                if User.objects.get(id=request.user.id).has_perm('users.add_it_assets'):
                    Position.objects.create(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
        except PermissionDenied:
            msg = '权限拒绝'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def get_pos(request):
    '供应商数据'
    if request.method == 'POST':
        if User.objects.get(id=request.user.id).has_perm('users.edit_it_assets'):
            id = json.loads(request.body.decode('utf-8')).get('id')
            obj = Position.objects.get(id=id)
            edit_data = obj.edit_data()
            return JsonResponse(edit_data)
        else:
            raise PermissionDenied


def del_data_pos(request):
    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.del_it_assets'):
            del_data = json.loads(request.body.decode('utf-8'))
            objs = Position.objects.filter(id__in=del_data)
            msg = ''

            try:
                with transaction.atomic():
                    objs.delete()
                success = True
            except Exception as e:
                msg = str(e)
                success = False

            return JsonResponse({'data': success, 'msg': msg})
        else:
            raise PermissionDenied


def list_pos(request):
    '下拉展示位置'
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_pos = Position.objects.filter(name__icontains=q)
        else:
            all_pos = Position.objects.all()

        for x in all_pos:
            data.append({'id': x.id, 'text': x.name})

        data.append({'id': 0, 'text': '全部'})

        return JsonResponse(data, safe=False)


def list_user(request):
    '下拉展示资产中的用户'
    if request.method == "POST":
        term = request.POST.get('term', None)

        if term:
            data = [
                x['user'] for x in Assets.objects.values('user').annotate(dcount=Count('user')) if term in x['user']
            ]
        else:
            data = []
        return JsonResponse(data, safe=False)


def list_supplier(request):
    '下拉展示供应商'
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_supplier = Supplier.objects.filter(name__icontains=q)
        else:
            all_supplier = Supplier.objects.all()

        for x in all_supplier:
            data.append({'id': x.id, 'text': x.name})

        return JsonResponse(data, safe=False)


def list_user(request):
    '下拉展示位置'
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_supplier = Supplier.objects.filter(name__icontains=q)
        else:
            all_supplier = Supplier.objects.all()

        for x in all_supplier:
            data.append({'id': x.id, 'text': x.name})

        return JsonResponse(data, safe=False)


def list_company_code(request):
    '下拉展示公司代号'
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_company_code = CompanyCode.objects.filter(Q(name__icontains=q) | Q(code__icontains=q))
        else:
            all_company_code = CompanyCode.objects.all()

        for x in all_company_code:
            data.append({'id': x.id, 'text': x.name, 'code': x.code})

        return JsonResponse(data, safe=False)


def list_using_department(request):
    '下拉展示使用部门'
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_using_department = Group.objects.filter(Q(name__icontains=q))
        else:
            all_using_department = Group.objects.all()

        for x in all_using_department:
            data.append({'id': x.id, 'text': x.name})

        return JsonResponse(data, safe=False)


def list_new_organization(request):
    """下拉展示新组织架构部门节点"""
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_new_organization = OrganizationMptt.objects.filter(Q(name__icontains=q) |
                                                                   Q(parent__name__icontains=q) |
                                                                   Q(parent__parent__name__icontains=q) |
                                                                   Q(parent__parent__parent__name__icontains=q)).filter(
                type=1)
        else:
            all_new_organization = OrganizationMptt.objects.all().filter(type=1)

        for x in all_new_organization:
            data.append({'id': x.get_ancestors_name(), 'text': x.get_ancestors_name()})

        return JsonResponse(data, safe=False)


def list_all_users(request):
    """下拉展示全体用户"""
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_users = User.objects.filter(Q(username__icontains=q) | Q(first_name__icontains=q)).filter(is_active=1)
        else:
            all_users = User.objects.filter(is_active=1)

        for x in all_users:
            data.append({'id': x.id, 'text': x.username})

        return JsonResponse(data, safe=False)


def list_shell_assets_name(request):
    '下拉展示列管资产名称'

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if not q:
            q = ''

        data = [{'id': v, 'text': k} for k, v in name_map_abbreviation.items() if q in k or q in v]

        return JsonResponse(data, safe=False)


def list_assets_name(request):
    '下拉展示固定资产名称'

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if not q:
            q = ''

        data = [{'id': text, 'text': text} for index, text in enumerate(assets_name_list) if q in text]

        return JsonResponse(data, safe=False)


def list_assets_template(request):
    '下拉展示资产模板'
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_template = AssetsTemplates.objects.filter(template_name__icontains=q)
        else:
            all_template = AssetsTemplates.objects.all()

        for x in all_template:
            data.append({'id': x.id, 'text': x.template_name})

        return JsonResponse(data, safe=False)


def list_ctype(request):
    '下拉展示资产类型'

    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if not q:
            q = ''

        data = [
            {'id': x['ctype'], 'text': x['ctype']} for x in
            PartModel.objects.values('ctype').annotate(dcount=Count('ctype'))
        ]

        return JsonResponse(data, safe=False)


def list_smodel(request):
    '下拉展示资产型号'
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        ctype = request.POST.get('ctype', None)

        if q is None:
            q = ''

        if ctype == '选择类别':
            pass
        else:
            all_smodel = PartModel.objects.filter(ctype=ctype, smodel__icontains=q)

            for x in all_smodel:
                data.append({'id': x.id, 'text': x.smodel})

        return JsonResponse(data, safe=False)


def list_assets_smodel(request):
    '下拉展示资产配件的型号'
    if request.method == "POST":
        data = []

        q = request.POST.get('q', '')

        ctype = request.POST.get('ctype', None)

        assets = request.POST.get('assets', None)

        if assets != '0' and ctype != '0':
            assets = Assets.objects.get(id=assets)
            all_smodel = assets.assetspartmodel_set.filter(part_model__ctype=ctype, part_model__smodel__icontains=q)

            for x in all_smodel:
                data.append({'id': x.id, 'text': x.part_model.smodel})

        return JsonResponse(data, safe=False)


def list_assets_smodel_with_company(request):
    """下拉展示资产配件的型号带公司名"""
    if request.method == "POST":
        data = []

        q = request.POST.get('q', '')

        ctype = request.POST.get('ctype', None)

        assets = request.POST.get('assets', None)

        if assets != '0' and ctype != '0':
            assets = Assets.objects.get(id=assets)
            all_smodel = assets.assetspartmodel_set.filter(part_model__ctype=ctype, part_model__smodel__icontains=q)

            for x in all_smodel:
                if x.part_model.brand:
                    data.append({'id': x.id,
                                 'text': x.part_model.brand + '-' + x.part_model.smodel + '-' + x.part_model.company.name})
                else:
                    data.append({'id': x.id,
                                 'text': x.part_model.smodel + '-' + x.part_model.company.name})

        return JsonResponse(data, safe=False)


def list_part_model_status(request):
    '根据公司、位置和类型来展示配件的某个状态下记录'

    if request.method == 'POST':
        data = []

        q = request.POST.get('q', None)

        ctype = request.POST.get('ctype', None)

        pos = request.POST.get('pos', None)

        pos = Position.objects.get(id=pos)

        company_code = request.POST.get('company_code', None)
        company = CompanyCode.objects.get(id=company_code)

        status = request.POST.get('status', None)

        status_list = status.split(',')

        if q is None:
            q = ''

        all_part_model_status = PartModelStatus.objects.filter(
            pos=pos, part_model__company=company, part_model__ctype=ctype,
            status__in=status_list, part_model__smodel__icontains=q)

        for x in all_part_model_status:
            data.append({'id': x.id, 'text': x.part_model.smodel})

        return JsonResponse(data, safe=False)


def list_part_model_status_without_company(request):
    '根据位置和类型来展示配件的某个状态下记录'

    if request.method == 'POST':
        data = []

        q = request.POST.get('q', None)

        ctype = request.POST.get('ctype', None)

        pos = request.POST.get('pos', None)

        pos = Position.objects.get(id=pos)

        status = request.POST.get('status', None)

        status_list = status.split(',')

        if q is None:
            q = ''

        all_part_model_status = PartModelStatus.objects.filter(
            pos=pos, part_model__ctype=ctype,
            status__in=status_list, part_model__smodel__icontains=q)

        for x in all_part_model_status:
            data.append({'id': x.id, 'text': x.part_model.smodel})

        return JsonResponse(data, safe=False)


def list_it_assets(request):
    '下拉展示资产型号'
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)
        status = request.POST.get('status', None)

        status_list = status.split(',')

        company_code_id = request.POST.get('company_code_id', None)

        if company_code_id is not None:
            if int(company_code_id) == 0:
                data = []
            else:
                show_user = request.POST.get('show_user')
                company = CompanyCode.objects.get(id=company_code_id)
                if q is None:
                    q = ''

                all_assets_number = Assets.objects.filter((
                                                                  Q(assets_number__icontains=q) |
                                                                  Q(user__icontains=q) |
                                                                  Q(name__icontains=q)) &
                                                          Q(status__in=status_list, company=company))

                for x in all_assets_number:
                    if int(show_user):
                        data.append({'id': x.id, 'text': x.assets_number + '-' + x.name})
                    else:
                        data.append({'id': x.id, 'text': x.assets_number + '-' + x.name + '-' + x.user})
        else:
            if q is None:
                q = ''

            all_assets_number = Assets.objects.filter((
                                                              Q(assets_number__icontains=q) |
                                                              Q(user__icontains=q) |
                                                              Q(name__icontains=q)) &
                                                      Q(status__in=status_list))

            for x in all_assets_number:
                data.append({'id': x.id, 'text': x.assets_number + '-' + x.name + '-' + x.user})

        return JsonResponse(data, safe=False)


def log_assets(request):
    "资产变更页面"

    if request.method == 'GET':
        if User.objects.get(id=request.user.id).has_perm('users.edit_it_assets'):
            head = {'value': '资产变更', 'username': request.user.username}
            return render(request, 'log_assets.html', {'head': head})
        else:
            return render(request, '403.html')


def create_application_form(request):
    """生成打印单"""
    if request.method == "POST":
        pdata = json.loads(request.body.decode('utf-8'))
        if 'type' in pdata:
            if pdata.get('type') == 'assets':
                assets_id_list = pdata.get('selected')
                return HttpResponse(json.dumps({'success': True, 'assets_id_list': assets_id_list}),
                                    content_type="application/json")
        else:
            dataTable = pdata.get('dataTable')
            assets_id_list = []
            for assets_id in dataTable:
                assets_id_list.append(assets_id['assets'])
            return HttpResponse(json.dumps({'success': True, 'assets_id_list': assets_id_list}),
                                content_type="application/json")


def do_event(request):
    """资产变更"""

    if request.method == "POST":
        pdata = json.loads(request.body.decode('utf-8'))
        assets_event = pdata.get('assets_event')
        assets_type = pdata.get('assets_type')
        dataTable = pdata.get('dataTable')
        # print(dataTable)

        msg = ''

        # print(dataTable)
        # return False

        # EVENT_DIC = dict((v, k) for k, v in LogAssets.EVENT)

        try:
            with transaction.atomic():
                if assets_event == '入库':
                    if assets_type == '固定资产':
                        """ 固定资产入库
                        如果是主机和笔记本，通常带有主机配件，比如cpu，硬盘，内存之类
                        需要写入的东西
                        1 固定资产记录增加一条
                        2 主机配件的不同类型的记录增加库存数量
                        入库日志
                        1 固定资产的日志
                        2 列管资产的日志

                        数据格式:
                        [
                            {
                                'pos': '2楼办公区', 'using_department': '财务部', 'with_graphics': '集成', 'ctype': '0',
                                'board': '联想', 'with_ssd': '三星192G', 'with_cpu': 'I5-6200G',
                                'with_disk': '', 'name': '笔记本', 'pos_id': '1', 'specification': 'E460', 'id': 2,
                                'with_mem': '金士顿8G', 'ctype_text': '电子设备', 'brand': '联想',
                                'company_code_id': 1, 'company_text': '广州创娱', 'company_code': 'GZCY',
                                'supplier_id': 1, 'supplier': '浪潮', 'purchase_id': 0, 'purchase': '是', 'price': 2000,
                            },
                            {
                                'pos': '2楼办公区', 'using_department': '财务部', 'with_graphics': '集成', 'ctype': '0',
                                'board': '联想', 'with_ssd': '', 'with_cpu': 'Intel N3050',
                                'with_disk': 'WD500G', 'name': '笔记本', 'pos_id': '1', 'specification': 'Lenovo Flex 3-1130',
                                'id': 3, 'with_mem': '金士顿4G', 'ctype_text': '电子设备', 'brand': '联想',
                                'company_code_id': 1, 'company_text': '广州创娱', 'company_code': 'GZCY',
                                'supplier_id': 1, 'supplier': '浪潮', 'purchase_id': 0, 'purchase': '是', 'price': 2000,
                            }
                        ]
                        """
                        for data in dataTable:
                            with_cpu = data.pop('with_cpu')
                            with_ssd = data.pop('with_ssd')
                            with_disk = data.pop('with_disk')
                            with_mem = data.pop('with_mem')
                            with_graphics = data.pop('with_graphics')
                            with_board = data.pop('board')

                            data.pop('pos')
                            data.pop('ctype_text')
                            data.pop('id')

                            # 新购买的单价的问题
                            purchase = data.pop('purchase_id')
                            data.pop('purchase')
                            price = data.pop('price')

                            # 公司的相关信息
                            data.pop('company_text')
                            company_code_id = data.pop('company_code_id')
                            company_code = data.pop('company_code')
                            company_obj = CompanyCode.objects.get(id=company_code_id)
                            data['company'] = company_obj

                            pos_id = data.pop('pos_id')
                            pos_obj = Position.objects.get(id=pos_id)
                            data['pos'] = pos_obj

                            warehousing_region_id = data.pop('warehousing_region_id')
                            wr = AssetsWarehousingRegion.objects.get(id=warehousing_region_id)
                            data['warehousing_region'] = wr

                            supplier_id = data.pop('supplier_id')
                            data.pop('supplier')
                            if supplier_id == '0':
                                data['supplier'] = None
                            else:
                                data['supplier'] = Supplier.objects.get(id=supplier_id)

                            # 保管人就是录入人
                            data['user'] = request.user.username

                            # 添加status
                            data['status'] = 0

                            # 添加资产编号
                            data['assets_number'] = get_max_assets_number(company_code, 'DZ')

                            # 添加新所属组织架构
                            data['belongs_to_new_organization'] = data['using_department']

                            # 添加与User表关联的auth_user_id字段
                            data['auth_user_id'] = request.user.id

                            # 创建固定资产对象
                            assets = Assets.objects.create(**data)

                            # 创建配件对象
                            list_cpu_obj_numer = create_or_get_part_model('CPU', with_cpu, company_obj)
                            list_ssd_obj_numer = create_or_get_part_model('固态硬盘', with_ssd, company_obj)
                            list_disk_obj_numer = create_or_get_part_model('机械硬盘', with_disk, company_obj)
                            list_mem_obj_numer = create_or_get_part_model('内存', with_mem, company_obj)
                            list_graphics_obj_numer = create_or_get_part_model('显卡', with_graphics, company_obj)
                            list_board_obj_number = create_or_get_part_model('主板', with_board, company_obj)

                            # 固定资产和列管资产进行关联
                            # list_cpu_obj_numer # ===> [{'obj': '8G', 'number': 2}, {'obj': '16G', 'number': 1}]
                            # cpu
                            for x in list_cpu_obj_numer:
                                for n in range(0, x['number']):
                                    AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=1)

                            # ssd
                            for x in list_ssd_obj_numer:
                                # AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=x['number'])
                                for n in range(0, x['number']):
                                    AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=1)

                            # disk
                            for x in list_disk_obj_numer:
                                # AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=x['number'])
                                for n in range(0, x['number']):
                                    AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=1)

                            # mem
                            for x in list_mem_obj_numer:
                                # AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=x['number'])
                                for n in range(0, x['number']):
                                    AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=1)

                            # graphics
                            for x in list_graphics_obj_numer:
                                AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=x['number'])

                            # board
                            for x in list_board_obj_number:
                                # AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=x['number'])
                                for n in range(0, x['number']):
                                    AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=1)

                            # 固定资产入库日志
                            LogAssets.objects.create(
                                event=0, assets=assets, etime=datetime.now(), purchase=purchase, price=price,
                                log_user=request.user.username, pos=pos_obj, user=data['user'])

                        success = True
                    elif assets_type == '列管资产':
                        """
                        列管资产入库
                        数据格式如下
                        [
                            {
                                'specification': '荣耀5', 'using_department': '运维部', 'ctype_text': '电子设备', 'id': 2,
                                'name': '手机', 'pos': '广州创娱6F', 'brand': '华为', 'company_code_id': '4', 'ctype': '0',
                                'company_text': '广州创娱', 'supplier': '华为', 'pos_id': '11', 'supplier_id': '5',
                                'company_code': 'GZCY', 'purchase_id': 0, 'purchase': '是', 'price': 2000,},
                            {
                                'specification': '荣耀5', 'using_department': '运维部', 'ctype_text': '电子设备', 'id': 10,
                                'name': '手机', 'pos': '广州创娱6F', 'brand': '华为', 'company_code_id': '4', 'ctype': '0',
                                'company_text': '广州创娱','supplier': '华为', 'pos_id': '11', 'supplier_id': '5',
                                'company_code': 'GZCY', 'purchase_id': 0, 'purchase': '是', 'price': 2000,}
                        ]
                        """
                        for data in dataTable:
                            data.pop('pos')
                            data.pop('ctype_text')
                            data.pop('id')

                            data.pop('company_text')
                            company_code = data.pop('company_code')
                            company_code_id = data.pop('company_code_id')
                            company_obj = CompanyCode.objects.get(id=company_code_id)
                            data['company'] = company_obj

                            # 新购买的单价的问题
                            purchase = data.pop('purchase_id')
                            data.pop('purchase')
                            price = data.pop('price')

                            pos_id = data.pop('pos_id')
                            pos_obj = Position.objects.get(id=pos_id)
                            data['pos'] = pos_obj

                            supplier_id = data.pop('supplier_id')
                            data.pop('supplier')
                            if supplier_id == '0':
                                data['supplier'] = None
                            else:
                                data['supplier'] = Supplier.objects.get(id=supplier_id)

                            # 保管人就是录入人
                            data['user'] = request.user.username

                            # 添加与User表关联字段auth_user_id字段
                            data['auth_user_id'] = request.user.id

                            # 添加新所属组织架构
                            data['belongs_to_new_organization'] = data['using_department']

                            # 添加status
                            data['status'] = 0

                            # 添加资产编号
                            identifier = name_map_abbreviation.get(data['name'], None)

                            if identifier is None:
                                raise Exception('列管资产名称匹配不到标识')
                            data['assets_number'] = get_max_assets_number(company_code, identifier)

                            # 创建固定资产对象
                            assets = Assets.objects.create(**data)

                            # 固定资产入库日志
                            LogAssets.objects.create(
                                event=0, assets=assets, etime=datetime.now(), purchase=purchase, price=price,
                                log_user=request.user.username, pos=pos_obj, user=data['user'])

                        success = True
                    else:
                        """主机配件入库
                        数据格式如下
                        [
                            {
                                'smodel': 'i5-6700U', 'pos_id': '6',
                                'id': 3, 'pos': '10楼办公区', 'number': '2', 'sub_assets_type': 'CPU',
                                'supplier_id': 1, 'supplier': '戴尔',
                                'company_id': '4', 'company_name': '广州创娱',
                                'purchase_id': 0, 'purchase': '是', 'price': 2000
                            }
                        ]
                        """

                        for data in dataTable:

                            # 去掉一些没用的数据
                            data.pop('id')
                            data.pop('pos')

                            ctype = data.pop('sub_assets_type')

                            smodel = data.pop('smodel')
                            brand = data.pop('brand')

                            pos_id = data.pop('pos_id')
                            pos_obj = Position.objects.get(id=pos_id)
                            # 重新添加pos的key
                            data['pos'] = pos_obj

                            # 添加供应商
                            data.pop('supplier')
                            supplier_id = data.pop('supplier_id')
                            data['supplier'] = Supplier.objects.get(id=supplier_id)

                            # 新购买的单价的问题
                            purchase = data.pop('purchase_id')
                            data.pop('purchase')
                            price = data.pop('price')

                            # 添加公司
                            data.pop('company_name')
                            company_obj = CompanyCode.objects.get(id=data.pop('company_id'))
                            data['company'] = company_obj

                            # 添加status
                            data['status'] = 0

                            # 如果没有填写用户，默认就是当前用户
                            if not data.get('user', None):
                                data['user'] = request.user.username

                            # 创建或者获取配件对象
                            part_model = get_or_create_part_model(ctype, smodel, data['supplier'], company_obj, brand)

                            # 创建或者更新配件的状态
                            create_or_update_part_model_status(part_model, **data)

                            # 入库日志
                            LogAssets.objects.create(
                                event=0, part_model=part_model, etime=datetime.now(), number=data['number'],
                                price=price,
                                log_user=request.user.username, pos=pos_obj, user=data['user'], purchase=purchase)

                        success = True
                elif assets_event == '领用':
                    if assets_type == '固定资产' or assets_type == '列管资产':
                        """固定资产领用
                        数据格式:
                        [
                            {
                                'user': '张文辉', 'pos': '9楼办公区',
                                'assets_number': 'DZ20170001', 'assets': '9', 'id': 2, 'pos_id': '4',
                            }
                        ]
                        """

                        for data in dataTable:
                            # 去掉一些没用的数据
                            data.pop('id')
                            data.pop('pos')
                            data.pop('assets')

                            assets_number = data.pop('assets_number').split('-')[0]

                            pos_obj = Position.objects.get(id=data.pop('pos_id'))
                            assets = Assets.objects.get(assets_number=assets_number)

                            # 如果不是库存状态，则引发一个异常
                            if assets.status != 0:
                                raise StatusError('%s: 已经不是库存状态' % (assets.assets_number))

                            assets.user = data.get('user')
                            user = User.objects.get(username=assets.user)
                            assets.auth_user = user
                            assets.pos = pos_obj
                            new_organization = assets.get_ancestor()
                            assets.using_department = new_organization
                            assets.belongs_to_new_organization = new_organization
                            assets.status = 1
                            assets.warehousing_region = None
                            assets.save()

                            # 记录到日志
                            LogAssets.objects.create(
                                event=1, assets=assets, etime=datetime.now(),
                                log_user=request.user.username, pos=pos_obj, user=data['user'])

                        success = True
                    elif assets_type == '固定资产合并':
                        """固定资产的合并
                        数据格式
                        [
                            {
                                'id': 2, 'merge_assets_id': '4188', 'merge_assets': 'GZCYDZ20173273-机械硬盘-严文驰',
                                'assets_id': '2558', 'assets': 'GZCYDZ20170059-主机-毕长恒'
                            }
                        ]
                        """
                        for data in dataTable:
                            assets = Assets.objects.get(id=data.pop('assets_id'))
                            merge_assets = Assets.objects.get(id=data.pop('merge_assets_id'))

                            # 检查主资产的状态
                            if assets.status != 1:
                                raise StatusError('主资产%s的状态不是领用' % (assets.assets_number))

                            # 检查合并资产的状态
                            if merge_assets.status != 0:
                                raise StatusError('合并资产%s的状态不是库存' % (merge_assets.assets_number))

                            # 合并资产到主资产中
                            merge_assets.belongs_to_assets = assets
                            merge_assets.user = assets.user
                            user = User.objects.get(username=assets.user)
                            merge_assets.auth_user = user
                            merge_assets.belongs_to_new_organization = assets.belongs_to_new_organization
                            merge_assets.using_department = assets.belongs_to_new_organization
                            merge_assets.pos = assets.pos
                            merge_assets.status = 1
                            merge_assets.save()

                            # 记录到日志
                            LogAssets.objects.create(
                                event=1, assets=merge_assets, etime=datetime.now(), log_user=request.user.username,
                                pos=merge_assets.pos, user=merge_assets.user)
                        success = True

                    else:
                        """主机配件领用
                        数据格式
                        [
                            {
                                'pos': '9楼机房', 'smodel': '金士顿16G', 'number': '1', 'part_model_status': '3',
                                'ctype': '内存', 'id': 2, 'assets': '11', 'assets_number': 'DZ20170004',
                            }
                        ]
                        """

                        for data in dataTable:
                            assets_number = data.pop('assets_number').split('-')[0]

                            # 检查库存是否足够
                            part_model_status = PartModelStatus.objects.get(id=data.get('part_model_status'))
                            assets = Assets.objects.get(assets_number=assets_number)
                            number = int(data.get('number'))

                            if part_model_status.number < number:
                                raise StockNotEnough('%s: %s 库存数量不够' % (data.get('pos'), data.get('smodel')))
                            # 如果刚好
                            elif part_model_status.number == number:
                                part_model = part_model_status.part_model
                                part_model_status.delete()
                                data['status'] = 1
                                data['pos'] = assets.pos
                                data['user'] = assets.user
                                create_or_update_assets_with_part_model(part_model, assets, data.get('number'))
                            else:
                                # 库存记录减少
                                part_model_status.number -= int(data.get('number'))
                                part_model_status.save()

                                # 增加或者更新领用的记录
                                data['status'] = 1
                                data['pos'] = assets.pos
                                data['user'] = assets.user

                                # create_or_update_part_model_status(part_model_status.part_model, **data)

                                # 更新固定资产和配件的中间表
                                create_or_update_assets_with_part_model(
                                    part_model_status.part_model, assets, data.get('number'))

                            # 日志
                            LogAssets.objects.create(
                                event=1, part_model=part_model_status.part_model, etime=datetime.now(), assets=assets,
                                number=data['number'], log_user=request.user.username, pos=assets.pos, user=assets.user)

                        success = True
                elif assets_event == '调拨':
                    if assets_type == '固定资产' or assets_type == '列管资产':
                        """调拨列管资产
                        数据格式:
                        [
                            {
                                'user': '梁保明', 'assets': '9', 'pos': '10楼办公区', 'using_department': '运维部',
                                'id': 2, 'pos_id': '6', 'assets_number': 'DZ20170001',
                                'company_code_id': 1, 'company_code': 'name'
                            }
                        ]
                        """
                        for data in dataTable:
                            assets = Assets.objects.get(id=data.get('assets'))
                            pos_obj = Position.objects.get(id=data.get('pos_id'))
                            assets.pos = pos_obj
                            # 记录下前领用人
                            pre_user = assets.user if assets.user else ''
                            assets.user = data.get('user')
                            user = User.objects.get(username=data.get('user'))
                            assets.auth_user = user
                            new_organization = assets.get_ancestor()
                            assets.using_department = new_organization
                            assets.belongs_to_new_organization = new_organization
                            assets.save()

                            # 记录到日志
                            LogAssets.objects.create(
                                event=3, assets=assets, etime=datetime.now(), pre_user=pre_user,
                                log_user=request.user.username, pos=pos_obj, user=data['user'])

                        success = True
                    else:
                        """调拨主机配件
                        数据格式:
                        [
                            {
                                'id': 2, 'new_assets': '9', 'raw_assets': '11', 'smodel': '金士顿16G',
                                'number': '1', 'ctype': '内存', 'raw_assets_part_model': '11',
                                'raw_assets_number': 'DZ20170004', 'new_assets_number': 'DZ20170004'
                            }
                        ]
                        """
                        for data in dataTable:
                            number = int(data.get('number'))
                            raw_assets_part_model = AssetsPartModel.objects.get(id=data.get('raw_assets_part_model'))
                            new_assets = Assets.objects.get(id=data.get('new_assets'))

                            # 前一个领用人
                            pre_user = raw_assets_part_model.assets.user if raw_assets_part_model.assets.user else ''

                            # 判断原资产的数量是否足够
                            if raw_assets_part_model.number < number:
                                raise AssetsPartModelNotEnouth(
                                    '%s: %s: %s数量不够' %
                                    (data.get('raw_assets_number'), data.get('ctype'), data.get('smodel')))
                            # 如果刚好的话，原资产需要删除掉记录
                            elif raw_assets_part_model.number == number:
                                raw_assets_part_model.delete()
                                create_or_update_assets_with_part_model(raw_assets_part_model.part_model, new_assets,
                                                                        number)
                            # 原资产的配件记录数目减少，新资产的更新
                            else:
                                raw_assets_part_model.number -= number
                                raw_assets_part_model.save()
                                create_or_update_assets_with_part_model(raw_assets_part_model.part_model, new_assets,
                                                                        number)

                            # 日志
                            LogAssets.objects.create(
                                event=3, part_model=raw_assets_part_model.part_model, etime=datetime.now(),
                                pre_user=pre_user, number=number, log_user=request.user.username,
                                pos=new_assets.pos, user=new_assets.user)

                        success = True
                elif assets_event == '回收':
                    if assets_type == '固定资产' or assets_type == '列管资产':
                        """回收固定资产
                        数据格式:
                        [
                            {
                                'assets_number': 'DZ20170004', 'id': 2,
                                'pos': '10楼机房', 'pos_id': '7', 'assets': '11'
                            }
                        ]
                        """
                        for data in dataTable:
                            pos_obj = Position.objects.get(id=data.get('pos_id'))
                            assets = Assets.objects.get(id=data.get('assets'))
                            warehousing_region_id = data.get('warehousing_region_id', '0')
                            if str(warehousing_region_id) != '0':
                                warehousing_region = AssetsWarehousingRegion.objects.get(id=warehousing_region_id)
                                assets.warehousing_region = warehousing_region
                            assets.status = 0
                            assets.pos = pos_obj
                            # 记录下前领用人
                            pre_user = assets.user if assets.user else ''
                            assets.user = request.user.username
                            user = User.objects.get(username=request.user.username)
                            assets.auth_user = user
                            assets.using_department = assets.get_ancestor()
                            assets.belongs_to_new_organization = assets.get_ancestor()
                            assets.save()

                            # 日志
                            LogAssets.objects.create(
                                event=4, assets=assets, etime=datetime.now(), pre_user=pre_user,
                                log_user=request.user.username, pos=pos_obj, user=request.user.username)

                        success = True
                    elif assets_type == '从固定资产回收主机配件':
                        """从某个固定资产中回收一个列管资产
                        数据格式：
                        [
                            {
                                'raw_assets': '9', 'user': '建军', 'id': 2, 'pos_id': '7',
                                'ctype': '内存', 'number': '1', 'raw_assets_part_model': '12',
                                'assets_number': 'DZ20170001', 'pos': '10楼机房', 'smodel': '金士顿16G'
                            }
                        ]
                        """
                        for data in dataTable:
                            # 所属的固定资产
                            raw_assets = Assets.objects.get(id=data.get('raw_assets'))
                            raw_assets_part_model = AssetsPartModel.objects.get(id=data.get('raw_assets_part_model'))
                            part_model = raw_assets_part_model.part_model
                            number = int(data.get('number'))

                            # 前一个领用人
                            pre_user = raw_assets.user if raw_assets.user else ''

                            data.pop('pos')

                            pos_obj = Position.objects.get(id=data.get('pos_id'))
                            data['pos'] = pos_obj

                            # 添加状态
                            data['status'] = 0

                            # 如果数量不够
                            if raw_assets_part_model.number < number:
                                raise AssetsPartModelNotEnouth(
                                    '%s: %s: %s 数量不够' % (
                                        data.get('assets_number'), data.get('ctype'), data.get('smodel')))
                            # 如果刚好够，固定资产删掉关联，更新或者创建列管资产的库存
                            elif raw_assets_part_model.number == number:
                                raw_assets_part_model.delete()
                                create_or_update_part_model_status(part_model, **data)
                            # 如果大于回收的数量
                            else:
                                # raw_assets_part_model.number -= number
                                # raw_assets_part_model.save()
                                raw_assets_part_model.delete()
                                create_or_update_part_model_status(part_model, **data)

                            # 日志
                            LogAssets.objects.create(
                                assets=raw_assets, event=4, part_model=part_model, etime=datetime.now(),
                                pre_user=pre_user, number=number, log_user=request.user.username,
                                pos=pos_obj, user=data['user'])

                        success = True
                    elif assets_type == '从外借回收主机配件':
                        """回收，从外借回收列管资产
                        数据格式:
                        [
                            {
                                'pos': '子公司', 'ctype': 'CPU', 'part_model_status': '5',
                                'target_pos_id': '7', 'smodel': 'I5-6200G', 'target_pos': '10楼机房',
                                'pos_id': '8', 'number': '1', 'id': 2, 'user': '建军',
                                'company_code': '海南创娱', 'company_code_id': 1,
                                'to_company_code': '广州创娱', 'to_company_code_id': 2,
                            }
                        ]
                        """
                        for data in dataTable:
                            part_model_status = PartModelStatus.objects.get(id=data.get('part_model_status'))
                            part_model = part_model_status.part_model
                            number = int(data.get('number'))

                            # 前一个领用人
                            pre_user = part_model_status.user if part_model_status.user else ''

                            pos_obj = Position.objects.get(id=data.pop('target_pos_id'))
                            data['pos'] = pos_obj

                            # 添加库存状态
                            data['status'] = 0

                            # 回收归属的公司
                            to_company_obj = CompanyCode.objects.get(id=data.get('to_company_code_id'))

                            # 如果回收的数据不够
                            if part_model_status.number < number:
                                raise StockNotEnough(
                                    '%s: %s: %s 数量不够' % (data.get('pos'), data.get('ctype'), data.get('smodel')))
                            # 如果刚好，删掉配件状态表记录，更新库存记录
                            elif part_model_status.number == number:
                                part_model_status.delete()
                                supplier = part_model_status.part_model.supplier
                                new_part_model = get_or_create_part_model(
                                    data.get('ctype'), data.get('smodel'), supplier, to_company_obj)
                                create_or_update_part_model_status(new_part_model, **data)
                            else:
                                part_model_status.number -= number
                                part_model_status.save()
                                supplier = part_model_status.part_model.supplier
                                new_part_model = get_or_create_part_model(
                                    data.get('ctype'), data.get('smodel'), supplier, to_company_obj)
                                create_or_update_part_model_status(new_part_model, **data)

                            # 日志
                            LogAssets.objects.create(
                                event=4, part_model=part_model, etime=datetime.now(), number=data['number'],
                                log_user=request.user.username, pos=pos_obj, user=data['user'], pre_user=pre_user)

                        success = True
                    elif assets_type == '回收合并固定资产':
                        """回收
                        回收合并固定资产
                        数据格式
                        [
                            {
                                'id': 2, 'merge_assets_id': '4188',
                                'merge_assets': 'GZCYDZ20173273-机械硬盘-毕长恒'
                            }
                        ]
                        """
                        for data in dataTable:
                            merge_assets = Assets.objects.get(id=data.pop('merge_assets_id'))

                            # 检查合并固定资产的状态
                            if merge_assets.status != 1:
                                raise StatusError('合并固定资产%s不是领用状态' % (merge_assets.assets_number))

                            # 记录前领用人
                            pre_user = merge_assets.user if merge_assets.user else ''
                            # 修改合并固定资产的值
                            merge_assets.status = 0
                            merge_assets.user = request.user.username
                            user = User.objects.get(username=request.user.username)
                            merge_assets.auth_user = user
                            merge_assets.using_department = merge_assets.belongs_to_new_organization = merge_assets.get_ancestor()
                            merge_assets.belongs_to_assets = None
                            merge_assets.save()

                            # log
                            LogAssets.objects.create(
                                event=4, assets=merge_assets, etime=datetime.now(), pre_user=pre_user,
                                log_user=request.user.username, pos=merge_assets.pos, user=request.user.username)
                        success = True
                elif assets_event == '外借':
                    if assets_type == '固定资产' or assets_type == '列管资产':
                        """固定资产外借
                        数据格式:
                        [
                            {
                                'assets': '11', 'pos_id': '3', 'assets_number': 'DZ20170004',
                                'user': '陈宇', 'pos': '6楼机房', 'using_department': '子公司', 'id': 2,
                                'company_code_id': 1, company_code: '海南创娱',
                            }
                        ]
                        """
                        for data in dataTable:
                            pos_obj = Position.objects.get(id=data.get('pos_id'))
                            company_obj = CompanyCode.objects.get(id=data.pop('company_code_id'))
                            assets = Assets.objects.get(id=data.get('assets'))

                            assets.status = 2
                            # assets.company = company_obj
                            assets.pos = pos_obj
                            assets.using_department = data.get('using_department')
                            pre_user = assets.user if assets.user else ''
                            assets.user = data.get('user')
                            user = User.objects.get(username=assets.user)
                            assets.auth_user = user
                            assets.using_department = assets.belongs_to_new_organization = assets.get_ancestor()
                            assets.save()

                            # 日志
                            LogAssets.objects.create(
                                event=2, assets=assets, etime=datetime.now(), pre_user=pre_user,
                                log_user=request.user.username, pos=pos_obj, user=data['user'])

                            success = True
                    else:
                        """外借列管资产
                        数据格式：
                        [
                            {
                                'target_pos_id': '8', 'pos': '9楼办公区', 'part_model_status': '1',
                                'pos_id': '4', 'ctype': 'CPU', 'target_pos': '子公司', 'number': '1',
                                'user': '陈宇', 'id': 2, 'smodel': 'I5-6200G',
                                'company_code': company_code, 'company_code_id': company_code_id,
                                'to_company_code': to_company_code, 'to_company_code_id': to_company_code_id,
                            }
                        ]
                        """
                        for data in dataTable:
                            part_model_status = PartModelStatus.objects.get(id=data.get('part_model_status'))
                            number = int(data.get('number'))

                            # 前一个领用人
                            pre_user = part_model_status.user if part_model_status.user else ''

                            if part_model_status.number < number:
                                raise AssetsPartModelNotEnouth(
                                    '%s: %s: %s 库存不够' % (data.get('pos'), data.get('ctype'), data.get('smodel')))
                            else:
                                # 库存数量减少
                                part_model_status.number -= number
                                part_model_status.save()

                                # 更新或者增加外借的记录
                                pos_obj = Position.objects.get(id=data.pop('target_pos_id'))
                                data['pos'] = pos_obj

                                data['status'] = 2

                                to_company_obj = CompanyCode.objects.get(id=data.pop('to_company_code_id'))
                                supplier = part_model_status.part_model.supplier

                                # 由于所属公司变了，需要重新创建一个part_model
                                # new_part_model = get_or_create_part_model(
                                #     data.get('ctype'), data.get('smodel'), supplier, to_company_obj)

                                create_or_update_part_model_status(part_model_status.part_model, **data)

                            # 日志
                            LogAssets.objects.create(
                                event=2, part_model=part_model_status.part_model, etime=datetime.now(),
                                pre_user=pre_user,
                                log_user=request.user.username, pos=pos_obj, user=data['user'], number=data['number'])

                        success = True
                elif assets_event == '损毁':
                    if assets_type == '固定资产' or assets_type == '列管资产':
                        """固定资产损毁
                        所需的数据
                        [
                            {
                                'assets': '10', 'using_department': '运维部',
                                'id': 2, 'assets_number': 'DZ20170003', 'pos': '10楼机房', 'pos_id': '7'
                            }
                        ]
                        """
                        for data in dataTable:
                            assets = Assets.objects.get(id=data.get('assets'))
                            pos_obj = Position.objects.get(id=data.get('pos_id'))

                            data['pos'] = pos_obj

                            assets.status = 4
                            assets.pos = pos_obj
                            assets.using_department = assets.belongs_to_new_organization = data.get('using_department')
                            pre_user = assets.user if assets.user else ''
                            assets.user = request.user.username
                            assets.auth_user_id = request.user.id
                            assets.save()

                            # 日志
                            LogAssets.objects.create(
                                event=5, assets=assets, etime=datetime.now(), pre_user=pre_user,
                                log_user=request.user.username, pos=pos_obj, user=request.user.username)

                        success = True
                    else:
                        """损毁主机配件
                        数据格式:
                        [
                            {
                                'number': '1', 'assets_number': 'DZ20170001', 'raw_assets': '9',
                                'smodel': '集成显卡', 'pos': '6楼机房', 'pos_id': '3', 'id': 2,
                                'ctype': '显卡', 'user': '杨振杰', 'raw_assets_part_model': '4'
                            }
                        ]
                        """
                        for data in dataTable:
                            raw_assets_part_model = AssetsPartModel.objects.get(id=data.get('raw_assets_part_model'))
                            part_model = raw_assets_part_model.part_model
                            number = int(data.get('number'))

                            # 前一个领用人
                            pre_user = raw_assets_part_model.assets.user if raw_assets_part_model.assets.user else ''

                            pos_obj = Position.objects.get(id=data.get('pos_id'))
                            data['pos'] = pos_obj

                            # 添加状态
                            data['status'] = 4

                            # 如果数量不够
                            if raw_assets_part_model.number < number:
                                raise AssetsPartModelNotEnouth(
                                    '%s: %s: %s' % (data.get('pos'), data.get('ctype'), data.get('smodel')))
                            # 如果数量刚刚好
                            elif raw_assets_part_model.number == number:
                                raw_assets_part_model.delete()
                                create_or_update_part_model_status(part_model, **data)
                            else:
                                raw_assets_part_model.number -= number
                                raw_assets_part_model.save()
                                create_or_update_part_model_status(part_model, **data)

                            # 日志
                            LogAssets.objects.create(
                                event=5, part_model=part_model, etime=datetime.now(), pre_user=pre_user,
                                number=number, log_user=request.user.username, pos=pos_obj, user=data['user'])

                        success = True
                elif assets_event == '清理':
                    if assets_type == '固定资产' or assets_type == '列管资产':
                        """清理固定资产
                        数据格式
                        [
                            {
                                'assets_number': 'DZ20170003', 'assets': '10',
                            }
                        ]
                        """
                        for data in dataTable:
                            assets = Assets.objects.get(id=data.get('assets'))

                            assets.status = 5
                            pre_user = assets.user if assets.user else ''
                            assets.save()

                            # 日志
                            LogAssets.objects.create(
                                event=6, assets=assets, etime=datetime.now(), pre_user=pre_user,
                                log_user=request.user.username, pos=assets.pos, user=assets.user)

                        success = True
                    else:
                        """清理主机配件
                        数据格式：
                        [
                            {
                                'pos_id': '3', 'user': '李天来', 'ctype': 'CPU', 'pos': '6楼机房',
                                'target_pos': '9楼机房', 'id': 2, 'target_pos_id': '5', 'smodel': 'I5-6200G',
                                'part_model_status': '8', 'number': '7'
                            }
                        ]
                        """
                        for data in dataTable:
                            part_model_status = PartModelStatus.objects.get(id=data.get('part_model_status'))
                            part_model = part_model_status.part_model
                            number = int(data.get('number'))

                            # 前一个领用人
                            pre_user = part_model_status.user if part_model_status.user else ''

                            pos = data.get('pos')
                            pos_obj = Position.objects.get(id=data.get('pos_id'))
                            data['pos'] = pos_obj

                            # 添加状态
                            data['status'] = 5

                            # 如果数量不够
                            if part_model_status.number < number:
                                raise PartModelStatusNotEnouth(
                                    '%s: %s: %s 数量不够' % (pos, data.get('ctype'), data.get('smodel')))
                            # 如果刚好
                            elif part_model_status.number == number:
                                part_model_status.delete()
                                create_or_update_part_model_status(part_model, **data)
                            else:
                                part_model_status.number -= number
                                part_model_status.save()
                                create_or_update_part_model_status(part_model, **data)

                            # 日志
                            LogAssets.objects.create(
                                event=6, part_model=part_model, etime=datetime.now(), pre_user=pre_user,
                                number=number, log_user=request.user.username, pos=pos_obj, user=data['user'])

                        success = True
                elif assets_event == '位置':
                    if assets_type == '位置变更':
                        """位置变更事件
                        数据格式:
                        [
                            {
                                'id': 2, 'user': '严文驰', 'pos_id': '27', 'company_code': '广州创娱',
                                'company_code_id': '4', 'pos': '露乐大厦2L'
                            },
                            {
                                'id': 2, 'user': '严文驰', 'pos_id': '27', 'company_code': '广州创娱',
                                'company_code_id': '4', 'pos': '露乐大厦2L'
                            },
                        ]

                        找到该用户下状态为领用的固定资产和列管资产，然后更新他们的位置
                        """

                        for data in dataTable:
                            company_obj = CompanyCode.objects.get(id=data.get('company_code_id'))
                            pos_obj = Position.objects.get(id=data.get('pos_id'))

                            all_assets = Assets.objects.filter(company=company_obj, user=data.get('user'), status=1)

                            # 更新位置
                            for assets in all_assets:
                                assets.pos = pos_obj
                                assets.user = data.get('user')
                                user = User.objects.get(username=data.get('user'))
                                assets.auth_user = user
                                assets.using_department = assets.belongs_to_new_organization = assets.get_ancestor()
                                assets.save()

                            # 日志
                            for assets in all_assets:
                                pre_user = assets.user if assets.user else ''
                                LogAssets.objects.create(
                                    event=7, assets=assets, etime=datetime.now(), pre_user=pre_user,
                                    log_user=request.user.username, pos=pos_obj, user=data.get('user'))
                        success = True
                elif assets_event == '变卖':
                    if assets_type == '固定资产' or assets_type == '列管资产':
                        """固定资产变卖
                        所需的数据
                        [
                            {
                                'assets': '10', 'using_department': '运维部',
                                'id': 2, 'assets_number': 'DZ20170003', 'pos': '10楼机房', 'pos_id': '7'
                            }
                        ]
                        """
                        for data in dataTable:
                            assets = Assets.objects.get(id=data.get('assets'))
                            pos_obj = Position.objects.get(id=data.get('pos_id'))

                            data['pos'] = pos_obj

                            assets.status = 6
                            assets.pos = pos_obj
                            assets.using_department = assets.belongs_to_new_organization = data.get('using_department')
                            pre_user = assets.user if assets.user else ''
                            assets.user = request.user.username
                            assets.auth_user_id = request.user.id
                            assets.save()

                            # 日志
                            LogAssets.objects.create(
                                event=12, assets=assets, etime=datetime.now(), pre_user=pre_user,
                                log_user=request.user.username, pos=pos_obj, user=request.user.username)

                        success = True
                    else:
                        """变卖主机配件
                        数据格式:
                        [
                            {
                                'number': '1', 'assets_number': 'DZ20170001', 'raw_assets': '9',
                                'smodel': '集成显卡', 'pos': '6楼机房', 'pos_id': '3', 'id': 2,
                                'ctype': '显卡', 'user': '杨振杰', 'raw_assets_part_model': '4'
                            }
                        ]
                        """
                        for data in dataTable:
                            raw_assets_part_model = AssetsPartModel.objects.get(id=data.get('raw_assets_part_model'))
                            part_model = raw_assets_part_model.part_model
                            number = int(data.get('number'))

                            # 前一个领用人
                            pre_user = raw_assets_part_model.assets.user if raw_assets_part_model.assets.user else ''

                            pos_obj = Position.objects.get(id=data.get('pos_id'))
                            data['pos'] = pos_obj

                            # 添加状态
                            data['status'] = 6

                            # 如果数量不够
                            if raw_assets_part_model.number < number:
                                raise AssetsPartModelNotEnouth(
                                    '%s: %s: %s' % (data.get('pos'), data.get('ctype'), data.get('smodel')))
                            # 如果数量刚刚好
                            elif raw_assets_part_model.number == number:
                                raw_assets_part_model.delete()
                                create_or_update_part_model_status(part_model, **data)
                            else:
                                raw_assets_part_model.number -= number
                                raw_assets_part_model.save()
                                create_or_update_part_model_status(part_model, **data)

                            # 日志
                            LogAssets.objects.create(
                                event=12, part_model=part_model, etime=datetime.now(), pre_user=pre_user,
                                number=number, log_user=request.user.username, pos=pos_obj, user=data['user'])

                        success = True

        except Supplier.DoesNotExist:
            msg = '供应商不存在'
            success = False
        except PartModelStatus.DoesNotExist:
            msg = '列管资产记录不存在'
            success = False
        except CompanyCode.DoesNotExist:
            msg = '公司不存在'
            success = False
        except AssetsPartModelNotEnouth as e:
            msg = str(e)
            success = False
        except StockNotEnough as e:
            msg = str(e)
            success = False
        except StatusError as e:
            msg = str(e)
            success = False
        except IntegrityError:
            msg = '资产记录有重复'
            success = False
        except User.DoesNotExist:
            msg = '用户不存在'
            success = False
        except Assets.DoesNotExist:
            msg = '资产编号不存在'
            success = False
        except Position.DoesNotExist:
            msg = '位置不存在'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def assets_reception(request):
    '资产领用页面'
    if request.method == 'GET':
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            head = {'value': '固定资产查询', 'username': request.user.username}
            all_company = [{'id': x.id, 'text': x.name} for x in CompanyCode.objects.all()]
            all_assets_name = [x['name'] for x in Assets.objects.values('name').annotate(dcount=Count('name'))]
            all_cpu = list(set([x['mounting_part__smodel'] for x in
                                Assets.objects.filter(mounting_part__ctype="CPU", status__in=[0, 1, 2, 3]).values(
                                    'mounting_part__smodel').distinct()]))
            all_board = list(set([x.smodel for x in PartModel.objects.filter(ctype='主板')]))
            all_ssd = list(set([x.smodel for x in PartModel.objects.filter(ctype='固态硬盘')]))
            all_disk = list(set([x.smodel for x in PartModel.objects.filter(ctype='机械硬盘')]))
            all_mem = list(set([x.smodel for x in PartModel.objects.filter(ctype='内存')]))
            all_graphics = list(set([x.smodel for x in PartModel.objects.filter(ctype='显卡')]))
            all_supplier = [{'id': x.id, 'name': x.name} for x in Supplier.objects.all()]
            all_user = [{'id': x.id, 'name': x.username} for x in User.objects.all()]
            all_using_department = [{'id': x.id, 'name': x.name} for x in Group.objects.all()]
            all_brand = [x['brand'] for x in Assets.objects.values('brand').annotate(dcount=Count('brand'))]
            all_new_organization = [x['belongs_to_new_organization'] if x['belongs_to_new_organization'] else '无' for x
                                    in
                                    Assets.objects.filter(status__in=[0, 1, 2, 3]).values(
                                        'belongs_to_new_organization').distinct()]
            all_new_organization.extend([x.get_ancestors_name() for x in OrganizationMptt.objects.filter(type=1)])
            all_new_organization = sorted(list(set(all_new_organization)))
            all_pos = [{'id': x.id, 'text': x.name} for x in Position.objects.all()]
            all_warehousing_region = [{'id': x.id, 'text': x.name} for x in AssetsWarehousingRegion.objects.all()]
            return render(request, 'assets_reception.html', {
                'head': head, 'all_cpu': all_cpu, 'all_board': all_board, 'all_assets_name': all_assets_name,
                'all_ssd': all_ssd, 'all_disk': all_disk, 'all_mem': all_mem, 'all_brand': all_brand,
                'all_graphics': all_graphics, 'all_supplier': all_supplier, 'all_user': all_user,
                'all_company': all_company, 'all_using_department': all_using_department,
                'all_new_organization': all_new_organization, 'all_pos': all_pos,
                'all_warehousing_region': all_warehousing_region})
        else:
            return render(request, '403.html')


def get_assets_change_history(request):
    """获取资产变更记录"""
    if request.method == "POST":
        if request.user.is_superuser:
            assets_id = json.loads(request.body.decode('utf-8')).get('id')
            log_assets = LogAssets.objects.filter(assets_id=assets_id).order_by('etime')
            data = {'data': [i.show_all() for i in log_assets]}
            return JsonResponse(data)
        else:
            raise PermissionDenied


def get_assets_reception(request):
    """获取固定资产数据"""

    if request.method == "POST":
        if request.user.is_superuser or request.user.has_perm('it_assets.change_assets_company') or \
                request.user.has_perm('users.edit_it_assets'):
            id = json.loads(request.body.decode('utf-8')).get('id')
            obj = Assets.objects.get(id=id)
            edit_data = obj.edit_data()
            return JsonResponse(edit_data)
        else:
            raise PermissionDenied


def edit_assets_reception(request):
    """修改固定资产和列管资产数据"""
    if request.method == "POST":
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        id = raw_data.pop('id')

        try:
            if request.user.is_superuser or request.user.has_perm('it_assets.change_assets_company') or \
                    request.user.has_perm('users.edit_it_assets'):
                obj = Assets.objects.get(id=id)
                supplier = raw_data.get('supplier')
                company = raw_data.get('company')
                pre_company = obj.company
                company_obj = obj.company
                if str(supplier) == '0':
                    supplier = None
                else:
                    supplier = Supplier.objects.get(id=supplier)
                if str(company) == '0':
                    company = None
                else:
                    current_company = CompanyCode.objects.get(id=company)
                    company_obj = current_company
                pos = Position.objects.get(id=raw_data.get('pos'))
                warehousing_region_id = raw_data.get('warehousing_region')
                if str(warehousing_region_id) != '0':
                    warehousing_region = AssetsWarehousingRegion.objects.get(id=warehousing_region_id)
                else:
                    warehousing_region = None
                user = raw_data.get('user')
                brand = raw_data.get('brand')
                remark = raw_data.get('remark')
                current_cpu = raw_data.get('cpu', '')
                current_mem = raw_data.get('mem', '')
                current_hdd = raw_data.get('hdd', '')
                current_ssd = raw_data.get('ssd', '')
                current_board = raw_data.get('board', '')
                current_graphics = raw_data.get('graphics', '')
                current_specification = raw_data.get('specification', '')
                pre_cpu = ','.join([str(x.brand or '') + x.smodel for x in obj.mounting_part.filter(ctype='CPU')])
                pre_ssd = ','.join([str(x.brand or '') + x.smodel for x in obj.mounting_part.filter(ctype='固态硬盘')])
                pre_hdd = ','.join([str(x.brand or '') + x.smodel for x in obj.mounting_part.filter(ctype='机械硬盘')])
                pre_mem = ','.join([str(x.brand or '') + x.smodel for x in obj.mounting_part.filter(ctype='内存')])
                pre_graphics = ','.join([str(x.brand or '') + x.smodel for x in obj.mounting_part.filter(ctype='显卡')])
                pre_board = ','.join([str(x.brand or '') + x.smodel for x in obj.mounting_part.filter(ctype='主板')])
                pre_specification = obj.specification
                """
                如果cpu/内存/主板/硬盘/规格发生变更时，记录变更日志
                """
                if pre_cpu != current_cpu:
                    LogAssets.objects.create(
                        event=9, assets=obj, part_model=None, etime=datetime.now(),
                        log_user=request.user, pos=obj.pos, user=obj.user, ctype='CPU',
                        pre_configuration=pre_cpu, current_configuration=current_cpu)
                if pre_mem != current_mem:
                    LogAssets.objects.create(
                        event=9, assets=obj, part_model=None, etime=datetime.now(),
                        log_user=request.user, pos=obj.pos, user=obj.user, ctype='内存',
                        pre_configuration=pre_mem, current_configuration=current_mem)
                if pre_hdd != current_hdd:
                    LogAssets.objects.create(
                        event=9, assets=obj, part_model=None, etime=datetime.now(),
                        log_user=request.user, pos=obj.pos, user=obj.user, ctype='机械硬盘',
                        pre_configuration=pre_hdd, current_configuration=current_hdd)
                if pre_ssd != current_ssd:
                    LogAssets.objects.create(
                        event=9, assets=obj, part_model=None, etime=datetime.now(),
                        log_user=request.user, pos=obj.pos, user=obj.user, ctype='固态硬盘',
                        pre_configuration=pre_ssd, current_configuration=current_ssd)
                if pre_graphics != current_graphics:
                    LogAssets.objects.create(
                        event=9, assets=obj, part_model=None, etime=datetime.now(),
                        log_user=request.user, pos=obj.pos, user=obj.user, ctype='显卡',
                        pre_configuration=pre_graphics, current_configuration=current_graphics)
                if pre_board != current_board:
                    LogAssets.objects.create(
                        event=9, assets=obj, part_model=None, etime=datetime.now(),
                        log_user=request.user, pos=obj.pos, user=obj.user, ctype='主板',
                        pre_configuration=pre_board, current_configuration=current_board)

                if pre_specification != current_specification:
                    LogAssets.objects.create(
                        event=9, assets=obj, part_model=None, etime=datetime.now(),
                        log_user=request.user, pos=obj.pos, user=obj.user, ctype='规格',
                        pre_configuration=pre_specification, current_configuration=current_specification)

                # 清空关联关系，重新创建配件对象
                obj.mounting_part.clear()

                # 创建配件对象
                list_cpu_obj_numer = create_or_get_part_model('CPU', current_cpu, company_obj)
                list_ssd_obj_numer = create_or_get_part_model('固态硬盘', current_ssd, company_obj)
                list_disk_obj_numer = create_or_get_part_model('机械硬盘', current_hdd, company_obj)
                list_mem_obj_numer = create_or_get_part_model('内存', current_mem, company_obj)
                list_graphics_obj_numer = create_or_get_part_model('显卡', current_graphics, company_obj)
                list_board_obj_number = create_or_get_part_model('主板', current_board, company_obj)

                # 固定资产和列管资产进行关联
                # list_cpu_obj_numer # ===> [{'obj': '8G', 'number': 2}, {'obj': '16G', 'number': 1}]
                # cpu
                for x in list_cpu_obj_numer:
                    for n in range(0, x['number']):
                        AssetsPartModel.objects.create(assets=obj, part_model=x['obj'], number=1)

                # ssd
                for x in list_ssd_obj_numer:
                    # AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=x['number'])
                    for n in range(0, x['number']):
                        AssetsPartModel.objects.create(assets=obj, part_model=x['obj'], number=1)

                # disk
                for x in list_disk_obj_numer:
                    # AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=x['number'])
                    for n in range(0, x['number']):
                        AssetsPartModel.objects.create(assets=obj, part_model=x['obj'], number=1)

                # mem
                for x in list_mem_obj_numer:
                    # AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=x['number'])
                    for n in range(0, x['number']):
                        AssetsPartModel.objects.create(assets=obj, part_model=x['obj'], number=1)

                # graphics
                for x in list_graphics_obj_numer:
                    AssetsPartModel.objects.create(assets=obj, part_model=x['obj'], number=x['number'])

                # board
                for x in list_board_obj_number:
                    # AssetsPartModel.objects.create(assets=assets, part_model=x['obj'], number=x['number'])
                    for n in range(0, x['number']):
                        AssetsPartModel.objects.create(assets=obj, part_model=x['obj'], number=1)

                # new_organization = raw_data.get('new_organization')
                pre_user = obj.user
                obj.supplier = supplier
                obj.company = current_company
                obj.pos = pos
                obj.warehousing_region = warehousing_region
                obj.user = user
                user_obj = User.objects.get(username=user)
                obj.auth_user = user_obj
                new_organization = obj.get_ancestor()
                obj.brand = brand
                obj.specification = current_specification
                obj.remark = remark
                # 如果使用人变更了， 记录日志
                if pre_user != user:
                    LogAssets.objects.create(
                        event=3, assets=obj, part_model=None, etime=datetime.now(),
                        log_user=request.user, pos=obj.pos, user=obj.user)
                if pre_company != current_company:
                    LogAssets.objects.create(
                        event=11, assets=obj, part_model=None, etime=datetime.now(),
                        log_user=request.user, pos=obj.pos, user=obj.user,
                        pre_configuration=pre_company.name if pre_company else '',
                        current_configuration=current_company.name)
                obj.using_department = new_organization
                obj.belongs_to_new_organization = new_organization
                obj.save()
                success = True
            else:
                raise PermissionDenied
        except PermissionDenied:
            msg = '权限拒绝'
            success = False
        except Assets.DoesNotExist:
            msg = '没有找到当前的资产'
            success = False
        except Supplier.DoesNotExist:
            msg = '供应商找不到'
            success = False
        except User.DoesNotExist:
            msg = '找不到该cmdb系统用户,请重新选择其他用户或新建该用户'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        return JsonResponse({'data': success, 'msg': msg})


def shell_assets_reception(request):
    '列管资产页面'
    if request.method == 'GET':
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            head = {'value': '列管资产查询', 'username': request.user.username}
            all_company = [{'id': x.id, 'text': x.name} for x in CompanyCode.objects.all()]
            all_assets_name = [
                x['name'] for x in Assets.objects.exclude(
                    assets_number__icontains='DZ').values('name').annotate(dcount=Count('name'))
            ]
            all_supplier = [{'id': x.id, 'name': x.name} for x in Supplier.objects.all()]
            all_user = [{'id': x.id, 'name': x.username} for x in User.objects.all()]
            all_using_department = [{'id': x.id, 'name': x.name} for x in Group.objects.all()]
            all_new_organization = [
                x['belongs_to_new_organization'] for x in
                Assets.objects.values('belongs_to_new_organization').
                    annotate(dcount=Count('belongs_to_new_organization'))
            ]
            return render(request, 'shell_assets_reception.html', {
                'head': head, 'all_assets_name': all_assets_name,
                'all_supplier': all_supplier, 'all_company': all_company, 'all_user': all_user,
                'all_using_department': all_using_department, 'all_new_organization': all_new_organization})
        else:
            return render(request, '403.html')


def sub_assets_reception(request):
    """主机配件页面"""
    if request.method == 'GET':
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            head = {'value': '主机配件查询', 'username': request.user.username}
            all_company = [{'id': x.id, 'text': x.name} for x in CompanyCode.objects.all()]
            all_cpu = [
                x.part_model.smodel
                for x in PartModelStatus.objects.select_related('part_model').filter(part_model__ctype='CPU')
            ]
            all_board = [
                x.part_model.smodel
                for x in PartModelStatus.objects.select_related('part_model').filter(part_model__ctype='主板')
            ]
            all_ssd = [
                x.part_model.smodel
                for x in PartModelStatus.objects.select_related('part_model').filter(part_model__ctype='固态硬盘')
            ]
            all_disk = [
                x.part_model.smodel
                for x in PartModelStatus.objects.select_related('part_model').filter(part_model__ctype='机械硬盘')
            ]
            all_mem = [
                x.part_model.smodel
                for x in PartModelStatus.objects.select_related('part_model').filter(part_model__ctype='内存')
            ]
            all_graphics = [
                x.part_model.smodel
                for x in PartModelStatus.objects.select_related('part_model').filter(part_model__ctype='显卡')
            ]
            all_users = [{'id': x.id, 'text': x.username} for x in User.objects.all()]

            """配件数量统计"""
            # 按配件类型统计
            ctype_count = PartModelStatus.objects.filter(status=0).values('part_model__ctype').annotate(
                total=Sum('number'))
            # 内存按型号统计
            mem_smodel_count = PartModelStatus.objects.filter(part_model__ctype='内存', status=0).values(
                'part_model__smodel').annotate(
                total=Sum('number'))
            # 内存按品牌统计
            mem_brand_count = PartModelStatus.objects.filter(part_model__ctype='内存', status=0).values(
                'part_model__brand').annotate(
                total=Sum('number'))
            # 内存按公司统计
            mem_company_count = PartModelStatus.objects.filter(part_model__ctype='内存', status=0).values(
                'part_model__company__name').annotate(
                total=Sum('number'))
            # 机械硬盘按型号统计
            hdd_smodel_count = PartModelStatus.objects.filter(part_model__ctype='机械硬盘', status=0).values(
                'part_model__smodel').annotate(
                total=Sum('number'))
            # 机械硬盘按品牌统计
            hdd_brand_count = PartModelStatus.objects.filter(part_model__ctype='机械硬盘', status=0).values(
                'part_model__brand').annotate(
                total=Sum('number'))
            # 机械硬盘按公司统计
            hdd_company_count = PartModelStatus.objects.filter(part_model__ctype='机械硬盘', status=0).values(
                'part_model__company__name').annotate(
                total=Sum('number'))
            # 固态硬盘按型号统计
            ssd_smodel_count = PartModelStatus.objects.filter(part_model__ctype='固态硬盘', status=0).values(
                'part_model__smodel').annotate(
                total=Sum('number'))
            # 固态硬盘按品牌统计
            ssd_brand_count = PartModelStatus.objects.filter(part_model__ctype='固态硬盘', status=0).values(
                'part_model__brand').annotate(
                total=Sum('number'))
            # 固态硬盘按公司统计
            ssd_company_count = PartModelStatus.objects.filter(part_model__ctype='固态硬盘', status=0).values(
                'part_model__company__name').annotate(
                total=Sum('number'))
            # CPU按品牌统计
            cpu_brand_count = PartModelStatus.objects.filter(part_model__ctype='CPU', status=0).values(
                'part_model__brand').annotate(
                total=Sum('number'))
            # CPU按公司统计
            cpu_company_count = PartModelStatus.objects.filter(part_model__ctype='CPU', status=0).values(
                'part_model__company__name').annotate(
                total=Sum('number'))
            # 显卡按品牌统计
            graphics_brand_count = PartModelStatus.objects.filter(part_model__ctype='显卡', status=0).values(
                'part_model__brand').annotate(
                total=Sum('number'))
            # 显卡按品牌统计
            graphics_company_count = PartModelStatus.objects.filter(part_model__ctype='显卡', status=0).values(
                'part_model__company__name').annotate(
                total=Sum('number'))

            return render(request, 'sub_assets_reception.html', {
                'head': head, 'all_cpu': all_cpu, 'all_board': all_board, 'all_ssd': all_ssd, 'all_mem': all_mem,
                'all_graphics': all_graphics, 'all_disk': all_disk, 'all_company': all_company, 'all_users': all_users,
                'ctype_count': ctype_count, 'mem_smodel_count': mem_smodel_count, 'mem_brand_count': mem_brand_count,
                'mem_company_count': mem_company_count, 'hdd_company_count': hdd_company_count,
                'ssd_company_count': ssd_company_count, 'cpu_company_count': cpu_company_count,
                'cpu_brand_count': cpu_brand_count, 'graphics_brand_count': graphics_brand_count,
                'graphics_company_count': graphics_company_count,
                'hdd_smodel_count': hdd_smodel_count, 'hdd_brand_count': hdd_brand_count, 'ssd_smodel_count':
                    ssd_smodel_count, 'ssd_brand_count': ssd_brand_count})
        else:
            return render(request, '403.html')


def data_sub_assets_reception(request):
    """主机配件数据"""

    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            AddConfigFlag = raw_get.get('AddConfigFlag', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            raw_data = ''

            # 添加sub_query
            sub_query = Q()

            if not AddConfigFlag:
                filter_company = raw_get.get('filter_company', '0')
                filter_CPU = raw_get.get('filter_CPU', '')
                filter_board = raw_get.get('filter_board', '')
                filter_ssd = raw_get.get('filter_ssd', '')
                filter_disk = raw_get.get('filter_disk', '')
                filter_mem = raw_get.get('filter_mem', '')
                filter_graphics = raw_get.get('filter_graphics', '')
                filter_number = raw_get.get('filter_number', '')
                filter_pos = raw_get.get('filter_pos', '')
                filter_status = raw_get.get('filter_status', '')
                filter_user = raw_get.get('filter_user', '')

                if filter_company != '0':
                    sub_query.add(Q(part_model__company=CompanyCode.objects.get(id=filter_company)), Q.AND)

                if filter_CPU != '全部':
                    sub_query.add(Q(part_model__ctype='CPU', part_model__smodel=filter_CPU), Q.AND)

                if filter_board != '全部':
                    sub_query.add(Q(part_model__ctype='主板', part_model__smodel=filter_board), Q.AND)

                if filter_ssd != '全部':
                    sub_query.add(Q(part_model__ctype='固态硬盘', part_model__smodel=filter_ssd), Q.AND)

                if filter_disk != '全部':
                    sub_query.add(Q(part_model__ctype='机械硬盘', part_model__smodel=filter_disk), Q.AND)

                if filter_mem != '全部':
                    sub_query.add(Q(part_model__ctype='内存', part_model__smodel=filter_mem), Q.AND)

                if filter_graphics != '全部':
                    sub_query.add(Q(part_model__ctype='显卡', part_model__smodel=filter_graphics), Q.AND)

                if filter_number:
                    sub_query.add(Q(number__icontains=filter_number), Q.AND)

                if int(filter_pos):
                    sub_query.add(Q(pos=Position.objects.get(id=filter_pos)), Q.AND)

                if int(filter_status) != 100:
                    sub_query.add(Q(status=filter_status), Q.AND)

                if filter_user != '全部':
                    sub_query.add(Q(user=filter_user), Q.AND)

            else:
                sub_query.add(Q(status=0), Q.AND)
                sub_query.add(Q(part_model__ctype__icontains=raw_get.get('ctype', '')), Q.AND)

            if search_value:

                STATUS_DIC = dict((v, k) for k, v in PartModelStatus.STATUS)
                status_list = [
                    v for k, v in STATUS_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                query = PartModelStatus.objects.select_related('pos').select_related('part_model'). \
                    select_related('part_model__supplier').filter((
                                                                          Q(part_model__ctype__icontains=search_value) |
                                                                          Q(
                                                                              part_model__smodel__icontains=search_value) |
                                                                          Q(status__in=status_list) |
                                                                          Q(number__icontains=search_value) |
                                                                          Q(pos__name__icontains=search_value) |
                                                                          Q(part_model__brand__icontains=search_value) |
                                                                          Q(
                                                                              user__icontains=search_value)) & sub_query).order_by(
                    'status')
            else:
                query = PartModelStatus.objects.select_related(
                    'pos').select_related('part_model').select_related(
                    'part_model__supplier').filter(sub_query).order_by('status')

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            # recordsFiltered = len(raw_data)
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def data_assets_reception(request):
    """资产领用数据"""

    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            raw_data = ''

            filter_ctype = raw_get.get('filter_ctype', '')
            filter_assets_type = raw_get.get('filter_assets_type', '')
            filter_company = raw_get.get('filter_company', '')
            filter_assets_number = raw_get.get('filter_assets_number', '')
            filter_name = raw_get.get('filter_name', '')
            filter_warehousing_region = request.POST.getlist('filter_warehousing_region[]', '全部')
            filter_merge_assets_number = raw_get.get('filter_merge_assets_number', '')
            filter_CPU = raw_get.get('filter_CPU', '')
            filter_board = raw_get.get('filter_board', '')
            filter_ssd = raw_get.get('filter_ssd', '')
            filter_disk = raw_get.get('filter_disk', '')
            filter_mem = raw_get.get('filter_mem', '')
            filter_graphics = raw_get.get('filter_graphics', '')
            filter_brand = raw_get.get('filter_brand', '')
            filter_specification = raw_get.get('filter_specification', '')
            filter_new_organization = raw_get.get('filter_new_organization', '')
            filter_user = raw_get.get('filter_user', '')
            filter_status = request.POST.getlist('filter_status[]', '全部')
            filter_pos = request.POST.getlist('filter_pos[]', '全部')
            filter_supplier = raw_get.get('filter_supplier', '')
            filter_remark = raw_get.get('filter_remark', '')
            exclude_unvailable_assets = raw_get.get('exclude_unvailable_assets', '')

            # 添加sub_query
            sub_query = Q()

            if int(filter_ctype) != 100:
                sub_query.add(Q(ctype=filter_ctype), Q.AND)

            if filter_assets_type == '固定资产':
                sub_query.add(Q(assets_number__contains='DZ'), Q.AND)
            elif filter_assets_type == '列管资产':
                sub_query.add(~Q(assets_number__contains='DZ'), Q.AND)

            if filter_assets_number:
                sub_query.add(Q(assets_number__icontains=filter_assets_number), Q.AND)

            if filter_merge_assets_number:
                sub_query.add(Q(assets__assets_number__icontains=filter_merge_assets_number), Q.AND)

            if filter_company != '0':
                sub_query.add(Q(company=CompanyCode.objects.get(id=filter_company)), Q.AND)

            if filter_name != '0':
                sub_query.add(Q(name__icontains=filter_name), Q.AND)

            if filter_CPU != '全部':
                sub_query.add(Q(mounting_part__ctype='CPU', mounting_part__smodel=filter_CPU), Q.AND)

            if filter_board != '全部':
                sub_query.add(Q(mounting_part__ctype='主板', mounting_part__smodel=filter_board), Q.AND)

            if filter_ssd != '全部':
                sub_query.add(Q(mounting_part__ctype='固态硬盘', mounting_part__smodel=filter_ssd), Q.AND)

            if filter_disk != '全部':
                sub_query.add(Q(mounting_part__ctype='机械硬盘', mounting_part__smodel=filter_disk), Q.AND)

            if filter_mem != '全部':
                sub_query.add(Q(mounting_part__ctype='内存', mounting_part__smodel=filter_mem), Q.AND)

            if filter_graphics != '全部':
                sub_query.add(Q(mounting_part__ctype='显卡', mounting_part__smodel=filter_graphics), Q.AND)

            if filter_brand != '全部':
                sub_query.add(Q(brand__icontains=filter_brand), Q.AND)

            if filter_specification:
                sub_query.add(Q(specification__icontains=filter_specification), Q.AND)

            if filter_status != '全部':
                sub_query.add(Q(status__in=filter_status), Q.AND)

            if filter_pos != '全部':
                # pos_obj = Position.objects.filter(id__in=filter_pos)
                sub_query.add(Q(pos_id__in=filter_pos), Q.AND)

            if int(filter_supplier) != 0:
                supplier = Supplier.objects.get(id=filter_supplier)
                sub_query.add(Q(supplier=supplier), Q.AND)

            if filter_new_organization != '全部':
                if filter_new_organization == '无':
                    sub_query.add(Q(belongs_to_new_organization=''), Q.AND)
                else:
                    sub_query.add(Q(belongs_to_new_organization__icontains=filter_new_organization), Q.AND)

            if filter_user != '全部':
                user = User.objects.get(username=filter_user)
                sub_query.add(Q(user=user), Q.AND)

            if filter_remark:
                sub_query.add(Q(remark__icontains=filter_remark), Q.AND)

            if int(exclude_unvailable_assets) == 1:
                sub_query.add(Q(status__in=[0, 1, 2, 3]), Q.AND)

            if str(filter_warehousing_region) != '全部':
                sub_query.add(Q(warehousing_region__id__in=filter_warehousing_region), Q.AND)

            if search_value:
                STATUS_DIC = dict((v, k) for k, v in Assets.STATUS)
                status_list = [
                    v for k, v in STATUS_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                TYPE_DIC = dict((v, k) for k, v in Assets.TYPE)
                type_list = [
                    v for k, v in TYPE_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                query = Assets.objects.select_related('supplier').prefetch_related('assets_set').filter((
                        Q(ctype__in=type_list) |
                        Q(assets_number__icontains=search_value) |
                        Q(name__icontains=search_value) |
                        Q(mounting_part__ctype__icontains=search_value) |
                        Q(mounting_part__smodel__icontains=search_value) |
                        Q(brand__icontains=search_value) |
                        Q(specification__icontains=search_value) |
                        Q(belongs_to_new_organization__icontains=search_value) |
                        Q(auth_user__username__icontains=search_value) |
                        Q(auth_user__first_name__icontains=search_value) |
                        Q(status__in=status_list) |
                        Q(assets__assets_number__icontains=search_value) |
                        Q(pos__name__icontains=search_value) |
                        Q(warehousing_region__name__icontains=search_value) |
                        Q(remark__icontains=search_value) & sub_query)
                ).order_by('-id').distinct()

            else:
                query = Assets.objects.select_related(
                    'supplier').prefetch_related('assets_set').filter(sub_query).order_by('-id')

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            # recordsFiltered = len(raw_data)
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def data_shell_assets_reception(request):
    """列管资产数据"""

    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            raw_data = ''

            filter_ctype = raw_get.get('filter_ctype', '')
            filter_company = raw_get.get('filter_company', '')
            filter_assets_number = raw_get.get('filter_assets_number', '')
            filter_name = raw_get.get('filter_name', '')
            filter_brand = raw_get.get('filter_brand', '')
            filter_specification = raw_get.get('filter_specification', '')
            filter_new_organization = raw_get.get('filter_new_organization', '')
            filter_user = raw_get.get('filter_user', '')
            filter_status = raw_get.get('filter_status', '')
            filter_pos = raw_get.get('filter_pos', '')
            filter_supplier = raw_get.get('filter_supplier', '')
            filter_remark = raw_get.get('filter_remark', '')

            # 添加sub_query
            sub_query = Q()

            if int(filter_ctype) != 100:
                sub_query.add(Q(ctype=filter_ctype), Q.AND)

            if filter_name != '全部':
                sub_query.add(Q(name__icontains=filter_name), Q.AND)

            if filter_assets_number:
                sub_query.add(Q(assets_number__icontains=filter_assets_number), Q.AND)

            if filter_company != '0':
                sub_query.add(Q(company=CompanyCode.objects.get(id=filter_company)), Q.AND)

            if filter_brand:
                sub_query.add(Q(brand__icontains=filter_brand), Q.AND)

            if filter_specification:
                sub_query.add(Q(specification__icontains=filter_specification), Q.AND)

            if filter_new_organization != '全部':
                sub_query.add(Q(belongs_to_new_organization__icontains=filter_new_organization), Q.AND)

            if filter_user != '全部':
                sub_query.add(Q(user__icontains=filter_user), Q.AND)

            if int(filter_status) != 100:
                sub_query.add(Q(status=filter_status), Q.AND)

            if int(filter_pos) != 0:
                pos_obj = Position.objects.get(id=filter_pos)
                sub_query.add(Q(pos=pos_obj), Q.AND)

            if int(filter_supplier) != 0:
                supplier = Supplier.objects.get(id=filter_supplier)
                sub_query.add(Q(supplier=supplier), Q.AND)

            if filter_remark:
                sub_query.add(Q(remark__icontains=filter_remark), Q.AND)

            if search_value:
                STATUS_DIC = dict((v, k) for k, v in Assets.STATUS)
                status_list = [
                    v for k, v in STATUS_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                TYPE_DIC = dict((v, k) for k, v in Assets.TYPE)
                type_list = [
                    v for k, v in TYPE_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                query = Assets.objects.select_related('supplier').filter(
                    Q(ctype__in=type_list) |
                    Q(assets_number__icontains=search_value) |
                    Q(name__icontains=search_value) |
                    Q(brand__icontains=search_value) |
                    Q(specification__icontains=search_value) |
                    Q(belongs_to_new_organization__icontains=search_value) |
                    Q(user__icontains=search_value) |
                    Q(status__in=status_list) |
                    Q(pos__name__icontains=search_value) |
                    Q(remark__icontains=search_value) & sub_query
                ).exclude(assets_number__icontains='DZ').order_by('status').distinct()
            else:
                query = Assets.objects.select_related('supplier').filter(sub_query).exclude(
                    assets_number__icontains='DZ').order_by('status')

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            # recordsFiltered = len(raw_data)
            data = {"data": [i.show_shell() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def assets_trace(request):
    """资产变更的追踪"""
    if request.method == "GET":
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            head = {'value': '资产追踪'}
            all_cpu = list(set([x.smodel for x in PartModel.objects.filter(ctype='CPU')]))
            all_board = list(set([x.smodel for x in PartModel.objects.filter(ctype='主板')]))
            all_ssd = list(set([x.smodel for x in PartModel.objects.filter(ctype='固态硬盘')]))
            all_disk = list(set([x.smodel for x in PartModel.objects.filter(ctype='机械硬盘')]))
            all_mem = list(set([x.smodel for x in PartModel.objects.filter(ctype='内存')]))
            all_graphics = list(set([x.smodel for x in PartModel.objects.filter(ctype='显卡')]))
            all_users = User.objects.all()
            all_events = list(LogAssets.EVENT)
            return render(request, 'assets_trace.html', {
                'head': head, 'all_cpu': all_cpu, 'all_board': all_board, 'all_ssd': all_ssd,
                'all_disk': all_disk, 'all_mem': all_mem, 'all_graphics': all_graphics, 'all_users': all_users,
                'all_events': all_events})
        else:
            return render(request, '403.html')


def data_assets_trace(request):
    """资产变更追踪数据"""
    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            raw_data = ''

            filter_event = raw_get.get('filter_event', '')
            filter_assets_number = raw_get.get('filter_assets_number', '')
            filter_name = raw_get.get('filter_name', '')
            filter_CPU = raw_get.get('filter_CPU', '')
            filter_board = raw_get.get('filter_board', '')
            filter_ssd = raw_get.get('filter_ssd', '')
            filter_disk = raw_get.get('filter_disk', '')
            filter_mem = raw_get.get('filter_mem', '')
            filter_graphics = raw_get.get('filter_graphics', '')
            filter_number = raw_get.get('filter_number', '')
            filter_etime = raw_get.get('filter_etime', '')
            filter_log_user = raw_get.get('filter_log_user', '')
            filter_pos = raw_get.get('filter_pos', '')
            filter_user = raw_get.get('filter_user', '')
            filter_purchase = raw_get.get('filter_purchase', '')
            filter_price = raw_get.get('filter_price', '')

            # 添加sub_query
            sub_query = Q()

            if int(filter_event) != 100:
                sub_query.add(Q(event=filter_event), Q.AND)

            if filter_assets_number:
                sub_query.add(Q(assets__assets_number__icontains=filter_assets_number), Q.AND)

            if filter_name:
                sub_query.add((Q(assets__name=filter_name) | Q(part_model__ctype=filter_name)), Q.AND)

            if filter_CPU != '全部':
                sub_query.add(Q(part_model__ctype='CPU', part_model__smodel=filter_CPU), Q.AND)

            if filter_board != '全部':
                sub_query.add(Q(part_model__ctype='主板', part_model__smodel=filter_board), Q.AND)

            if filter_ssd != '全部':
                sub_query.add(Q(part_model__ctype='固态硬盘', part_model__smodel=filter_ssd), Q.AND)

            if filter_disk != '全部':
                sub_query.add(Q(part_model__ctype='机械硬盘', part_model__smodel=filter_disk), Q.AND)

            if filter_mem != '全部':
                sub_query.add(Q(part_model__ctype='内存', part_model__smodel=filter_mem), Q.AND)

            if filter_graphics != '全部':
                sub_query.add(Q(part_model__ctype='显卡', part_model__smodel=filter_graphics), Q.AND)

            if filter_number:
                sub_query.add(Q(number__icontains=filter_number), Q.AND)

            if filter_etime:
                sub_query.add(Q(etime__contains=filter_etime), Q.AND)

            if filter_log_user != '全部':
                sub_query.add(Q(log_user__icontains=filter_log_user), Q.AND)

            if int(filter_pos) != 0:
                pos_obj = Position.objects.get(id=filter_pos)
                sub_query.add(Q(pos=pos_obj), Q.AND)

            if filter_user != '全部':
                sub_query.add(Q(user__icontains=filter_user), Q.AND)

            if int(filter_purchase) != 100:
                sub_query.add(Q(purchase=filter_purchase), Q.AND)

            if filter_price:
                sub_query.add(Q(price__icontains=filter_price), Q.AND)

            if search_value:

                EVENT_DIC = dict((v, k) for k, v in LogAssets.EVENT)
                event_list = [
                    v for k, v in EVENT_DIC.items() if (k.startswith(search_value) or k.endswith(search_value))
                ]

                query = LogAssets.objects.select_related('assets').select_related('pos').filter(
                    Q(event__in=event_list) |
                    Q(assets__assets_number__icontains=search_value) |
                    Q(part_model__ctype__contains=search_value) |
                    Q(part_model__smodel__icontains=search_value) |
                    Q(etime__contains=search_value) |
                    Q(log_user__icontains=search_value) |
                    Q(pos__name__icontains=search_value) |
                    Q(user__icontains=search_value) |
                    Q(number__icontains=search_value) | Q(price__icontains=search_value) & sub_query
                ).order_by('-etime')

            else:
                query = LogAssets.objects.select_related('assets').select_related('pos').filter(sub_query).order_by(
                    '-etime')

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            # recordsFiltered = len(raw_data)
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def download(request):
    """导出excel"""
    if request.method == "POST":
        raw_get = json.loads(request.body.decode('utf-8'))
        file_suffix = int(time.time())
        file_name = 'zichan_' + str(file_suffix) + '.xls'
        download_path = os.path.join(os.path.dirname(__file__), 'downloads', file_name)

        def gen_excel(download_path, **raw_get):

            wb = xlwt.Workbook()
            sheet_name = wb.add_sheet("assets")

            # 第一行记录字段
            row1 = sheet_name.row(0)

            col_fields = [
                '类别', '资产编号', '资产名称', '仓库区域', 'CPU', '主板', '固态硬盘',
                '机械硬盘', '内存', '显卡', '其他', '品牌', '规格',
                '使用部门', '使用人', '财产状态', '备注', '位置', '公司', '备注'
            ]

            # 自定义过滤标签
            filter_ctype = raw_get.get('filter_ctype', '')
            filter_assets_type = raw_get.get('filter_assets_type', '')
            filter_company = raw_get.get('filter_company', '')
            filter_assets_number = raw_get.get('filter_assets_number', '')
            filter_name = raw_get.get('filter_name', '')
            filter_warehousing_region = raw_get.get('filter_warehousing_region', '全部')
            if filter_warehousing_region is None:
                filter_warehousing_region = '全部'
            filter_merge_assets_number = raw_get.get('filter_merge_assets_number', '')
            filter_CPU = raw_get.get('filter_CPU', '')
            filter_board = raw_get.get('filter_board', '')
            filter_ssd = raw_get.get('filter_ssd', '')
            filter_disk = raw_get.get('filter_disk', '')
            filter_mem = raw_get.get('filter_mem', '')
            filter_graphics = raw_get.get('filter_graphics', '')
            filter_brand = raw_get.get('filter_brand', '')
            filter_specification = raw_get.get('filter_specification', '')
            filter_new_organization = raw_get.get('filter_new_organization', '')
            filter_user = raw_get.get('filter_user', '')
            filter_status = raw_get.get('filter_status', '全部')
            if filter_status is None:
                filter_status = '全部'
            filter_pos = raw_get.get('filter_pos', '全部')
            if filter_pos is None:
                filter_pos = '全部'
            filter_supplier = raw_get.get('filter_supplier', '')
            filter_remark = raw_get.get('filter_remark', '')

            # 添加sub_query
            sub_query = Q()

            if int(filter_ctype) != 100:
                sub_query.add(Q(ctype=filter_ctype), Q.AND)

            if filter_assets_type == '固定资产':
                sub_query.add(Q(assets_number__contains='DZ'), Q.AND)
            elif filter_assets_type == '列管资产':
                sub_query.add(~Q(assets_number__contains='DZ'), Q.AND)

            if filter_assets_number:
                sub_query.add(Q(assets_number__icontains=filter_assets_number), Q.AND)

            if filter_merge_assets_number:
                sub_query.add(Q(assets__assets_number__icontains=filter_merge_assets_number), Q.AND)

            if filter_company != '0':
                sub_query.add(Q(company=CompanyCode.objects.get(id=filter_company)), Q.AND)

            if filter_name != '0':
                sub_query.add(Q(name__icontains=filter_name), Q.AND)

            if filter_CPU != '全部':
                sub_query.add(Q(mounting_part__ctype='CPU', mounting_part__smodel=filter_CPU), Q.AND)

            if filter_board != '全部':
                sub_query.add(Q(mounting_part__ctype='主板', mounting_part__smodel=filter_board), Q.AND)

            if filter_ssd != '全部':
                sub_query.add(Q(mounting_part__ctype='固态硬盘', mounting_part__smodel=filter_ssd), Q.AND)

            if filter_disk != '全部':
                sub_query.add(Q(mounting_part__ctype='机械硬盘', mounting_part__smodel=filter_disk), Q.AND)

            if filter_mem != '全部':
                sub_query.add(Q(mounting_part__ctype='内存', mounting_part__smodel=filter_mem), Q.AND)

            if filter_graphics != '全部':
                sub_query.add(Q(mounting_part__ctype='显卡', mounting_part__smodel=filter_graphics), Q.AND)

            if filter_brand != '全部':
                sub_query.add(Q(brand__icontains=filter_brand), Q.AND)

            if filter_specification:
                sub_query.add(Q(specification__icontains=filter_specification), Q.AND)

            if filter_new_organization != '全部':
                sub_query.add(Q(belongs_to_new_organization__icontains=filter_new_organization), Q.AND)

            if filter_user != '全部':
                sub_query.add(Q(user__icontains=filter_user), Q.AND)

            if filter_status != '全部':
                sub_query.add(Q(status__in=filter_status), Q.AND)

            if filter_pos != '全部':
                sub_query.add(Q(pos__id__in=filter_pos), Q.AND)

            if int(filter_supplier) != 0:
                supplier = Supplier.objects.get(id=filter_supplier)
                sub_query.add(Q(supplier=supplier), Q.AND)

            if filter_remark:
                sub_query.add(Q(remark__icontains=filter_remark), Q.AND)

            if filter_warehousing_region != '全部':
                sub_query.add(Q(warehousing_region__id__in=filter_warehousing_region), Q.AND)

            try:
                for index, field in enumerate(col_fields):
                    row1.write(index, field)

                # all_assets = Assets.objects.filter(assets_number__contains='DZ')
                all_assets = Assets.objects.select_related(
                    'supplier').prefetch_related('assets_set').filter((sub_query)).order_by('assets_number')

                nrow = 1

                for assets in all_assets:
                    row = sheet_name.row(nrow)
                    for index, field in enumerate(col_fields):
                        if index == 0:
                            value = assets.get_ctype_display()
                        elif index == 1:
                            value = assets.assets_number
                        elif index == 2:
                            value = assets.name
                        elif index == 3:
                            value = assets.warehousing_region.name if assets.warehousing_region else ''
                        elif index == 4:
                            value = ','.join([x.smodel for x in assets.mounting_part.filter(ctype='CPU')])
                        elif index == 5:
                            value = ','.join([x.smodel for x in assets.mounting_part.filter(ctype='主板')])
                        elif index == 6:
                            value = ','.join([x.smodel for x in assets.mounting_part.filter(ctype='固态硬盘')])
                        elif index == 7:
                            value = ','.join([x.smodel for x in assets.mounting_part.filter(ctype='机械硬盘')])
                        elif index == 8:
                            value = ','.join([x.smodel for x in assets.mounting_part.filter(ctype='内存')])
                        elif index == 9:
                            value = ','.join([x.smodel for x in assets.mounting_part.filter(ctype='显卡')])
                        elif index == 10:
                            value = ''
                        elif index == 11:
                            value = assets.brand
                        elif index == 12:
                            value = assets.specification
                        elif index == 13:
                            value = assets.belongs_to_new_organization
                        elif index == 14:
                            value = assets.user
                        elif index == 15:
                            value = assets.get_status_display()
                        elif index == 16:
                            value = ''
                        elif index == 17:
                            value = assets.pos.name
                        elif index == 18:
                            value = assets.company.name
                        elif index == 19:
                            value = assets.remark
                        row.write(index, value)
                    nrow += 1

                wb.save(download_path)
                data = file_name
                success = True

            except Exception as e:
                data = str(e)
                success = False

            return {'data': data, 'success': success}

        def file_iterator(file_path, chunk_size=512):
            gen_excel(file_path.encode('utf-8'))
            with open(file_path.encode('utf-8'), 'rb+') as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        # file_name = '固定资产台账.xls'
        # response = StreamingHttpResponse(file_iterator(file_path))
        # response['Content-Type'] = 'application/octet-stream'
        # response['Content-Disposition'] = 'attachment;filename={0}'.format(urlquote(file_name))
        # return response

        return JsonResponse(gen_excel(download_path, **raw_get))


def assets_template(request):
    """资产模板页面"""

    if request.method == 'GET':
        if User.objects.get(id=request.user.id).has_perm('users.edit_it_assets'):
            head = {'value': '资产模板', 'username': request.user.username}
            all_new_organization = [x.get_ancestors_name() for x in OrganizationMptt.objects.filter(type=1)]
            return render(request, 'assets_template.html',
                          {'head': head, 'all_new_organization': all_new_organization})
        else:
            return render(request, '403.html')


def data_assets_template(request):
    """资产变更追踪数据"""
    if request.method == "GET":
        if User.objects.get(id=request.user.id).has_perm('users.edit_it_assets'):
            raw_get = request.GET.dict()
            draw = raw_get.get('draw', 0)
            raw_data = AssetsTemplates.objects.all()
            recordsTotal = len(raw_data)

            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def add_or_edit_assets_template(request):
    """增加或者修改资产模板"""
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')

        try:
            if editFlag:
                if User.objects.get(id=request.user.id).has_perm('users.edit_it_assets'):
                    s = AssetsTemplates.objects.filter(id=id)
                    s.update(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
            else:
                if User.objects.get(id=request.user.id).has_perm('users.add_it_assets'):
                    AssetsTemplates.objects.create(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
        except PermissionDenied:
            msg = '权限拒绝'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def get_assets_template(request):
    """获取资产模板"""
    if request.method == 'POST':
        if User.objects.get(id=request.user.id).has_perm('users.edit_it_assets'):
            id = json.loads(request.body.decode('utf-8')).get('id')
            obj = AssetsTemplates.objects.get(id=id)
            edit_data = obj.edit_data()
            return JsonResponse(edit_data)
        else:
            raise PermissionDenied


def del_data_assets_template(request):
    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.del_it_assets'):
            del_data = json.loads(request.body.decode('utf-8'))
            objs = AssetsTemplates.objects.filter(id__in=del_data)
            msg = ''

            try:
                with transaction.atomic():
                    objs.delete()
                success = True
            except Exception as e:
                msg = str(e)
                success = False

            return JsonResponse({'data': success, 'msg': msg})
        else:
            raise PermissionDenied


def company_code(request):
    "公司代号页面"

    if request.method == 'GET':
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            head = {'value': '公司代号', 'username': request.user.username}
            return render(request, 'company_code.html', {'head': head})
        else:
            return render(request, '403.html')


def data_company_code(request):
    '公司代号页面数据'
    if request.method == "GET":
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            raw_get = request.GET.dict()
            draw = raw_get.get('draw', 0)
            raw_data = CompanyCode.objects.all()
            recordsTotal = len(raw_data)

            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def add_or_edit_company_code(request):
    '增加或者修改资产模板'
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')
        leader = raw_data.pop('leader')

        try:
            leader = User.objects.get(id=leader)
            raw_data['leader'] = leader
            if editFlag:
                if User.objects.get(id=request.user.id).has_perm('users.edit_it_assets'):
                    s = CompanyCode.objects.filter(id=id)
                    s.update(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
            else:
                if User.objects.get(id=request.user.id).has_perm('users.add_it_assets'):
                    CompanyCode.objects.create(**raw_data)
                    success = True
                else:
                    raise PermissionDenied
        except PermissionDenied:
            msg = '权限拒绝'
            success = False
        except Exception as e:
            msg = str(e)
            success = False

        return JsonResponse({'data': success, 'msg': msg})


def get_company_code(request):
    '获取公司代号'
    if request.method == 'POST':
        if User.objects.get(id=request.user.id).has_perm('users.edit_it_assets'):
            id = json.loads(request.body.decode('utf-8')).get('id')
            obj = CompanyCode.objects.get(id=id)
            edit_data = obj.edit_data()
            return JsonResponse(edit_data)
        else:
            raise PermissionDenied


def del_data_company_code(request):
    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.del_it_assets'):
            del_data = json.loads(request.body.decode('utf-8'))
            objs = CompanyCode.objects.filter(id__in=del_data)
            msg = ''

            try:
                with transaction.atomic():
                    objs.delete()
                success = True
            except ProtectedError:
                msg = '存在资产使用该公司，不能删除'
                success = False
            except Exception as e:
                msg = str(e)
                success = False

            return JsonResponse({'data': success, 'msg': msg})
        else:
            raise PermissionDenied


def assets_collect(request):
    """资产图表汇总
    需要把所有公司的全部资产展示
    """
    if request.method == "GET":
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            head = {'value': '资产图表汇总', 'username': request.user.username}
            all_assets = get_all_assets()
            data = {'all_assets': all_assets}
            return render(request, 'assets_collect.html', {'head': head, 'data': data})
        else:
            return render(request, '403.html')


def detail(request, company):
    """某个公司的某种状态下的资产的详细数据
    """

    if request.method == "GET":
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            head = {'value': company}
            company_id = CompanyCode.objects.get(name=company).id
            all_data_structure = get_assets_detail()
            return render(request, 'assets_detail.html', {
                'head': head, 'all_data_structure': all_data_structure, 'company_id': company_id})
        else:
            return render(request, '403.html')


def assets_data_detail(request):
    """某个公司下某个状态的所有资产统计
    """
    if request.method == "POST":
        if User.objects.get(id=request.user.id).has_perm('users.view_it_assets'):
            pdata = json.loads(request.body.decode('utf-8'))
            status_code = pdata.get('status_code')
            company_name = pdata.get('company_name')
            data = get_assets_detail_data(status_code, company_name)
            return JsonResponse(data, safe=False)


def assets_application_form(request):
    if request.method == 'POST':
        assets_id_list = json.loads(request.body.decode('utf-8'))
        assets_obj_list = [Assets.objects.get(pk=x) for x in assets_id_list]
        max_id = PrintNumberRecord.objects.all().order_by('-serial_id').first()
        print_id = str(max_id.serial_id + 1)
        print_num = "YL-YW-" + print_id.zfill(4)[-4:]
        PrintNumberRecord.objects.create(serial_id=max_id.serial_id + 1, number=print_num)
        return render(request, 'it_assets_application_form.html', {'assets_obj_list': assets_obj_list,
                                                                   'print_num': print_num})
    if request.method == 'GET':
        assets_obj_list = [Assets.objects.first()]
        return render(request, 'it_assets_application_form.html', {'assets_obj_list': assets_obj_list})


def assets_add_config(request):
    """固定资产领用主机配件，升级配置"""
    if request.method == 'POST':
        if request.user.is_superuser:
            pdata = json.loads(request.body.decode('utf-8'))
            assetsId = pdata.get('assetsId')
            dataId = pdata.get('dataId')
            part_model_status_obj = PartModelStatus.objects.get(pk=dataId)
            assets = Assets.objects.get(pk=assetsId)
            part_model = part_model_status_obj.part_model
            if part_model_status_obj.status == 0 and part_model_status_obj.number > 0:
                """减少库存数量"""
                part_model_status_obj.number = part_model_status_obj.number - 1
                part_model_status_obj.save()
                if part_model_status_obj.number == 0:
                    part_model_status_obj.delete()
                """创建固定资产与主机配件关系"""
                create_or_update_assets_with_part_model(part_model, assets, 1)
                """记录日志"""
                part_model_brand = part_model_status_obj.part_model.brand
                if not part_model_brand:
                    part_model_brand = ''
                LogAssets.objects.create(
                    event=10, part_model=part_model_status_obj.part_model, etime=datetime.now(), assets=assets,
                    number=1, log_user=request.user.username, pos=assets.pos, user=assets.auth_user.username,
                    ctype=part_model_status_obj.part_model.ctype,
                    current_configuration=str(part_model_brand) + str(part_model_status_obj.part_model.smodel))
                success = True
                return JsonResponse({'data': success})
            else:
                raise PartModelStatusNotEnouth
        else:
            raise PermissionDenied


def it_assets_amount_statistics(request):
    """IT资产数量统计"""
    if request.method == 'POST':
        success = True
        msg = 'ok'
        try:
            all_assets = Assets.objects.select_related('company').filter(status__in=(0,))
            """主机按公司按规格统计数量"""
            computer_company = tuple(all_assets.filter(name__icontains='主机').values('company').distinct())
            computer = dict()
            for c in computer_company:
                company = CompanyCode.objects.get(pk=c['company'])
                computer_statistics = tuple(
                    all_assets.filter(name__icontains='主机', company_id=c['company']).values('specification').annotate(
                        total=Count('assets_number')))
                computer[company.name] = computer_statistics
            """显示器按公司按品牌统计数量"""
            display_company = tuple(all_assets.filter(name__icontains='显示器').values('company').distinct())
            display = dict()
            for c in display_company:
                company = CompanyCode.objects.get(pk=c['company'])
                display_statistics = tuple(
                    all_assets.filter(name__icontains='显示器', company_id=c['company']).values('brand').annotate(
                        total=Count('assets_number')))
                display[company.name] = display_statistics
            """绘画板按公司统计数量"""
            draw = tuple(
                all_assets.filter(name__icontains='绘画板').values('company').annotate(total=Count('assets_number')))
            draw = [{'company': CompanyCode.objects.get(pk=x['company']).name, 'total': x['total']} for x in draw]

            return JsonResponse({'success': success, 'computer': computer, 'display': display, 'draw': draw})
        except Exception as e:
            success = False
            msg = str(e)
            return JsonResponse({'msg': msg, 'success': success})


class AssetsBatchAlterView(generic.View):
    """资产信息批量修改"""

    def get(self, request):
        if request.user.is_superuser:
            form = UploadFileForm()
            alter_type = AssetsBatchAlterRecord.TYPE
            return render(request, 'assets_batch_alter.html', {'form': form, 'alter_type': alter_type})
        else:
            return render(request, '403.html')

    def post(self, request):
        success = True
        msg = 'ok'
        try:
            if not request.user.is_superuser:
                raise Exception('权限受限')
            pdata = json.loads(request.body.decode('utf-8'))
            table_data = pdata.get('table_data')
            """验证excel数据"""
            if len(table_data) == 1:
                raise Exception('excel中没有需要修改的资产数据!')
            """去除数据前后空格并字符串化"""
            table_data = [list(map(lambda x: str(x).strip(), d)) for d in table_data]
            """判断修改类型"""
            table_head = table_data[0]
            if '修改前公司主体' in table_head and '修改后公司主体' in table_head:
                alter_type = 1
                old_index = table_head.index('修改前公司主体')
                new_index = table_head.index('修改后公司主体')
            elif '修改前资产状态' in table_head and '修改后资产状态' in table_head:
                alter_type = 2
                old_index = table_head.index('修改前资产状态')
                new_index = table_head.index('修改后资产状态')
            elif '修改前仓库区域' in table_head and '修改后仓库区域' in table_head:
                alter_type = 3
                old_index = table_head.index('修改前仓库区域')
                new_index = table_head.index('修改后仓库区域')
            else:
                raise Exception('未能识别修改字段信息，请核实表头是否正确！')
            """创建修改记录"""
            record_obj = AssetsBatchAlterRecord.objects.create(alter_user=request.user, alter_type=alter_type)
            """修改对应资产字段"""
            batch_alter_assets_info(table_data, alter_type, old_index, new_index, record_obj, request.user)

        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return JsonResponse({'success': success, 'msg': msg})


def assets_templates_download(request, filename):
    """资产excel模板下载"""
    file = open('/data/www/cmdb/it_assets/excel_templates/' + filename + '.xlsx', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="' + filename + '.xlsx"'
    return response


def assets_batch_alter_excel_import(request):
    """批量修改资产信息excel导入"""
    if request.method == "GET":
        if request.user.is_superuser:
            return HttpResponseRedirect('/it_assets/assets_batch_alter/')
        else:
            return render(request, '403.html')

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fname = request.FILES['file'].name
            save_uploaded_file(request.FILES['file'], 'it_assets/upload/', fname)
            table = read_excel_table_data('it_assets/upload/' + fname)

        return render(request, 'assets_batch_alter.html', {'form': form, 'table': table})


def assets_batch_alter_record(request):
    """批量修改资产历史记录"""
    if request.method == 'GET':
        if request.user.is_superuser:
            all_user = User.objects.filter(is_active=1)
            all_alter_type = AssetsBatchAlterRecord.TYPE
            return render(request, 'assets_batch_alter_record.html',
                          {'all_user': all_user, 'all_alter_type': all_alter_type})
        else:
            return render(request, '403.html')


def data_assets_batch_alter_record(request):
    """批量修改资产历史记录数据"""

    if request.method == "POST":
        if request.user.is_superuser:
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            filter_alter_user = raw_get.get('filter_alter_user', '全部')
            filter_alter_type = raw_get.get('filter_alter_type', '0')

            # 添加sub_query
            sub_query = Q()

            if filter_alter_user != '全部':
                user = User.objects.get(username=filter_alter_user)
                sub_query.add(Q(alter_user=user), Q.AND)

            if str(filter_alter_type) != '0':
                sub_query.add(Q(alter_type=filter_alter_type), Q.AND)

            if search_value:
                alter_type_list = [x[0] for x in AssetsBatchAlterRecord.TYPE if search_value in x[1]]
                query = AssetsBatchAlterRecord.objects.filter((
                        Q(alter_user__username__icontains=search_value) |
                        Q(alter_user__first_name__icontains=search_value) |
                        Q(alter_type__in=alter_type_list) & sub_query)
                ).order_by('-alter_time').distinct()

            else:
                query = AssetsBatchAlterRecord.objects.filter(sub_query).order_by('-alter_time')

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def data_assets_batch_alter_record_detail(request):
    """批量修改资产历史记录详情数据"""

    if request.method == "POST":
        if request.user.is_superuser:
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))
            record_id = raw_get.get('record_id', 0)

            if search_value:
                result_list = [x[0] for x in AssetsBatchAlterRecordDetail.RESULT if search_value in x[1]]
                query = AssetsBatchAlterRecordDetail.objects.filter(record_id=record_id).filter((
                        Q(assets_number__icontains=search_value) |
                        Q(result__in=result_list))
                ).order_by('-result').distinct()
            else:
                query = AssetsBatchAlterRecordDetail.objects.filter(record_id=record_id).order_by('-result')

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def create_bthalt_assets_excel_data(request):
    """生成批量修改资产结果下载数据"""
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        id = raw_data.get('id', 0)
        file_suffix = int(time.time())
        file_name = 'bth_alter_result' + str(file_suffix) + '.xls'
        download_path = os.path.join(os.path.dirname(__file__), 'bth_alt_rsl_download', file_name)

        def gen_excel(download_path):
            if request.user.is_superuser:
                wb = xlwt.Workbook()
                sheet_name = wb.add_sheet("detail")

                # 第一行记录字段
                row1 = sheet_name.row(0)

                col_fields = (
                    '修改时间', '修改人', '修改类型', '资产编号', '修改前', '修改后', '修改结果', '备注'
                )

                try:
                    for index, field in enumerate(col_fields):
                        row1.write(index, field)

                    obj = AssetsBatchAlterRecord.objects.prefetch_related('assetsbatchalterrecorddetail_set').get(pk=id)

                    nrow = 1

                    for d in obj.assetsbatchalterrecorddetail_set.all():
                        row = sheet_name.row(nrow)
                        for index, field in enumerate(col_fields):
                            if index == 0:
                                value = str(d.record.alter_time)[:19]
                            elif index == 1:
                                value = d.record.alter_user.username
                            elif index == 2:
                                value = d.record.get_alter_type_display()
                            elif index == 3:
                                value = d.assets_number
                            elif index == 4:
                                value = d.old_value
                            elif index == 5:
                                value = d.new_value
                            elif index == 6:
                                value = d.get_result_display()
                            elif index == 7:
                                value = d.remark
                            row.write(index, value)
                        nrow += 1

                    wb.save(download_path)
                    data = file_name
                    success = True

                except Exception as e:
                    data = str(e)
                    success = False

                return {'data': data, 'success': success}
            else:
                success = False
                return {'msg': '没有权限', 'success': success}

        return JsonResponse(gen_excel(download_path))


def bthalt_assets_result_downloads(request, filename):
    """批量修改资产结果下载"""
    file = open('/data/www/cmdb/it_assets/bth_alt_rsl_download/' + filename + '.xls', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="' + filename + '.xls"'
    return response


def assets_warehousing_region(request):
    """资产仓库区"""
    if request.method == "GET":
        if request.user.is_superuser:

            return render(request, 'assets_warehousing_region.html')
        else:
            return render(request, '403.html')


def data_assets_warehousing_region(request):
    """资产仓库区域数据"""
    if request.method == "POST":
        if request.user.is_superuser:
            raw_get = request.POST.dict()

            search_value = raw_get.get('search[value]', '')
            start = int(raw_get.get('start', 0))
            draw = raw_get.get('draw', 0)
            length = int(raw_get.get('length', 10))

            if search_value:
                query = AssetsWarehousingRegion.objects.filter(
                    Q(name__icontains=search_value)
                ).order_by('name')

            else:
                query = AssetsWarehousingRegion.objects.order_by(
                    'name')

            raw_data = query[start: start + length]
            recordsTotal = query.count()
            data = {"data": [i.show_all() for i in raw_data], 'draw': draw, 'recordsTotal': recordsTotal,
                    'recordsFiltered': recordsTotal}
            return JsonResponse(data)


def add_or_edit_warehousing_region(request):
    """增加或者修改仓库区域"""
    if request.method == 'POST':
        success = True
        raw_data = json.loads(request.body.decode('utf-8'))
        msg = 'ok'
        editFlag = raw_data.pop('editFlag')
        id = raw_data.pop('id')

        try:
            if not request.user.is_superuser:
                raise PermissionDenied
            if editFlag:
                wr = AssetsWarehousingRegion.objects.filter(id=id)
                wr.update(**raw_data)
            else:
                AssetsWarehousingRegion.objects.create(**raw_data)
        except IntegrityError:
            msg = '区域已存在'
            success = False
        except PermissionDenied:
            msg = '权限拒绝'
            success = False
        except Exception as e:
            msg = str(e)
            success = False
        finally:
            return JsonResponse({'data': success, 'msg': msg})


def get_assets_warehousing_region(request):
    """获取资产仓库区域"""
    if request.method == 'POST':
        if User.objects.get(id=request.user.id).has_perm('users.edit_it_assets'):
            id = json.loads(request.body.decode('utf-8')).get('id')
            obj = AssetsWarehousingRegion.objects.get(id=id)
            edit_data = obj.edit_data()
            return JsonResponse(edit_data)
        else:
            raise PermissionDenied


def del_data_warehousing_region(request):
    """删除仓库区域"""
    if request.method == "POST":
        if request.user.is_superuser:
            del_data = json.loads(request.body.decode('utf-8'))
            objs = AssetsWarehousingRegion.objects.filter(id__in=del_data)
            msg = ''

            try:
                with transaction.atomic():
                    objs.delete()
                success = True
            except IntegrityError:
                success = False
                msg = '存在关联资产，请先修改相关资产的仓库区域！'
            except Exception as e:
                msg = str(e)
                success = False

            return JsonResponse({'data': success, 'msg': msg})
        else:
            raise PermissionDenied


def list_warehousing_region(request):
    """列出仓库区域"""
    if request.method == "POST":
        data = []

        q = request.POST.get('q', None)

        if q:
            all_warehousing_region = AssetsWarehousingRegion.objects.filter(name__icontains=q)
        else:
            all_warehousing_region = AssetsWarehousingRegion.objects.all()

        for x in all_warehousing_region:
            data.append({'id': x.id, 'text': x.name})

        return JsonResponse(data, safe=False)
