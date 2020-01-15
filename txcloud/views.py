from django.shortcuts import render
from django.http import JsonResponse
from assets.models import GameProject
from assets.models import HostInitialize
from assets.models import HostInitializeLog
from assets.models import Room
from assets.models import Business
from assets.models import TecentCloudAccount
from assets.models import Area
from assets.utils import get_ip
from myworkflows.models import SpecialUserParamConfig
from txcloud.TXCloud import TXCloudTC3
from txcloud.TXCloud import TXCloudV2
from txcloud.utils import gen_password
from txcloud.utils import get_host_init_business
from txcloud.utils import get_syndic_ip
from txcloud.models import Region
from txcloud.models import ServerZoneNumber
from txcloud.models import MysqlZoneConfig
from mysql.models import MysqlInstance
from mysql.models import MyqlHistoryRecord
from mysql.utils import ws_update_mysql_list
from tasks import do_query_txserver_status
from tasks import query_mysql_info
from tasks import query_txcloud_async_result
from cmdb.settings import PRODUCTION_ENV
from cmdb.logs import PurchaseCloudServerLog
from collections import defaultdict

import json
import time


def get_cloud_platform_administrator():
    """获取云平台管理员"""
    obj, created = SpecialUserParamConfig.objects.get_or_create(param='CLOUD_PLATFORM_ADMINISTRATOR',
                                                                defaults={
                                                                    'param': 'CLOUD_PLATFORM_ADMINISTRATOR',
                                                                    'remark': '云平台管理员'})
    return obj.get_user_obj_list()


def purchase_server(request):
    """购买腾讯云服务器"""
    if request.method == 'GET':
        if request.user in get_cloud_platform_administrator():
            projects = GameProject.objects.prefetch_related('cloud_account').filter(status=1)
            projects = [{'id': p.id, 'text': p.project_name, 'cloud_account': 1 if p.cloud_account else 0} for p in
                        projects]
            rooms = [{'id': r.id, 'text': r.area.chinese_name + '-' + r.room_name} for r in Room.objects.all()]
            success, business = get_host_init_business()
            business = [{'id': b, 'text': b} for b in business]
            period = {1: '1个月', 2: '2个月', 3: '3个月', 6: '半年', 12: '1年', 24: '2年', 36: '3年', 48: '4年', 60: '5年'}
            period = sorted(period.items(), key=lambda x: x[0], reverse=False)
            return render(request, 'purchase_txcloud_server.html',
                          {'projects': projects, 'period': period, 'rooms': rooms, 'business': business})
        else:
            return render(request, '403.html')


def get_server_region(request):
    """获取服务器地域"""
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        success = True
        data = ''
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            project_id = raw_data.get('project', '0')
            if project_id == '0':
                # 选择其中一个帐号即可
                cloud_account = TecentCloudAccount.objects.last()
            else:
                project_obj = GameProject.objects.prefetch_related('cloud_account').get(pk=project_id)
                cloud_account = project_obj.cloud_account
            obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, region='', action='DescribeRegions')
            success, msg = obj.python_request()
            if success:
                data = [
                    {'code': x['region'], 'region': x['region_name'].replace(')', '').replace('(', '-').split('-')[0],
                     'city': x['region_name'].replace(')', '').replace('(', '-').split('-')[1]} for x in msg]
                data.sort(key=lambda x: x['city'])
                data.sort(key=lambda x: x['region'])
                Region.objects.all().delete()
                for r in data:
                    Region.objects.create(**r)
            else:
                raise Exception(msg)

        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def get_server_zone(request):
    """获取服务器可用区"""
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        success = True
        data = ''
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            project_id = raw_data.get('project', '0')
            project_obj = GameProject.objects.prefetch_related('cloud_account').get(pk=project_id)
            cloud_account = project_obj.cloud_account
            region_code = raw_data.get('region_code', '0')
            obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, region=region_code,
                             action='DescribeZones')
            success, msg = obj.python_request()
            if success:
                data = msg
            else:
                raise Exception(msg)

        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def get_instance_type(request):
    """获取实例机型"""
    if request.method == 'POST':
        raw_data = request.POST
        data = []
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            project_id = raw_data.get('project', '0')
            project_obj = GameProject.objects.prefetch_related('cloud_account').get(pk=project_id)
            cloud_account = project_obj.cloud_account
            region_code = raw_data.get('region_code', '0')
            zone = raw_data.get('zone', '0')
            obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, region=region_code,
                             action='DescribeInstanceTypeConfigs',
                             params={"Filters": [{"Name": "zone", "Values": [zone]}]})
            success, msg = obj.python_request()
            if success:
                q = raw_data.get('q', None)
                if q:
                    data = [x for x in msg if q in x['text']]
                else:
                    data = msg
            else:
                raise Exception(msg)

        except Exception as e:
            data = [str(e)]
        finally:
            return JsonResponse(data, safe=False)


def get_instance_config_info(request):
    """获取实例配置"""
    if request.method == 'POST':
        raw_data = request.POST
        data = []
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            project_id = raw_data.get('project', '0')
            project_obj = GameProject.objects.prefetch_related('cloud_account').get(pk=project_id)
            cloud_account = project_obj.cloud_account
            region_code = raw_data.get('region_code', '0')
            zone = raw_data.get('zone', '0')
            charge_mode = raw_data.get('charge_mode', '0')
            obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, region=region_code,
                             action='DescribeZoneInstanceConfigInfos',
                             params={"Filters": [{"Name": "zone", "Values": [zone]},
                                                 {"Name": "instance-charge-type", "Values": [charge_mode]}]})
            success, msg = obj.python_request()
            if success:
                # cpu/内存筛选
                instance_cpu = raw_data.get('instance_cpu', '0')
                instance_memory = raw_data.get('instance_memory', '0')
                if instance_cpu != '0':
                    msg = [x for x in msg if x['cpu'] == instance_cpu]
                if instance_memory != '0':
                    msg = [x for x in msg if x['memory'] == instance_memory]
                msg = [{'id': x['id'],
                        'text': 'CPU：' + x['cpu'] + '核' + ' / ' + '内存：' + x['memory'] + 'GB' + ' / ' + x['text']} for
                       x in msg]

                # 下拉框搜索
                q = raw_data.get('q', None)
                if q:
                    data = [x for x in msg if q in x['text']]
                else:
                    data = msg
            else:
                raise Exception(msg)

        except Exception as e:
            data = [str(e)]
        finally:
            return JsonResponse(data, safe=False)


def get_image_version(request):
    """获取镜像版本"""
    if request.method == 'POST':
        raw_data = request.POST
        data = []
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            project_id = raw_data.get('project', '0')
            project_obj = GameProject.objects.prefetch_related('cloud_account').get(pk=project_id)
            cloud_account = project_obj.cloud_account
            region_code = raw_data.get('region_code', '0')
            image_type = raw_data.get('image_type', '0')
            system_framework = raw_data.get('system_framework', '0')
            operation_system = raw_data.get('operation_system', '0')
            obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, region=region_code,
                             action='DescribeImages',
                             params={"Filters": [{"Name": "image-type", "Values": [image_type]}]})
            success, msg = obj.python_request()
            if success:
                msg = [x for x in msg if system_framework in x['text'] and operation_system in x['text']]
                q = raw_data.get('q', None)
                if q:
                    data = [x for x in msg if q in x['text']]
                else:
                    data = msg
            else:
                raise Exception(msg)

        except Exception as e:
            data = [str(e)]
        finally:
            return JsonResponse(data, safe=False)


def get_server_project(request):
    """获取服务器项目列表数据"""
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        data = []
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            project_id = raw_data.get('project', '0')
            project_obj = GameProject.objects.prefetch_related('cloud_account').get(pk=project_id)
            cloud_account = project_obj.cloud_account
            config = {"Action": "DescribeProject"}
            obj = TXCloudV2(config, cloud_account.secret_id, cloud_account.secret_key, domain='account.api.qcloud.com')
            success, msg = obj.post()
            if success:
                q = raw_data.get('q', None)
                if q:
                    data = [x for x in msg if q in x['text']]
                else:
                    data = msg
            else:
                raise Exception(msg)

        except Exception as e:
            data = [str(e)]
        finally:
            return JsonResponse(data, safe=False)


def get_security_group(request):
    """获取安全组"""
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        data = []
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            project_id = raw_data.get('project', '0')
            project_obj = GameProject.objects.prefetch_related('cloud_account').get(pk=project_id)
            cloud_account = project_obj.cloud_account
            region_code = raw_data.get('region_code', '0')
            obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, region=region_code,
                             action='DescribeSecurityGroups', host="vpc.tencentcloudapi.com", service='vpc')
            success, msg = obj.python_request()
            if success:
                q = raw_data.get('q', None)
                if q:
                    data = [x for x in msg if q in x['text']]
                else:
                    data = msg
            else:
                raise Exception(msg)

        except Exception as e:
            data = [str(e)]
        finally:
            return JsonResponse(data, safe=False)


def inquiry_price(request):
    """服务器购买前面询价"""
    if request.method == 'POST':
        raw_data = json.loads(request.body.decode('utf-8'))
        success = True
        data = ''
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            project_id = raw_data.pop('cmdb_project', '0')
            project_obj = GameProject.objects.prefetch_related('cloud_account').get(pk=project_id)
            cloud_account = project_obj.cloud_account
            region_code = raw_data.pop('Region', '')
            data_disk = raw_data.get('DataDisks', [])
            if not data_disk:
                raw_data.pop('DataDisks', [])
            obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, region=region_code,
                             action='InquiryPriceRunInstances', params=raw_data)
            success, msg = obj.python_request()
            if success:
                data = msg
            else:
                raise Exception(msg)

        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def run_instance(request):
    """购买服务器"""
    if request.method == 'POST':
        success = True
        data = ''
        log = PurchaseCloudServerLog()
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            project_id = raw_data.pop('cmdb_project', '0')
            project_obj = GameProject.objects.prefetch_related('cloud_account').get(pk=project_id)
            cloud_account = project_obj.cloud_account
            room = Room.objects.get(pk=raw_data.pop('room'))
            result, syndic_ip = get_syndic_ip(project_obj, room)
            business = Business.objects.get(business_name=raw_data.pop('business'))
            region_code = raw_data.pop('Region', '')
            random_pass = gen_password()
            raw_data['LoginSettings']['Password'] = random_pass
            data_disk = raw_data.get('DataDisks', [])
            if not data_disk:
                raw_data.pop('DataDisks', [])
            action = 'RunInstances'
            if PRODUCTION_ENV:
                obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, region=region_code, action=action,
                                 params=raw_data)
                success, data = obj.python_request()
            else:
                data = ['ins-r4g9mlye']
            if success:
                log.logger.info('购买腾讯云服务器提交成功: {}'.format(data))
                instance_set = data
                # 插入主机初始化表
                for i in instance_set:
                    host_initialize, created = HostInitialize.objects.update_or_create(instance_id=i,
                                                                                       defaults={
                                                                                           'password': random_pass,
                                                                                           'project': project_obj,
                                                                                           'add_user': request.user,
                                                                                           'instance_id': i,
                                                                                           'room': room,
                                                                                           'business': business,
                                                                                           'syndic_ip': syndic_ip,
                                                                                           'instance_state': 'PENDING'})
                    HostInitializeLog.objects.create(host_initialize=host_initialize)

                    # 异步查询实例创建后运行状态
                    do_query_txserver_status.delay([i], cloud_account.secret_id, cloud_account.secret_key,
                                                   cloud_account.__str__(), region_code)
            else:
                raise Exception(data)

        except Exception as e:
            success = False
            data = str(e)
            log.logger.error('购买腾讯云服务器提交失败: {}'.format(data))
        finally:
            return JsonResponse({'success': success, 'data': data})


def get_server_zone_number(request):
    """获取实例机型可用区数量"""
    if request.method == 'POST':
        success = True
        data = 'ok'
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            # 选择其中一个帐号即可
            cloud_account = TecentCloudAccount.objects.last()
            action = 'DescribeZoneInstanceConfigInfos'
            zone_dict = defaultdict(set)
            for r in Region.objects.all():
                obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, region=r.code, action=action)
                success, data = obj.python_request()
                for d in data:
                    zone_dict[d['instance_type']].add(d['zone'])
            for i, z in zone_dict.items():
                ServerZoneNumber.objects.update_or_create(instance_type=i,
                                                          defaults={'zone_detail': json.dumps(list(z))})
        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def mysql_purchase(request):
    """购买腾讯云数据库填单页面"""
    if request.method == 'GET':
        if request.user in get_cloud_platform_administrator():
            projects = GameProject.objects.prefetch_related('cloud_account').filter(status=1)
            projects = [{'id': p.id, 'text': p.project_name, 'cloud_account': 1 if p.cloud_account else 0} for p in
                        projects]
            areas = [{'id': a.id, 'text': a.chinese_name} for a in Area.objects.all()]
            purchase_period = [
                {'id': 1, 'text': '1个月'},
                {'id': 2, 'text': '2个月'},
                {'id': 3, 'text': '3个月'},
                {'id': 4, 'text': '4个月'},
                {'id': 5, 'text': '5个月'},
                {'id': 6, 'text': '半年'},
                {'id': 7, 'text': '7个月'},
                {'id': 8, 'text': '8个月'},
                {'id': 9, 'text': '9个月'},
                {'id': 10, 'text': '10个月'},
                {'id': 11, 'text': '11个月'},
                {'id': 12, 'text': '1年'},
                {'id': 24, 'text': '2年'},
                {'id': 36, 'text': '3年'},
            ]
            return render(request, 'txcloud_mysql_purchase.html',
                          {'projects': projects, 'areas': areas, 'purchase_period': purchase_period})
        else:
            return render(request, '403.html')


def get_mysql_config(request):
    """获取云数据库mysql可售配置信息"""
    if request.method == 'POST':
        success = True
        data = ''
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            # 选择其中一个帐号即可
            cloud_account = TecentCloudAccount.objects.last()
            host = 'cdb.tencentcloudapi.com'
            service = 'cdb'
            action = 'DescribeDBZoneConfig'
            version = '2017-03-20'
            region = json.loads(request.body.decode('utf-8')).get('region_code', '')
            obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, region=region, action=action,
                             version=version, host=host, service=service)
            success, data = obj.python_request()
            if success:
                MysqlZoneConfig.objects.all().delete()
                for d in data:
                    for zone in d['zones']:
                        MysqlZoneConfig.objects.create(region=d['region'], region_name=d['region_name'],
                                                       zone=zone['zone'], zone_name=zone['zone_name'],
                                                       config_data=json.dumps(zone['sell_type']),
                                                       protect_mode=json.dumps(zone['protect_mode']))

            else:
                raise Exception(data)
        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def get_mysql_region(request):
    """获取云数据库mysql地域"""
    if request.method == 'POST':
        success = True
        data = ''
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')

            configs = MysqlZoneConfig.objects.values('region', 'region_name').distinct()
            data = [{'code': x['region'], 'city': x['region_name']} for x in configs]
            data.sort(key=lambda x: x['code'])

        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def get_mysql_zone(request):
    """获取云mysql数据库可用区"""
    if request.method == 'POST':
        success = True
        data = ''
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            region = json.loads(request.body.decode('utf-8')).get('region_code', '')
            zone_list = MysqlZoneConfig.objects.filter(region=region).values('zone', 'zone_name').distinct()
            data = [{'zone': zone['zone'], 'zone_name': zone['zone_name']} for zone in zone_list]
            data.sort(key=lambda x: x['zone'])

        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def get_mysql_framework(request):
    """获取云mysql数据库架构"""
    if request.method == 'POST':
        success = True
        data = ''
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            region = raw_data.get('region', '')
            zone = raw_data.get('zone', '')
            obj = MysqlZoneConfig.objects.filter(region=region, zone=zone)
            if not obj:
                raise Exception('找不到mysql配置信息')

            config_data = json.loads(obj[0].config_data)
            data = list(set([f['framework'] for c in config_data for f in c['configs']]))

        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def get_mysql_engine(request):
    """获取云mysql数据库版本"""
    if request.method == 'POST':
        success = True
        data = ''
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            region = raw_data.get('region', '')
            zone = raw_data.get('zone', '')
            framework = raw_data.get('framework', '')
            obj = MysqlZoneConfig.objects.filter(region=region, zone=zone)
            if not obj:
                raise Exception('找不到mysql配置信息')

            config_data = json.loads(obj[0].config_data)
            protect_mode = json.loads(obj[0].protect_mode)
            config_data = list(filter(lambda x: x['configs'][0]['framework'] == framework, config_data))
            if not config_data:
                raise Exception('该可用区不支持')
            config_data = config_data[0]
            data = {
                'engine_version': json.loads(config_data['engine_version']),
                'configs': config_data['configs'],
                'protect_mode': protect_mode,
            }

        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def get_mysql_price(request):
    """获取云数据库mysql实例价格"""
    if request.method == 'POST':
        success = True
        data = ''
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            project = raw_data.pop('project', None)
            if project is None:
                # 选择其中一个帐号即可
                cloud_account = TecentCloudAccount.objects.last()
            else:
                project_obj = GameProject.objects.prefetch_related('cloud_account').get(pk=project)
                cloud_account = project_obj.cloud_account
            region = raw_data.pop('region', '')
            action = 'DescribeDBPrice'
            version = '2017-03-20'
            host = 'cdb.tencentcloudapi.com'
            service = 'cdb'
            obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, region=region, action=action,
                             version=version, host=host, service=service, params=raw_data)
            success, data = obj.python_request()
        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def get_mysql_default_params(request):
    """获取腾讯云数据库初始化参数"""
    if request.method == 'POST':
        success = True
        data = ''
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            project = raw_data.pop('project', '0')
            if project == '0':
                # 选择其中一个帐号即可
                cloud_account = TecentCloudAccount.objects.last()
            else:
                project_obj = GameProject.objects.prefetch_related('cloud_account').get(pk=project)
                cloud_account = project_obj.cloud_account

            region = raw_data.pop('Region', '')
            action = 'DescribeDefaultParams'
            version = '2017-03-20'
            host = 'cdb.tencentcloudapi.com'
            service = 'cdb'
            obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, region=region, action=action,
                             version=version, host=host, service=service, params=raw_data)
            success, data = obj.python_request()
            if success:
                data = data[0]
            else:
                raise Exception(data)

        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def create_txcloud_mysql(request):
    """创建云数据库实例mysql"""
    if request.method == 'POST':
        success = True
        data = ''
        password = ''
        port = ''
        try:
            if request.user not in get_cloud_platform_administrator():
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            cmdb_project = raw_data.pop('cmdb_project')
            project_obj = GameProject.objects.get(pk=cmdb_project)
            cloud_account = project_obj.cloud_account
            area = raw_data.pop('area')
            area_obj = Area.objects.get(pk=area)
            purpose = raw_data.pop('purpose')
            pay_type = raw_data.pop('pay_type')
            if pay_type == 'PRE_PAID':
                action = 'CreateDBInstance'
            elif pay_type == 'HOUR_PAID':
                action = 'CreateDBInstanceHour'
                raw_data.pop('Period')
            else:
                raise Exception('未知的计费类型')
            region = raw_data.pop('region')
            is_init = raw_data.pop('is_init', '0')

            if is_init == '1':
                # 增加初始化参数
                password = gen_password()
                raw_data['Password'] = password
                lower_case_table_names = raw_data.pop('lower_case_table_names')
                character_set_server = raw_data.pop('character_set_server')
                raw_data['ParamList'] = {'lower_case_table_names': lower_case_table_names,
                                         'character_set_server': character_set_server}
                port = raw_data.get('Port')
            else:
                raw_data.pop('Port')

            version = '2017-03-20'
            host = 'cdb.tencentcloudapi.com'
            service = 'cdb'
            if PRODUCTION_ENV:
                obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, version=version, region=region,
                                 action=action, params=raw_data, host=host, service=service)
                success, data = obj.python_request()
            else:
                data = ['cdb-pxdvxhnk']
            if success:
                # 插入数据库实例列表
                tx_region, created = Region.objects.get_or_create(code=region, defaults={'code': region, 'city': '',
                                                                                         'region': ''})
                for i in data:
                    mysql = MysqlInstance.objects.create(project=project_obj, area=area_obj.chinese_name,
                                                         purpose=purpose,
                                                         port=port, user='root', password=password, cmdb_area=area_obj,
                                                         instance_id=i, status=0, open_wan=0, tx_region=tx_region)
                    # 新增记录
                    source_ip = get_ip(request)
                    MyqlHistoryRecord.objects.create(mysql=mysql, create_user=request.user, type=1, source_ip=source_ip)
                    # 查询实例状态
                    query_mysql_info.delay(region, cloud_account.secret_id, cloud_account.secret_key,
                                           cloud_account.__str__(), [i])
            else:
                raise Exception(data)

        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})


def open_mysql_wan(request):
    """开通数据库外网访问"""
    if request.method == 'POST':
        success = True
        data = 'ok'
        try:
            if not request.user.is_superuser:
                raise Exception('权限受限')
            raw_data = json.loads(request.body.decode('utf-8'))
            mysql_obj = MysqlInstance.objects.get(pk=raw_data.get('id', 0))
            region = mysql_obj.get_tx_region_code()
            instance_id = mysql_obj.instance_id
            if not instance_id:
                raise Exception('InstanceId为空')
            project = mysql_obj.project
            cloud_account = project.cloud_account
            if not cloud_account:
                raise Exception('该项目没有关联云帐号')

            if PRODUCTION_ENV:
                action = 'OpenWanService'
                version = '2017-03-20'
                host = 'cdb.tencentcloudapi.com'
                service = 'cdb'
                params = {
                    'InstanceId': instance_id,
                }
                obj = TXCloudTC3(cloud_account.secret_id, cloud_account.secret_key, version=version, region=region,
                                 action=action, params=params, host=host, service=service)
                success, data = obj.python_request()
            else:
                data = '7227cd44-f628f69e-a30b684c-52783f84'

            if success:
                mysql_obj.status = 3
                mysql_obj.save()
                ws_update_mysql_list()
                # 异步查询腾讯云任务执行结果
                query_txcloud_async_result.delay(region, cloud_account.secret_id, cloud_account.secret_key,
                                                 cloud_account.__str__(), instance_id, data)

        except MysqlInstance.DoesNotExist:
            success = False
            data = '找不到数据库实例'
        except Exception as e:
            success = False
            data = str(e)
        finally:
            return JsonResponse({'success': success, 'data': data})
