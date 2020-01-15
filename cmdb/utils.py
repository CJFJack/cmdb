# -*- encoding: utf-8 -*-

from assets.models import *

from django.db import IntegrityError, transaction

from decimal import Decimal
from datetime import datetime
from datetime import timedelta

import xlrd
import os

import sys
import requests

#from imp import reload

#reload(sys)
#sys.setdefaultencoding('utf8')


def check_before_delete(objs):
    '''
    Check before delete objs
    '''
    if objs[0].__class__.__name__ == "Room":
        return _check_room_before_delete(objs)

    if objs[0].__class__.__name__ == "Cabinet":
        return _check_cabinet_before_delete(objs)

    if objs[0].__class__.__name__ == "Device":
        return _check_device_before_delete(objs)

    if objs[0].__class__.__name__ == "Host":
        return _check_host_before_delete(objs)

    if objs[0].__class__.__name__ == "NetworkDevice":
        return ('true', '')

    if objs[0].__class__.__name__ == "IpPool":
        return (True, 'ok')

    if objs[0].__class__.__name__ == "Vip":
        return _check_vip_before_delete(objs)

    if objs[0].__class__.__name__ == "AppType":
        return _check_apptype_before_delete(objs)

    if objs[0].__class__.__name__ == "Application":
        return _check_application_before_delete(objs)

    if objs[0].__class__.__name__ == "PlatForm":
        return _check_platform_before_delete(objs)

    if objs[0].__class__.__name__ == "ChiefPlatForm":
        return _check_chief_platform_before_delete(objs)

    if objs[0].__class__.__name__ == "OsType":
        return _check_ostype_before_delete(objs)

    if objs[0].__class__.__name__ == "IpType":
        return _check_iptype_before_delete(objs)

    if objs[0].__class__.__name__ == "DeviceBrand":
        return _check_brand_before_delete(objs)

    if objs[0].__class__.__name__ == "DeviceModel":
        return _check_model_before_delete(objs)

    if objs[0].__class__.__name__ == "SDNS":
        return _check_sdns_before_delete(objs)

    if objs[0].__class__.__name__ == "Certificate":
        return _check_certificate_before_delete(objs)

    if objs[0].__class__.__name__ == "NetworkPolicy":
        return ('true', '')


def handle_uploaded_file(f):
    '''
    Handle file upload
    '''
    fpath = os.path.join(os.getcwd(), 'assets/upload/', f.name)
    with open(fpath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


class ImportExcel(object):
    '''
    Import data from excel,with specified table name
    '''

    def __init__(self, fpath, action, ts):

        self.fpath = fpath
        self.action = action
        self.tpath = os.path.join('/tmp', str(ts))

        # tables must be imported in order!
        self._import_order = {
            '更新值班': 1,
            '少年英雄': 2,
            '剑雨江湖': 3,
        }

        def _get_records_total():
            '''
            获取全部的表的总行数
            '''
            records_total = 0
            workbook = xlrd.open_workbook(fpath)

            tnames = workbook.sheet_names()

            for table in tnames:
                records_total += workbook.sheet_by_name(table).nrows - 1

            return records_total

        self._records_total = _get_records_total()

        # 初始化的时候写入初始的记录
        '''
        with open(self.tpath, 'wb') as f:
            f.write('0\n'.encode('utf-8'))
            f.write(str(self._records_total).encode('utf-8'))
        '''

    def _update_tpath(self):
        '''
        每次循环完一次以后，更新tpath里面的值
        '''

        with open(self.tpath, 'r') as f:
            info = f.readlines()

        finished = str(int(info[0].split('\n')[0]) + 1) + '\n'    # 自增1

        with open(self.tpath, 'wb') as f:
            f.write(finished)
            f.write(str(self._records_total))

    def _xldate_to_datetime(self, xldate):
        """
            将excel的xldate格式转化为python的
            datetime 格式，并且格式化输出
        """

        raw_date = datetime(1900, 1, 1)
        delta = timedelta(days=xldate)
        return (raw_date + delta).strftime('%Y-%m-%d')

    def doImport(self):
        if self.action == "add":
            return self._addImport(self.fpath, False)
        if self.action == "update":
            return self._addImport(self.fpath, True)

    def _addImport(self, fpath, update):

        # msg = ''

        workbook = xlrd.open_workbook(fpath)
        # tnames = workbook.sheet_names()
        sheet_name = workbook.sheet_by_name("值班安排表")

        # Let's order the tnames by import order
        # tnames = sorted(
        #     tnames, key=lambda table: self._import_order.get(table))

        return self._addDutyScheduleObj(workbook, sheet_name, update)

    def _addDutyScheduleObj(self, workbook, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'start_date',
            1: 'end_date',
            2: 'weekdays_person',
            3: 'weekend_person',
            4: 'belongs_to_game_project',
        }

        error = ''
        table = '值班安排表'
        try:
            with transaction.atomic():
                for row_index in range(1, sheet_name.nrows):
                    edata = {}
                    # edata['belongs_to_game_project'] = belongs_to_game_project
                    for col_index in range(0, len(_col_defines)):
                        cell_obj = sheet_name.cell(row_index, col_index)
                        if col_index in [0, 1]:
                            if cell_obj.ctype == 3:
                                edata[_col_defines.get(col_index)] = datetime(*xlrd.xldate_as_tuple(
                                    cell_obj.value, workbook.datemode)).strftime("%Y-%m-%d")
                            else:
                                error = '表 {table} 第{row_index}行,第{col_index}列 日期格式不对\n'.format(
                                        table=table, row_index=row_index + 1, col_index=col_index)
                                raise NameError
                        elif col_index in [2]:
                            weekdays_person = cell_obj.value.split(',')
                            weekdays_person = User.objects.filter(username__in=weekdays_person)
                        elif col_index in [3]:
                            weekend_person = cell_obj.value.split(',')
                            weekend_person = User.objects.filter(username__in=weekend_person)
                        elif col_index in [4]:
                            project_name = cell_obj.value.split(',')
                            list_project = GameProject.objects.filter(project_name__in=project_name)
                    else:
                        for project in list_project:
                            edata['belongs_to_game_project'] = project
                            obj = DutySchedule.objects.create(**edata)
                            obj.weekdays_person.add(*weekdays_person)
                            obj.weekend_person.add(*weekend_person)

        except GameProject.DoesNotExist:
            error = '%s项目不存在' % (table)
            return error
        except NameError:
            return error
        except User.DoesNotExist:
            error = '表 {table} 第{row_index}行,第{col_index}列 用户{username}不存在\n'.format(
                    table=table, row_index=row_index + 1, col_index=col_index, username=username)
            return error
        except Exception as e:
            info = {
                'table': table,
                'row_index': row_index + 1,
                'col_index': col_index,
                'e': str(e)
            }
            error = '表 {table} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(**info)
            return error

        return error

    def _addDeviceBrandObj(self, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'brandname',
        }

        error = ''
        tname = 'brandname'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                for col_index in range(0, len(_col_defines)):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    edata[_col_defines.get(col_index)] = str(
                        cell_obj.value.encode('utf-8')).strip()
                d_b = DeviceBrand(**edata)
                d_b.save()
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                self._update_tpath()
        return error

    def _addDeviceModelObj(self, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'belongs_to_brand',
            1: 'modelname',
            2: 'u_bit',
        }

        error = ''
        tname = 'brand_model'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                for col_index in range(0, len(_col_defines)):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [0]:
                        brandname = str(cell_obj.value.encode('utf-8')).strip()
                        belongs_to_brand = DeviceBrand.objects.get(
                            brandname=brandname)
                        edata[_col_defines.get(
                            col_index)] = belongs_to_brand
                    elif col_index in [2]:
                        edata[_col_defines.get(col_index)] = int(
                            cell_obj.value)
                    else:
                        edata[_col_defines.get(col_index)] = str(
                            cell_obj.value.encode('utf-8')).strip()
                d_m = DeviceModel(**edata)
                d_m.save()
            except Device.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index} 品牌名称不存在\n'.format(tname=tname,
                                                                                 row_index=row_index,
                                                                                 col_index=col_index)
                raise NameError
            except NameError:
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                self._update_tpath()

        return error

    def _addPlatFormObj(self, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'platform_name',
            1: 'manager',
            2: 'manager_tel',
            3: 'developer',
            4: 'developer_tel',
            5: 'status',
            6: 'id',
        }

        error = ''
        tname = 'platform'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                if update:
                    col_index = len(_col_defines)
                    cell_obj = sheet_name.cell(row_index, col_index - 1)
                    if cell_obj.ctype == 0:
                        id_is_none = True
                    else:
                        id_is_none = False
                        instance = PlatForm.objects.filter(id=int(cell_obj.value))
                        if len(instance) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,平台id不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index)
                            raise NameError
                for col_index in range(0, len(_col_defines) - 1):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [2, 4]:  # ctype  2  float
                        if cell_obj.ctype == 0:
                            pass
                        else:
                            edata[_col_defines.get(col_index)] = int(cell_obj.value)
                    elif col_index in [5]:
                        char_order = str(cell_obj.value.encode('utf-8'))
                        if char_order == '生产':
                            edata[_col_defines.get(col_index)] = 0
                        elif char_order == '下线':
                            edata[_col_defines.get(col_index)] = 1
                        elif char_order == '未上线':
                            edata[_col_defines.get(col_index)] = 2
                        elif char_order == '内部平台使用':
                            edata[_col_defines.get(col_index)] = 3

                        else:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,请输入生产、下线、未上线、内部平台使用\n'.format(tname=tname,
                                                                                                          row_index=row_index,
                                                                                                          col_index=col_index)
                            raise NameError
                    else:
                        if cell_obj.ctype == 0:
                            pass
                        else:
                            edata[_col_defines.get(col_index)] = cell_obj.value.encode('utf-8')
                if update and not id_is_none:
                    instance.update(**edata)
                else:
                    p = PlatForm(**edata)
                    p.save()
            except NameError:
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'platform: %s' % (row_index)
                self._update_tpath()

        return error

    def _addOsTypeObj(self, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'templatename',
            1: 'ostype',
            2: 'os_detail_name',
            3: 'template_cpu',
            4: 'template_mem',
            5: 'template_disk',
        }

        error = ''
        tname = 'os_type'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                for col_index in range(0, len(_col_defines)):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    edata[_col_defines.get(col_index)
                          ] = cell_obj.value.encode('utf-8')
                ot = OsType(**edata)
                ot.save()
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                self._update_tpath()

        return error

    def _addIpTypeObj(self, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'ip_belongs_to_room',
            1: 'typename',
            2: 'network_area',
            3: 'start',
            4: 'end',
            5: 'order',
            6: 'ip_type',
            7: 'in_pairs',
        }

        error = ''
        tname = 'iptype'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                for col_index in range(0, len(_col_defines)):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [0]:
                        roomname = str(cell_obj.value.encode('utf-8'))
                        ip_belongs_to_room = Room.objects.filter(
                            roomname=roomname)[0]
                        edata[_col_defines.get(
                            col_index)] = ip_belongs_to_room
                    elif col_index in [3, 4]:
                        edata[_col_defines.get(col_index)] = int(
                            cell_obj.value)
                    elif col_index in [5]:
                        char_order = str(cell_obj.value.encode('utf-8')).strip()
                        if char_order == '降序':
                            edata[_col_defines.get(col_index)] = 1
                        elif char_order == '升序':
                            edata[_col_defines.get(col_index)] = 0
                        else:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,请输入升序或者降序\n'.format(tname=tname,
                                                                                                row_index=row_index,
                                                                                                col_index=col_index)
                            raise NameError
                    elif col_index in [7]:
                        char_in_pairs = str(cell_obj.value.encode('utf-8'))
                        if char_in_pairs == '否':
                            edata[_col_defines.get(col_index)] = 0
                        elif char_in_pairs == '是':
                            edata[_col_defines.get(col_index)] = 1
                        else:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,请输入是或者否\n'.format(tname=tname,
                                                                                              row_index=row_index,
                                                                                              col_index=col_index)
                            raise NameError
                    else:
                        edata[_col_defines.get(col_index)] = str(
                            cell_obj.value.encode('utf-8')).strip()
                it = IpType(**edata)
                it.save()
            except NameError:
                continue
            except Room.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,机房名称{roomname}不存在\n'.format(tname=tname,
                                                                                            row_index=row_index,
                                                                                            col_index=col_index,
                                                                                            roomname=roomname)
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                self._update_tpath()

        return error

    def _addIpPoolObj(self, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'ip_pool_belongs_to_platform',
            1: 'start_ip',
            2: 'en_ip',
            3: 'gateway',
            4: 'netmask',
            5: 'vlan',
            6: 'pool_status',
            7: 'pool_type',
            8: 'belongs_to_iptype',
            9: 'belongs_to_iptype2',
            10: 'in_pair_with',
            11: 'ip_segment'
        }

        error = ''
        tname = 'ip_pool'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                if update:
                    col_index = len(_col_defines)
                    cell_obj = sheet_name.cell(row_index, col_index - 1)
                    if cell_obj.ctype == 0:
                        id_is_none = True
                    else:
                        id_is_none = False
                        instance = IpPool.objects.filter(ip_segment=int(cell_obj.value))
                        if len(instance) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,资源池ip_segment不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index)
                            raise NameError
                for col_index in range(0, len(_col_defines) - 1):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [0]:    # 所属平台
                        if cell_obj.ctype == 0:
                            edata[_col_defines.get(col_index)] = None
                        else:
                            platform_name = str(cell_obj.value.encode('utf-8')).strip()
                            ip_pool_belongs_to_platform = PlatForm.objects.get(
                                platform_name=platform_name)
                            edata[_col_defines.get(
                                col_index)] = ip_pool_belongs_to_platform
                    elif col_index in [6]:    # 平台状态
                        char_status = str(cell_obj.value.encode('utf-8')).strip()
                        if char_status == "可用":
                            edata[_col_defines.get(col_index)] = 1
                        elif char_status == "停用":
                            edata[_col_defines.get(col_index)] = 0
                        else:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,请输入可用或者停用\n'.format(tname=tname,
                                                                                                row_index=row_index,
                                                                                                col_index=col_index)
                            raise NameError
                    elif col_index in [7]:    # 平台属性
                        char_type = str(cell_obj.value.encode('utf-8')).strip()
                        if char_type == '私有':
                            edata[_col_defines.get(col_index)] = 0
                        elif char_type == '公有':
                            edata[_col_defines.get(col_index)] = 1
                        else:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,请输入私有或者公有\n'.format(tname=tname,
                                                                                                row_index=row_index,
                                                                                                col_index=col_index)
                            raise NameError
                    elif col_index in [8]:    # 所属第一个ip类型
                        typename = cell_obj.value.rsplit('-', 1)[0]
                        network_area = cell_obj.value.rsplit('-', 1)[1]
                        iptype = IpType.objects.get(typename=typename, network_area=network_area)
                        edata[_col_defines.get(col_index)] = iptype
                    elif col_index in [9]:    # 所属第二个ip类型,如果有的话
                        if cell_obj.value:
                            typename = cell_obj.value.rsplit('-', 1)[0]
                            network_area = cell_obj.value.rsplit('-', 1)[1]
                            iptype2 = IpType.objects.get(typename=typename, network_area=network_area)
                            edata[_col_defines.get(col_index)] = iptype2
                    elif col_index in [10]:
                        # Since we don't add pairs now, will be in next step
                        pass
                    else:
                        if cell_obj.ctype == 2:  # float type
                            edata[_col_defines.get(col_index)] = int(cell_obj.value)
                        else:
                            edata[_col_defines.get(col_index)] = str(
                                cell_obj.value.encode('utf-8')).strip()
                if update and not id_is_none:
                    instance.update(**edata)
                else:
                    ippool = IpPool(**edata)
                    ippool.save()
            except NameError:
                continue
            except IpType.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,ip类型不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index)
                continue
            except PlatForm.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,平台名称{platform_name}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index, platform_name=platform_name)
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'ippool: %s' % (row_index)
                self._update_tpath()

        # Add in pairs
        for row_index in range(1, sheet_name.nrows):
            try:
                self_start_ip = str(sheet_name.cell(row_index, 1).value).strip()
                start_ip = str(sheet_name.cell(row_index, 10).value).strip()
                # if start_ip is true
                if start_ip:
                    self_obj = IpPool.objects.get(start_ip=self_start_ip)
                    ippool_obj = IpPool.objects.get(start_ip=start_ip)
                    self_obj.in_pair_with = ippool_obj
                    self_obj.save()
            except IpPool.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,起始ip{start_ip}不存在\n'.format(tname=tname,
                                                                                            row_index=row_index,
                                                                                            col_index=col_index,
                                                                                            start_ip=start_ip)
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue

        return error

    def _addAppType(self, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'app_type',
            1: 'app_detail_type',
        }

        error = ''
        tname = 'app_type'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                for col_index in range(0, len(_col_defines)):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    edata[_col_defines.get(col_index)] = str(
                        cell_obj.value.encode('utf-8')).strip()
                at = AppType(**edata)
                at.save()
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                self._update_tpath()

        return error

    def _addDeviceObj(self, sheet_name, update):

        # remember postion
        _belongs_to_room = None
        _col = None
        _row = None
        _belongs_to_model = None

        # column and field relationship
        _col_defines = {
            0: 'belongs_to_room',
            1: 'maintenance_code',
            2: 'belongs_to_model',
            3: 'room_col',
            4: 'col_index',
            5: 'start_u_bit',
            6: 'device_cpu',
            7: 'device_mem',
            8: 'device_disk',
            9: 'purchase_date',
            10: 'warranty_date',
            11: 'device_status',
            12: 'device_remarks',
            13: 'id',
        }

        error = ''
        tname = 'device'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                if update:
                    col_index = len(_col_defines)
                    cell_obj = sheet_name.cell(row_index, col_index - 1)
                    # 如果id不存在，则新增一个
                    if cell_obj.ctype == 0:
                        id_is_none = True
                    else:
                        id_is_none = False
                        instance = Device.objects.filter(id=int(cell_obj.value))
                        if len(instance) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,物理设备id不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index)
                            raise NameError

                for col_index in range(0, len(_col_defines) - 1):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [0]:
                        roomname = str(cell_obj.value.encode('utf-8'))
                        belongs_to_room = Room.objects.filter(roomname=roomname)[0]
                        # remember room
                        edata[_col_defines.get(col_index)] = belongs_to_room
                        _belongs_to_room = belongs_to_room
                    elif col_index in [1]:
                        if cell_obj.ctype == 1:
                            edata[_col_defines.get(col_index)] = str(cell_obj.value).strip()
                        if cell_obj.ctype == 2:
                            edata[_col_defines.get(col_index)] = str(int(cell_obj.value)).strip()
                    elif col_index in [2]:
                        brand_model = str(cell_obj.value.encode('utf-8'))
                        device_brand_name = brand_model.split('@')[0]
                        device_model_name = brand_model.split('@')[1]
                        device_brand = DeviceBrand.objects.get(brandname=device_brand_name)
                        device_model = device_brand.devicemodel_set.get(
                            modelname=device_model_name)

                        _belongs_to_model = device_model
                        edata[_col_defines.get(col_index)] = _belongs_to_model
                    elif col_index in [3]:
                        if cell_obj.ctype == 0:
                            # 如果是空的
                            edata[_col_defines.get(col_index)] = None
                        else:
                            # in try ... except block, int and char type
                            if cell_obj.ctype == 2:
                                col = int(cell_obj.value)
                            else:
                                col = str(cell_obj.value).strip()
                            _col = col
                            # check col is full
                            if _belongs_to_room.col_is_full(col):
                                error += '表 {tname} 第{row_index}行,第{col_index}列,物理设备列{col}已经放满\n'.format(
                                    tname=tname,
                                    row_index=row_index,
                                    col_index=col_index,
                                    col=col)
                                raise NameError
                            else:
                                edata[_col_defines.get(col_index)] = col
                    elif col_index in [4]:
                        if cell_obj.ctype == 0:
                            # 如果是空的
                            edata[_col_defines.get(col_index)] = None
                        else:
                            if cell_obj.ctype == 2:
                                row = int(cell_obj.value)
                            else:
                                row = str(cell_obj.value).strip()
                            _row = row
                            if _belongs_to_room.col_index_is_full(_col, row):
                                error += '表 {tname} 第{row_index}行,第{col_index}列,物理设备列{row}已经放满\n'.format(
                                    tname=tname,
                                    row_index=row_index,
                                    col_index=col_index,
                                    row=row)
                                raise NameError
                            else:
                                edata[_col_defines.get(col_index)] = row
                    elif col_index in [5]:
                        if cell_obj.ctype == 0:
                            # 如果是空的
                            edata[_col_defines.get(col_index)] = None
                        else:
                            if update:
                                listSelfUsed = instance[0].u2list()
                            else:
                                listSelfUsed = None
                            start_u = int(cell_obj.value)
                            check_u_result = check_u(_belongs_to_room, _belongs_to_model, _col, _row, start_u, listSelfUsed=listSelfUsed)
                            if check_u_result:
                                error += '表 {tname} 第{row_index}行,第{col_index}列{check_u_result}\n'.format(
                                    tname=tname,
                                    row_index=row_index,
                                    col_index=col_index,
                                    check_u_result=check_u_result)
                                raise NameError
                            else:
                                edata[_col_defines.get(col_index)] = start_u
                    elif col_index in [9, 10]:
                        date_time_set = datetime(
                            *xlrd.xldate_as_tuple(cell_obj.value, 0)).strftime("%Y-%m-%d")
                        edata[_col_defines.get(col_index)] = date_time_set
                    elif col_index in [11]:
                        char_status = str(cell_obj.value.encode('utf-8')).strip()
                        if char_status == '上架':
                            edata[_col_defines.get(col_index)] = 0
                        elif char_status == '生产':
                            edata[_col_defines.get(col_index)] = 1
                        elif char_status == '维修':
                            edata[_col_defines.get(col_index)] = 2
                        elif char_status == '下线':
                            edata[_col_defines.get(col_index)] = 3
                        else:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,请输入可用上架,生产,维修,下线\n'.format(
                                tname=tname,
                                row_index=row_index,
                                col_index=col_index)
                            raise NameError
                    elif col_index in [12]:
                        if cell_obj.ctype == 0:
                            pass
                        else:
                            edata[_col_defines.get(col_index)] = str(
                                cell_obj.value.encode('utf-8'))
                    else:
                        edata[_col_defines.get(col_index)] = str(
                            cell_obj.value.encode('utf-8')).strip()
                if update and not id_is_none:
                    instance.update(**edata)
                else:
                    d = Device(**edata)
                    d.save()

            except Room.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,机房名{roomname}不存在\n'.format(
                    tname=tname,
                    row_index=row_index,
                    col_index=col_index,
                    roomname=roomname)
                continue
            except DeviceBrand.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,品牌{device_brand_name}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    device_brand_name=device_brand_name)
                continue
            except DeviceModel.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,品牌{device_model_name}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    device_model_name=device_model_name)
                continue
            except NameError:
                continue
            except IntegrityError:
                error += '表 {tname} 第{row_index}行,第{col_index}列,序列号重复\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index)
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'device: %s' % (row_index)
                self._update_tpath()

        return error

    def _addHostObj(self, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'belongs_to_PlatForm',
            1: 'hostname',
            2: 'host_network_area',
            3: 'belongs_to_device',
            4: 'host_cpu',
            5: 'host_mem',
            6: 'host_disk',
            7: 'belongs_to_ostype',
            8: 'vcenter',
            9: 'host_status',
            10: 'host_remarks',
            11: 'id',
        }

        error = ''
        tname = 'host'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                if update:
                    col_index = len(_col_defines)
                    cell_obj = sheet_name.cell(row_index, col_index - 1)
                    if cell_obj.ctype == 0:
                        id_is_none = True
                    else:
                        id_is_none = False
                        instance = Host.objects.filter(id=int(cell_obj.value))
                        if len(instance) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,主机id不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index)
                            raise NameError
                for col_index in range(0, len(_col_defines) - 1):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [0]:
                        platform_name = str(
                            cell_obj.value.encode('utf-8')).strip()
                        belongs_to_PlatForm = PlatForm.objects.get(
                            platform_name=platform_name)
                        edata[_col_defines.get(col_index)] = belongs_to_PlatForm
                    elif col_index in [2]:
                        typename_network_area = str(
                            cell_obj.value.encode('utf-8')).strip()  # SIT-WEB-WEB
                        typename = typename_network_area.rsplit('-', 1)[0]  # SIT-WEB
                        network_area = typename_network_area.rsplit('-', 1)[1]
                        IpType.objects.get(typename=typename, network_area=network_area)
                        edata[_col_defines.get(col_index)] = typename_network_area
                    elif col_index in [3]:
                        if cell_obj.ctype == 0:
                            pass
                        else:
                            if cell_obj.ctype == 1:
                                maintenance_code = str(cell_obj.value.encode('utf-8')).strip()
                            else:
                                maintenance_code = str(int(cell_obj.value)).encode('utf-8').strip()
                            d = Device.objects.get(maintenance_code=maintenance_code)
                            edata[_col_defines.get(col_index)] = d
                    elif col_index in [7]:
                        templatename = str(
                            cell_obj.value.encode('utf-8')).strip()
                        belongs_to_ostype = OsType.objects.get(templatename=templatename)
                        edata[_col_defines.get(col_index)] = belongs_to_ostype
                    elif col_index in [9]:
                        char_status = str(
                            cell_obj.value.encode('utf-8')).strip()
                        if char_status == '生产':
                            edata[_col_defines.get(col_index)] = 0
                        elif char_status == '下线':
                            edata[_col_defines.get(col_index)] = 1
                        elif char_status == '维修':
                            edata[_col_defines.get(col_index)] = 2
                        else:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,请输入可用生产,维修,下线\n'.format(tname=tname,
                                                                                                    row_index=row_index,
                                                                                                    col_index=col_index)
                            raise NameError
                    else:
                        if cell_obj.ctype == 0:
                            pass
                        elif cell_obj.ctype == 2:
                            edata[_col_defines.get(col_index)] = str(
                                int(cell_obj.value)).encode('utf-8').strip()
                        else:
                            edata[_col_defines.get(col_index)] = str(
                                cell_obj.value.encode('utf-8')).strip()
                if update and not id_is_none:
                    instance.update(**edata)
                else:
                    h = Host(**edata)
                    h.save()
            except NameError:
                continue
            except PlatForm.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,平台名称{platform_name}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index, platform_name=platform_name)
                continue
            except IpType.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,网络区域{typename_network_area}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    typename_network_area=typename_network_area)
                continue
            except Device.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,物理设备服务编号{maintenance_code}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    maintenance_code=maintenance_code)
                continue
            except OsType.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,操作系统模板{templatename}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index, templatename=templatename)
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'host: %s' % (row_index)
                self._update_tpath()

        return error

    def _addApplicationObj(self, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'hostname',
            1: 'application_name',
            2: 'belongs_to_apptype',
            3: 'sdns',
            4: 'certificate',
            5: 'id',
        }

        error = ''
        tname = 'application'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                if update:
                    col_index = len(_col_defines)
                    cell_obj = sheet_name.cell(row_index, col_index - 1)
                    if cell_obj.ctype == 0:
                        id_is_none = True
                    else:
                        id_is_none = False
                        instance = Application.objects.filter(id=int(cell_obj.value))
                        if len(instance) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,平台id不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index)
                            raise NameError
                for col_index in range(0, len(_col_defines) - 1):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [2]:
                        typename = str(
                            cell_obj.value.encode('utf-8')).strip()  # db-mysql
                        app_type = typename.split('-')[0]
                        app_detail_type = typename.split('-')[1]
                        belongs_to_apptype = AppType.objects.get(
                            app_type=app_type, app_detail_type=app_detail_type)
                        edata[_col_defines.get(col_index)] = belongs_to_apptype
                    elif col_index in [3, 4]:
                        # 这里暂时把智能DNS和证书字段都设置为None
                        edata[_col_defines.get(col_index)] = None
                    else:
                        if cell_obj.ctype == 0:
                            edata[_col_defines.get(col_index)] = None
                        else:
                            edata[_col_defines.get(col_index)] = str(
                                cell_obj.value.encode('utf-8')).strip()
                if update and not id_is_none:
                    instance.update(**edata)
                else:
                    a = Application(**edata)
                    a.save()
            except AppType.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,所属类型{typename}不存在\n'.format(
                    tname=tname,
                    row_index=row_index,
                    col_index=col_index,
                    typename=typename)
                continue
            except NameError:
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'application: %s' % (row_index)
                self._update_tpath()

        return error

    def _addAssignedIpObj(self, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'ip',
            1: 'vlan',
            2: 'belongs_to_device',
            3: 'belongs_to_host',
            4: 'belongs_to_iptype',
            5: 'id',
        }

        error = ''
        tname = 'assigned_ip'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                if update:
                    col_index = len(_col_defines)
                    cell_obj = sheet_name.cell(row_index, col_index - 1)
                    if cell_obj.ctype == 0:
                        id_is_none = True
                    else:
                        id_is_none = False
                        instance = AssignedIp.objects.filter(id=int(cell_obj.value))
                        if len(instance) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,物理ip的id不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index)
                            raise NameError
                for col_index in range(0, len(_col_defines) - 1):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [0]:
                        edata[_col_defines.get(col_index)] = str(cell_obj.value.encode('utf-8')).strip()
                    elif col_index in [1]:
                        if cell_obj.ctype == 2:
                            edata[_col_defines.get(col_index)] = str(int(cell_obj.value)).strip()
                        else:
                            edata[_col_defines.get(col_index)] = str(cell_obj.value.encode('utf-8')).strip()
                    elif col_index in [2]:
                        if not cell_obj.value:
                            pass
                        else:
                            maintenance_code = str(
                                cell_obj.value.encode('utf-8')).strip()
                            d = Device.objects.get(maintenance_code=maintenance_code)
                            edata[_col_defines.get(col_index)] = d
                    elif col_index in [3]:
                        if not cell_obj.value:
                            pass
                        else:
                            hostname = str(cell_obj.value.encode('utf-8')).strip()
                            h = Host.objects.get(hostname=hostname)
                            edata[_col_defines.get(col_index)] = h
                    elif col_index in [4]:
                        typename_network_area = str(cell_obj.value.encode('utf-8')).strip()  # SIT-WEB-WEB
                        typename = typename_network_area.rsplit('-', 1)[0]  # SIT-WEB
                        network_area = typename_network_area.rsplit('-', 1)[1]
                        iptype = IpType.objects.get(typename=typename, network_area=network_area)
                        edata[_col_defines.get(col_index)] = iptype
                if update and not id_is_none:
                    instance.update(**edata)
                else:
                    asi = AssignedIp(**edata)
                    asi.save()
            except Device.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,物理设备服务编号{maintenance_code}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    maintenance_code=maintenance_code)
                continue
            except Host.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,主机名{hostname}不存在\n'.format(tname=tname,
                                                                                           row_index=row_index,
                                                                                           col_index=col_index,
                                                                                           hostname=hostname)
                continue
            except IpType.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,网络区域{typename_network_area}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    typename_network_area=typename_network_area)
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'assgined_ip: %s' % (row_index)
                self._update_tpath()

        return error

    def _addApplicationHost(self, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'hostname',
            1: 'application_name',
        }

        error = ''
        tname = 'host_applications'

        # 记住主机名
        _hostname = ''

        for row_index in range(1, sheet_name.nrows):
            try:
                for col_index in range(0, len(_col_defines)):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [0]:
                        hostname = str(cell_obj.value.encode('utf-8')).strip()
                        h = Host.objects.get(hostname=hostname)
                        _hostname = hostname
                    elif col_index in [1]:
                        """
                        Excel表里面的记录有一种如下的情况:
                        在application表里面，有三条这样的记录:
                             mysql
                        A    mysql
                        B    mysql

                        在host_applications里面有一条这样的记录:
                        C    mysql

                        读取application记录的方法是：
                        1 在host_applications表里面找到 mysql这个application_name
                        去到application表里面，根据mysql这个字段去查找
                        2 会发现有三条记录，这样，又会通过host_applications里面的'C'这个hostname
                        来做一个联合的查询，也就是在application中找到application_name为mysql,
                        hostname为c的来查询
                        3 但是此时是找不到这条记录的，这样，就会取application表中application_name mysql
                        同时hostname为空的记录，也就是第一条记录
                        """
                        application_name = str(
                            cell_obj.value.encode('utf-8')).strip()
                        # app = Application.objects.get(
                        #    application_name=application_name, hostname=_hostname)
                        app = Application.objects.filter(application_name=application_name)
                        # 如果没有，则说明没有这个application_name的服务
                        if len(app) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,获取服务名{application_name}不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index,
                                application_name=application_name)
                            raise NameError
                        # 如果获取到多个app，则需要通过hostname在一次进行过滤,如果找不到，按照3
                        elif len(app) > 1:
                            app = Application.objects.filter(
                                application_name=application_name, hostname=_hostname)
                            if len(app) == 0:
                                app = Application.objects.get(application_name=application_name, hostname=None)
                            else:
                                app = app[0]
                        # 如果长度为1，说明可以通过这个application_name来获取唯一的服务
                        elif len(app) == 1:
                            app = app[0]
                        h.applications.add(app)
                        h.save()
            except Host.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,主机名{hostname}不存在\n'.format(tname=tname,
                                                                                           row_index=row_index,
                                                                                           col_index=col_index,
                                                                                           hostname=hostname)
                continue
            except Application.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,服务名{application_name}主机名{hostname}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    application_name=application_name, hostname=_hostname)
                continue
            except Application.MultipleObjectsReturned:
                error += '表 {tname} 第{row_index}行,第{col_index}列,获取服务名{application_name}有重复\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    application_name=application_name)
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
            finally:
                # print 'application_host: %s' % (row_index)
                self._update_tpath()

        return error

    def _addVipObj(self, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'ip',
            1: 'vlan',
            2: 'vip_belongs_to_iptype',
            3: 'id'
        }

        error = ''
        tname = 'vip'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                if update:
                    col_index = len(_col_defines)
                    cell_obj = sheet_name.cell(row_index, col_index - 1)
                    if cell_obj.ctype == 0:
                        id_is_none = True
                    else:
                        id_is_none = False
                        instance = Vip.objects.filter(id=int(cell_obj.value))
                        if len(instance) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,vip的id不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index)
                            raise NameError
                for col_index in range(0, len(_col_defines) - 1):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [2]:
                        typename_network_area = str(
                            cell_obj.value.encode('utf-8')).strip()  # SIT-WEB-WEB
                        typename = typename_network_area.rsplit('-', 1)[0]  # SIT-WEB
                        network_area = typename_network_area.rsplit('-', 1)[1]
                        it = IpType.objects.get(
                            typename=typename, network_area=network_area
                        )
                        edata[_col_defines.get(col_index)] = it
                    else:
                        edata[_col_defines.get(col_index)] = str(
                            cell_obj.value).strip()
                if update and not id_is_none:
                    instance.update(**edata)
                else:
                    v = Vip(**edata)
                    v.save()

            except IpType.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,网络区域{typename_network_area}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    typename_network_area=typename_network_area)
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'vip: %s' % (row_index)
                self._update_tpath()

        return error

    def _addApplicationVip(self, sheet_name, update):

        # column and field relationship
        _col_defines = {
            0: 'hostname',
            1: 'application_name',
            2: 'ip',
        }

        error = ''
        tname = 'application_with_vip'

        # 记住主机名
        _hostname = ''

        for row_index in range(1, sheet_name.nrows):
            try:
                for col_index in range(0, len(_col_defines)):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [0]:
                        if cell_obj.ctype == 0:
                            _hostname = None
                        else:
                            _hostname = str(
                                cell_obj.value.encode('utf-8')).strip()
                    elif col_index in [1]:
                        application_name = str(
                            cell_obj.value.encode('utf-8')).strip()
                        app = Application.objects.get(
                            application_name=application_name, hostname=_hostname)
                    elif col_index in [2]:
                        vip = str(cell_obj.value).strip()
                        vip_obj = Vip.objects.get(ip=vip)
                        app.with_vip.add(vip_obj)
            except Application.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,服务名{application_name}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    application_name=application_name)
                continue
            except Application.MultipleObjectsReturned:
                error += '表 {tname} 第{row_index}行,第{col_index}列,获取服务名{application_name}有重复\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    application_name=application_name)
                continue
            except Vip.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,vip{vip}不存在\n'.format(tname=tname,
                                                                                      row_index=row_index,
                                                                                      col_index=col_index,
                                                                                      vip=vip)
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'application_vip: %s' % (row_index)
                self._update_tpath()

        return error

    def _addPublicAndLoadIp(self, sheet_name, update):
        # column and field relationship
        _col_defines = {
            0: 'ip',
            1: 'belongs_to_platform',
            2: 'remarks',
            3: 'id',
        }

        error = ''
        tname = 'public_load_ip'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                if update:
                    col_index = len(_col_defines)
                    cell_obj = sheet_name.cell(row_index, col_index - 1)
                    if cell_obj.ctype == 0:
                        id_is_none = True
                    else:
                        id_is_none = False
                        instance = PublicAndLoadIp.objects.filter(id=int(cell_obj.value))
                        if len(instance) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,id不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index)
                            raise NameError
                for col_index in range(0, len(_col_defines) - 1):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [0]:
                        ip = str(cell_obj.value.encode('utf-8')).strip()
                        edata[_col_defines.get(col_index)] = ip
                    elif col_index in [1]:
                        platform_name = str(cell_obj.value.encode('utf-8')).strip()
                        belongs_to_platform = PlatForm.objects.get(platform_name=platform_name)
                        edata[_col_defines.get(col_index)] = belongs_to_platform
                    else:
                        if cell_obj.ctype == 0:
                            edata[_col_defines.get(col_index)] = None
                        else:
                            edata[_col_defines.get(col_index)] = str(cell_obj.value.encode('utf-8')).strip()

                if update and not id_is_none:
                    instance.update(**edata)
                else:
                    p = PublicAndLoadIp(**edata)
                    p.save()
            except PlatForm.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,平台名称{platform_name}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    platform_name=platform_name)
                continue
            except NameError:
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'vip: %s' % (row_index)
                self._update_tpath()

        return error

    def _addPublicRelation(self, sheet_name, update):
        # column and field relationship
        '''
        _col_defines = {
            0: 'publicAndloadip',
            1: 'relation',
            2: 'publicAndloadip2',
            3: 'assignedip',
            4: 'vip',
            5: 'port',
            6: 'id',
        }
        '''

        error = ''
        tname = 'public_relation_ip'

        for row_index in range(1, sheet_name.nrows):
            try:
                # 首先获取出公网或负载IP
                cell_obj = sheet_name.cell(row_index, 0)
                ip = str(cell_obj.value.encode('utf-8')).strip()
                publicAndloadip = PublicAndLoadIp.objects.get(ip=ip)

                # 获取relation
                cell_obj = sheet_name.cell(row_index, 1)
                relation = str(cell_obj.value.encode('utf-8')).strip()

                # 获取port
                cell_obj = sheet_name.cell(row_index, 5)
                if cell_obj.ctype == 2:
                    port = str(int(cell_obj.value)).encode('utf-8').strip()
                else:
                    port = str(cell_obj.value.encode('utf-8')).strip()

                # 取三个中间表中的一个
                for col_index in [2, 3, 4]:
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if cell_obj.value:
                        if col_index == 2:
                            ip2 = str(cell_obj.value.encode('utf-8')).strip()
                            publicAndloadip2 = PublicAndLoadIp.objects.filter(ip=ip2)
                            if len(publicAndloadip2) == 0:
                                error += '表 {tname} 第{row_index}行,第{col_index}列,公网负载IP{ip2}不存在\n'.format(
                                    tname=tname, row_index=row_index, col_index=col_index, ip2=ip2)
                                raise NameError
                            else:
                                PublicAndLoadIpMappingSelf.objects.create(
                                    publicAndloadip=publicAndloadip,
                                    publicAndloadip2=publicAndloadip2[0],
                                    relation=relation,
                                    port=port
                                )
                                break
                        elif col_index == 3:
                            ip2 = str(cell_obj.value.encode('utf-8')).strip()
                            assignedip = AssignedIp.objects.filter(ip=ip2)
                            if len(assignedip) == 0:
                                error += '表 {tname} 第{row_index}行,第{col_index}列,物理IP{ip2}不存在\n'.format(
                                    tname=tname, row_index=row_index, col_index=col_index, ip2=ip2)
                                raise NameError
                            else:
                                AssignedIpMappingPublicAndLoadIp.objects.create(
                                    assignedip=assignedip[0],
                                    publicAndloadip=publicAndloadip,
                                    relation=relation,
                                    port=port
                                )
                                break
                        elif col_index == 4:
                            ip2 = str(cell_obj.value.encode('utf-8')).strip()
                            vip = Vip.objects.filter(ip=ip2)
                            if len(vip) == 0:
                                error += '表 {tname} 第{row_index}行,第{col_index}列,vip{ip2}不存在\n'.format(
                                    tname=tname, row_index=row_index, col_index=col_index, ip2=ip2)
                                raise NameError
                            else:
                                VipMappingPublicAndLoadIp.objects.create(
                                    vip=vip[0],
                                    publicAndloadip=publicAndloadip,
                                    relation=relation,
                                    port=port
                                )
                            break
                    else:
                        continue

            except PublicAndLoadIp.DoesNotExist:
                error += '表 {tname} 第{row_index}行,公网或负载ip{ip}不存在\n'.format(
                    tname=tname, row_index=row_index, ip=ip)
                continue
            except AssignedIp.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,物理ip{assignedip}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    assignedip=assignedip)
                continue
            except Vip.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,vip{vip}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    vip=vip)
                continue
            except NameError:
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'vip: %s' % (row_index)
                self._update_tpath()
        return error

    def _addNetworkDevice(self, sheet_name, update):
        # column and field relationship
        _col_defines = {
            0: 'device_num',
            1: 'device_name',
            2: 'port',
            3: 'remarks',
            4: 'vc',
            5: 'binding_device',
            6: 'id',
        }

        error = ''
        tname = 'network_device'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            # 如果有绑定设备的话，记录下，保存后添加相互绑定
            has_binding = False
            _binding_device = None
            try:
                if update:
                    col_index = len(_col_defines)
                    cell_obj = sheet_name.cell(row_index, col_index - 1)
                    if cell_obj.ctype == 0:
                        id_is_none = True
                    else:
                        id_is_none = False
                        instance = NetworkDevice.objects.filter(id=int(cell_obj.value))
                        if len(instance) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,id不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index)
                            raise NameError
                for col_index in range(0, len(_col_defines) - 1):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [5]:
                        # 有绑定设备
                        if cell_obj.value:
                            _device_num = str(cell_obj.value.encode('utf-8')).strip()
                            _binding_device = NetworkDevice.objects.get(device_num=_device_num)
                            edata[_col_defines.get(col_index)] = _binding_device
                            has_binding = True
                        else:
                            edata[_col_defines.get(col_index)] = None
                    else:
                        edata[_col_defines.get(col_index)] = str(cell_obj.value.encode('utf-8')).strip()

                if update and not id_is_none:
                    instance.update(**edata)
                else:
                    d = NetworkDevice(**edata)
                    d.save()
                    # 如果有绑定的话，要给上一条记录绑定当前的设备
                    if has_binding:
                        _binding_device.binding_device = d
                        _binding_device.save()
            except NameError:
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'vip: %s' % (row_index)
                self._update_tpath()

        return error

    def _addNetworkDeviceIp(self, sheet_name, update):
        # column and field relationship
        _col_defines = {
            0: 'network_device',
            1: 'assignedip',
            2: 'opposite_end',
            3: 'id',
        }

        error = ''
        tname = 'network_device_ip'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            # 记录对端设备和ip
            _opposite_end_obj = None
            try:
                if update:
                    col_index = len(_col_defines)
                    cell_obj = sheet_name.cell(row_index, col_index - 1)
                    if cell_obj.ctype == 0:
                        id_is_none = True
                    else:
                        id_is_none = False
                        instance = NetworkDeviceIp.objects.filter(id=int(cell_obj.value))
                        if len(instance) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,id不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index)
                            raise NameError
                for col_index in range(0, len(_col_defines) - 1):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [0]:
                        device_num = str(cell_obj.value.encode('utf-8')).strip()
                        network_device = NetworkDevice.objects.get(device_num=device_num)
                        edata[_col_defines.get(col_index)] = network_device
                    elif col_index in [1]:
                        asip = str(cell_obj.value.encode('utf-8')).strip()
                        assignedip = AssignedIp.objects.get(ip=asip)

                        edata[_col_defines.get(col_index)] = assignedip
                    else:
                        # 如果存在，说明有对端设备
                        # 对端设备一般是上一条记录
                        # 这里的做法是选择网络设备和物理ip，并且没有对端设备的记录，然后取其中一条
                        if not cell_obj.value:
                            has_opposite_end = False
                            edata[_col_defines.get(col_index)] = None
                        else:
                            opposite_end_info = str(cell_obj.value.encode('utf-8')).strip()    # 格式为device_num#1.1.1.1
                            _device_num = opposite_end_info.split('#')[0]
                            _network_device = NetworkDevice.objects.get(device_num=_device_num)
                            _ip = opposite_end_info.split('#')[1]
                            _assignedip = AssignedIp.objects.get(ip=_ip)

                            _network_device_ip_obj = NetworkDeviceIp.objects.filter(network_device=_network_device, assignedip=_assignedip)
                            # 如果能在中间表中找到网络设备和ip的记录，先取对端为None的，
                            # 如果没有，则新建一条(有绑定多个对端的情况)
                            if _network_device_ip_obj:
                                opposite_end = NetworkDeviceIp.objects.filter(
                                    network_device=_network_device, assignedip=_assignedip, opposite_end=None).first()
                                # 如果没有，则新建一条
                                if not opposite_end:
                                    opposite_end = NetworkDeviceIp.objects.create(network_device=_network_device, assignedip=_assignedip, opposite_end=None)
                                edata[_col_defines.get(col_index)] = opposite_end
                                has_opposite_end = True
                                _opposite_end_obj = opposite_end

                            else:
                                raise CmdbImportError()

                if update and not id_is_none:
                    instance.update(**edata)
                else:
                    d = NetworkDeviceIp(**edata)
                    d.save()
                    # 如果有对端设备，需要把对端设备和自身绑定
                    if has_opposite_end:
                        _opposite_end_obj.opposite_end = d
                        _opposite_end_obj.save()
            except NameError:
                continue
            except IpType.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第3列,ip类型不存在{iptype}不存在\n'.format(
                    tname=tname, row_index=row_index, iptype=iptype)
                continue
            except CmdbImportError:
                error += '表 {tname} 第{row_index}行,第{col_index}列,网络设备记录{opposite_end_info}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    opposite_end_info=opposite_end_info)
                continue
            except AssignedIp.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,物理IP{asip}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    asip=asip)
                continue
            except NetworkDevice.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,网络设备{device_num}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    device_num=device_num)
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'vip: %s' % (row_index)
                self._update_tpath()

        return error

    def _addNetworkDeviceInternalIp(self, sheet_name, update):
        # column and field relationship
        _col_defines = {
            0: 'network_device',
            1: 'assignedip',
            2: 'opposite_end',
            3: 'id',
        }

        error = ''
        tname = 'network_device_internal_ip'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                if update:
                    col_index = len(_col_defines)
                    cell_obj = sheet_name.cell(row_index, col_index - 1)
                    if cell_obj.ctype == 0:
                        id_is_none = True
                    else:
                        id_is_none = False
                        instance = NetworkDeviceInternalIp.objects.filter(id=int(cell_obj.value))
                        if len(instance) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,id不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index)
                            raise NameError
                for col_index in range(0, len(_col_defines) - 1):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [0]:
                        device_num = str(cell_obj.value.encode('utf-8')).strip()
                        network_device = NetworkDevice.objects.get(device_num=device_num)
                        edata[_col_defines.get(col_index)] = network_device
                    elif col_index in [1]:
                        asip = str(cell_obj.value.encode('utf-8')).strip()
                        assignedip = AssignedIp.objects.get(ip=asip)

                        edata[_col_defines.get(col_index)] = assignedip
                    else:
                        # 这里没有对端设备，全部设置为None
                        edata[_col_defines.get(col_index)] = None

                if update and not id_is_none:
                    instance.update(**edata)
                else:
                    d = NetworkDeviceInternalIp(**edata)
                    d.save()
            except IpType.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第3列,ip类型不存在{iptype}不存在\n'.format(
                    tname=tname, row_index=row_index, iptype=iptype)
                continue
            except NameError:
                continue
            except AssignedIp.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,物理IP{asip}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    asip=asip)
                continue
            except NetworkDevice.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,网络设备{device_num}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    device_num=device_num)
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'vip: %s' % (row_index)
                self._update_tpath()

        return error

    def _addNetworkDeviceExternalIp(self, sheet_name, update):
        # column and field relationship
        _col_defines = {
            0: 'network_device',
            1: 'assignedip',
            2: 'opposite_end',
            3: 'id',
        }

        error = ''
        tname = 'network_device_external_ip'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                if update:
                    col_index = len(_col_defines)
                    cell_obj = sheet_name.cell(row_index, col_index - 1)
                    if cell_obj.ctype == 0:
                        id_is_none = True
                    else:
                        id_is_none = False
                        instance = NetworkDeviceExternalIp.objects.filter(id=int(cell_obj.value))
                        if len(instance) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,id不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index)
                            raise NameError
                for col_index in range(0, len(_col_defines) - 1):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [0]:
                        device_num = str(cell_obj.value.encode('utf-8')).strip()
                        network_device = NetworkDevice.objects.get(device_num=device_num)
                        edata[_col_defines.get(col_index)] = network_device
                    elif col_index in [1]:
                        asip = str(cell_obj.value.encode('utf-8')).strip()
                        assignedip = AssignedIp.objects.get(ip=asip)

                        edata[_col_defines.get(col_index)] = assignedip
                    else:
                        # 这里没有对端设备，全部设置为None
                        edata[_col_defines.get(col_index)] = None

                if update and not id_is_none:
                    instance.update(**edata)
                else:
                    d = NetworkDeviceExternalIp(**edata)
                    d.save()
            except IpType.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第3列,ip类型不存在{iptype}不存在\n'.format(
                    tname=tname, row_index=row_index, iptype=iptype)
                continue
            except NameError:
                continue
            except AssignedIp.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,物理IP{asip}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    asip=asip)
                continue
            except NetworkDevice.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,网络设备{device_num}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    device_num=device_num)
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'vip: %s' % (row_index)
                self._update_tpath()

        return error

    def _addNetworkDeviceLoopbackIp(self, sheet_name, update):
        # column and field relationship
        _col_defines = {
            0: 'network_device',
            1: 'assignedip',
            2: 'opposite_end',
            3: 'id',
        }

        error = ''
        tname = 'network_device_loopback_ip'

        for row_index in range(1, sheet_name.nrows):
            edata = {}
            try:
                if update:
                    col_index = len(_col_defines)
                    cell_obj = sheet_name.cell(row_index, col_index - 1)
                    if cell_obj.ctype == 0:
                        id_is_none = True
                    else:
                        id_is_none = False
                        instance = NetworkDeviceLoopbackIp.objects.filter(id=int(cell_obj.value))
                        if len(instance) == 0:
                            error += '表 {tname} 第{row_index}行,第{col_index}列,id不存在\n'.format(
                                tname=tname, row_index=row_index, col_index=col_index)
                            raise NameError
                for col_index in range(0, len(_col_defines) - 1):
                    cell_obj = sheet_name.cell(row_index, col_index)
                    if col_index in [0]:
                        device_num = str(cell_obj.value.encode('utf-8')).strip()
                        network_device = NetworkDevice.objects.get(device_num=device_num)
                        edata[_col_defines.get(col_index)] = network_device
                    elif col_index in [1]:
                        asip = str(cell_obj.value.encode('utf-8')).strip()
                        assignedip = AssignedIp.objects.get(ip=asip)

                        edata[_col_defines.get(col_index)] = assignedip
                    else:
                        # 这里没有对端设备，全部设置为None
                        edata[_col_defines.get(col_index)] = None

                if update and not id_is_none:
                    instance.update(**edata)
                else:
                    d = NetworkDeviceLoopbackIp(**edata)
                    d.save()
            except IpType.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第3列,ip类型不存在{iptype}不存在\n'.format(
                    tname=tname, row_index=row_index, iptype=iptype)
                continue
            except NameError:
                continue
            except AssignedIp.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,物理IP{asip}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    asip=asip)
                continue
            except NetworkDevice.DoesNotExist:
                error += '表 {tname} 第{row_index}行,第{col_index}列,网络设备{device_num}不存在\n'.format(
                    tname=tname, row_index=row_index, col_index=col_index,
                    device_num=device_num)
                continue
            except Exception as e:
                info = {
                    'tname': tname,
                    'row_index': row_index,
                    'col_index': col_index,
                    'e': str(e)
                }
                error += '表 {tname} 第{row_index}行,第{col_index}列导入失败,错误:{e}\n'.format(
                    **info)
                continue
            finally:
                # print 'vip: %s' % (row_index)
                self._update_tpath()

        return error
