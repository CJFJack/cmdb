# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import os
import sys
import random
import base64
import time
from datetime import datetime
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session
from txcloud.utils import get_server_zone_number

"""
secret_id = "sfsdfsdfsdfsdasdgasgasdg"
secret_key = "sfsadgadsgasdgasdga"
region = "ap-guangzhou"
action = "DescribeZoneInstanceConfigInfos"
version = "2017-03-12"
params = {"Filters": [{"Name": "zone", "Values": ["ap-guangzhou-4"]}, {"Name": "instance-charge-type", "Values": ["PREPAID"]}]}
"""


class TXCloudTC3(object):
    """腾讯云: 认证方式TC3"""

    def __init__(self, secret_id, secret_key, region, action, params={}, version="2017-03-12",
                 host="cvm.tencentcloudapi.com", service='cvm', **kwargs):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.action = action
        self.version = version
        self.params = params

        self._service = service
        self._host = host
        self._endpoint = "https://" + self._host
        self._algorithm = "TC3-HMAC-SHA256"
        self._timestamp = int(time.time())
        self._date = datetime.utcfromtimestamp(self._timestamp).strftime("%Y-%m-%d")
        self._credential_scope = self._date + "/" + self._service + "/" + "tc3_request"
        self._signed_headers = "content-type;host"
        self._payload = json.dumps(self.params)

    def __canonical(self):
        # 步骤 1：拼接规范请求串
        http_request_method = "POST"
        canonical_uri = "/"
        canonical_querystring = ""
        ct = "application/json; charset=utf-8"
        canonical_headers = "content-type:%s\nhost:%s\n" % (ct, self._host)
        hashed_request_payload = hashlib.sha256(self._payload.encode("utf-8")).hexdigest()
        canonical_request = (http_request_method + "\n" +
                             canonical_uri + "\n" +
                             canonical_querystring + "\n" +
                             canonical_headers + "\n" +
                             self._signed_headers + "\n" +
                             hashed_request_payload)
        return canonical_request

    def __string_to_sign(self):
        # 步骤 2：拼接待签名字符串
        canonical_request = self.__canonical()
        hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = (self._algorithm + "\n" +
                          str(self._timestamp) + "\n" +
                          self._credential_scope + "\n" +
                          hashed_canonical_request)
        return string_to_sign

    def __signature(self):
        # 步骤 3：计算签名，计算签名摘要函数
        def sign(key, msg):
            return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

        secret_date = sign(("TC3" + self.secret_key).encode("utf-8"), self._date)
        secret_service = sign(secret_date, self._service)
        secret_signing = sign(secret_service, "tc3_request")
        string_to_sign = self.__string_to_sign()
        signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
        return signature

    def authorization(self):
        # 步骤 4：拼接 Authorization
        signature = self.__signature()
        authorization = (self._algorithm + " " +
                         "Credential=" + self.secret_id + "/" + self._credential_scope + ", " +
                         "SignedHeaders=" + self._signed_headers + ", " +
                         "Signature=" + signature)
        return authorization

    def shell_script(self):
        # 生成shell脚本
        authorization = self.authorization()
        return 'curl -X POST ' + self._endpoint \
               + ' -H "Authorization: ' + authorization + '"' \
               + ' -H "Content-Type: application/json; charset=utf-8"' \
               + ' -H "Host: ' + self._host + '"' \
               + ' -H "X-TC-Action: ' + self.action + '"' \
               + ' -H "X-TC-Timestamp: ' + str(self._timestamp) + '"' \
               + ' -H "X-TC-Version: ' + self.version + '"' \
               + ' -H "X-TC-Region: ' + self.region + '"' \
               + " -d '" + self._payload + "'"

    @staticmethod
    def __format_run_instance_result(response):
        # 格式化创建实例结果输出
        return response['InstanceIdSet']

    @staticmethod
    def __format_describe_instance_result(response):
        # 格式化查询实例状态结果输出
        instance_set = response['InstanceSet']
        return [{'instance_id': i['InstanceId'], 'instance_state': i['InstanceState'],
                 'public_ip': i.get('PublicIpAddresses', [''])[0], 'cpu': i['CPU'],
                 'memory': i['Memory'], 'private_ip': i.get('PrivateIpAddresses', [''])[0]} for i in instance_set]

    @staticmethod
    def __format_describe_region_result(response):
        # 格式化查询地域结果输出
        region_set = response['RegionSet']
        return [{'region': i['Region'], 'region_name': i['RegionName']} for i in region_set]

    @staticmethod
    def __format_describe_zone_result(response):
        # 格式化查询可用区结果输出
        zone_set = response['ZoneSet']
        return [{'zone': i['Zone'], 'zone_name': i['ZoneName']} for i in zone_set]

    @staticmethod
    def __format_instance_type_result(response):
        # 格式化查询实例机型结果输出
        instance_set = response['InstanceTypeConfigSet']
        return [{'id': i['InstanceType'],
                 'text': '机型：' + i['InstanceFamily'] + ' / ' + '规格：' + i['InstanceType'] + ' / ' + 'CPU：' + str(
                     i['CPU']) + '核' + ' / ' + '内存：' + str(i['Memory']) + 'GB'} for i in instance_set]

    @staticmethod
    def __format_image_version_result(response):
        # 格式化查询镜像版本结果输出
        image_set = response['ImageSet']
        return [{'id': i['ImageId'], 'text': i['OsName']} for i in image_set]

    @staticmethod
    def __format_security_group_result(response):
        # 格式化查询安全组结果输出
        group_set = response['SecurityGroupSet']
        return [{'id': i['SecurityGroupId'], 'text': i['SecurityGroupName'] + '-' + i['SecurityGroupDesc']} for i in
                group_set]

    @staticmethod
    def __format_inquiry_price_result(response):
        # 格式化查询价格结果输出
        return response['Price']

    @staticmethod
    def __format_instance_config_info_result(response):
        # 格式化查询实例配置信息输出
        def format_price(price):
            if price.get('ChargeUnit', '') == 'HOUR':
                return str(price['UnitPrice']) + '元/小时'
            return str(price['OriginalPrice']) + '元/月'

        instance_quotaset = response['InstanceTypeQuotaSet']
        instance_quotaset.sort(key=lambda x: float(format_price(x['Price']).split('元')[0]))

        # 判断实例处理器型号，目前只有SA1、SA2两种机型使用AMD型号CPU，其余使用Intel，该信息目前腾讯云还不支持通过API获取(2019.11.25)
        def format_process_type(instance_type):
            if instance_type.split('.')[0] in ('SA1', 'SA2'):
                return 'AMD'
            return 'Intel'

        return [{
            'id': i['InstanceType'],
            'text': '机型：' + i['TypeName'] + ' / ' + '规格：' + i['InstanceType'] + ' / ' + '价格：' + format_price(
                i['Price']) + ' / ' + str(
                get_server_zone_number(i['InstanceType'])) + '个可用区' + ' / ' + '处理器型号：' + format_process_type(
                i['InstanceType']),
            'cpu': str(i['Cpu']), 'memory': str(i['Memory']), 'zone': i['Zone'], 'instance_type': i['InstanceType']}
            for i in instance_quotaset if i['Status'] == 'SELL']

    @staticmethod
    def __format_db_zone_config_result(response):
        # 格式化查询数据库可售配置
        items = response['Items']
        return [
            {
                'region': i['Region'],
                'region_name': i['RegionName'],
                'zones': [
                    {
                        'zone': zone_conf['Zone'],
                        'zone_name': zone_conf['ZoneName'],
                        'protect_mode': zone_conf['ProtectMode'],
                        'sell_type': [
                            {
                                'type_name': s['TypeName'],
                                'engine_version': json.dumps(s['EngineVersion']),
                                'configs': [
                                    {
                                        'framework': c['Type'],
                                        'cpu': c['Cpu'],
                                        'memory': c['Memory'],
                                        "volume_min": c['VolumeMin'],
                                        "volume_max": c['VolumeMax'],
                                        "volume_step": c['VolumeStep'],
                                        "connection": c['Connection'],
                                        "qps": c['Qps'],
                                        "iops": c['Iops'],
                                        "info": c['Info'],
                                    } for c in s['Configs']
                                ]
                            } for s in zone_conf['SellType']
                        ]
                    } for zone_conf in i['ZonesConf'] if zone_conf['Status'] in (1, 2)
                ]
            } for i in items
        ]

    @staticmethod
    def __format_describe_db_price_result(response):
        response.__delitem__('RequestId')
        response['Price'] = '%.2f' % (response['Price'] / 100)
        response['OriginalPrice'] = '%.2f' % (response['OriginalPrice'] / 100)
        return response

    @staticmethod
    def __format_describe_db_default_params_result(response):
        items = response['Items']
        return [{'default': i['Default'], 'value': list(map(lambda x: x.lower(), i['EnumValue']))} for i in items if
                i['Name'] in ('character_set_server',)]

    @staticmethod
    def __format_create_mysql_result(response):
        return response['InstanceIds']

    @staticmethod
    def __format_query_mysql_info_result(response):
        return response['Items']

    @staticmethod
    def __format_open_mysql_wan_result(response):
        return response['AsyncRequestId']

    @staticmethod
    def __format_describe_async_request_result(response):
        return {'status': response['Status'], 'info': response['Info']}

    def python_request(self):
        # python请求
        success = True
        msg = 'ok'
        try:
            headers = {
                'Authorization': self.authorization(),
                'Content-Type': 'application/json; charset=utf-8',
                'Host': self._host,
                'X-TC-Action': self.action,
                'X-TC-Timestamp': str(self._timestamp),
                'X-TC-Version': self.version,
                'X-TC-Region': self.region,
            }
            s = Session()
            s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
            r = s.post(self._endpoint, headers=headers, json=self.params, timeout=30, verify=False)
            # 判断是否错误
            if r.status_code != 200:
                raise Exception(str(r))
            res = r.json()
            error = res['Response'].get('Error', None)
            if error:
                raise Exception(error.get('Message', ''))

            # 根据Action类型格式化返回结果
            if self.action == 'RunInstances':
                msg = self.__format_run_instance_result(res['Response'])
            elif self.action == 'DescribeInstances':
                msg = self.__format_describe_instance_result(res['Response'])
            elif self.action == 'DescribeRegions':
                msg = self.__format_describe_region_result(res['Response'])
            elif self.action == 'DescribeZones':
                msg = self.__format_describe_zone_result(res['Response'])
            elif self.action == 'DescribeInstanceTypeConfigs':
                msg = self.__format_instance_type_result(res['Response'])
            elif self.action == 'DescribeImages':
                msg = self.__format_image_version_result(res['Response'])
            elif self.action == 'DescribeSecurityGroups':
                msg = self.__format_security_group_result(res['Response'])
            elif self.action == 'InquiryPriceRunInstances':
                msg = self.__format_inquiry_price_result(res['Response'])
            elif self.action == 'DescribeZoneInstanceConfigInfos':
                msg = self.__format_instance_config_info_result(res['Response'])
            elif self.action == 'DescribeDBZoneConfig':
                msg = self.__format_db_zone_config_result(res['Response'])
            elif self.action == 'DescribeDBPrice':
                msg = self.__format_describe_db_price_result(res['Response'])
            elif self.action == 'DescribeDefaultParams':
                msg = self.__format_describe_db_default_params_result(res['Response'])
            elif self.action in ('CreateDBInstance', 'CreateDBInstanceHour'):
                msg = self.__format_create_mysql_result(res['Response'])
            elif self.action == 'DescribeDBInstances':
                msg = self.__format_query_mysql_info_result(res['Response'])
            elif self.action == 'OpenWanService':
                msg = self.__format_open_mysql_wan_result(res['Response'])
            elif self.action == 'DescribeAsyncRequestInfo':
                msg = self.__format_describe_async_request_result(res['Response'])
            else:
                msg = json.dumps(res['Response'])

        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return success, msg


"""
secret_id = "AKIDQgp4EE2f9SZUDkMEC3pUxGOZaQ7eFKUS"
secret_key = "770ky6oStBIEzd5LQyOmxzpgjnjfS9fA"
action = "DescribeProject"
config = {"Action": action}
domain = "account.api.qcloud.com"
"""


class TXCloudV2(object):
    """腾讯云: 认证方式v2"""

    def __init__(self, config, secret_id, secret_key, domain):
        self.config = config
        self.domain = domain
        self.url = 'https://' + domain + '/v2/index.php'
        self.id = secret_id
        self.Key = secret_key

    def __auth(self):
        data = {}
        Singna = []
        Random = range(100000)
        number = random.choice(Random)
        data['SecretId'] = self.id
        data['Nonce'] = number
        data['Timestamp'] = int(time.time())
        data = dict(data, **self.config)
        base = sorted(data.items(), key=lambda data: data[0])
        for i in base:
            Singna.append(str(i[0]) + '=' + str(i[1]) + '&')  # end='')
            result = 'POST' + self.domain + '/v2/index.php?' + ''.join(Singna).rstrip('&')
        self.Key = self.Key.encode(encoding='utf-8')
        result = result.encode(encoding='utf-8')
        uri = hmac.new(self.Key, result, digestmod=hashlib.sha1).digest()
        key = base64.b64encode(uri)
        data['Signature'] = key
        return data

    @staticmethod
    def __format_server_project_result(response):
        # 格式化服务器项目结果输出
        data = response['data']
        return [{'id': i['projectId'], 'text': i['projectName'] + '-' + i['projectInfo']} for i in data]

    def post(self):
        success = True
        msg = 'ok'
        try:
            data = self.__auth()
            s = Session()
            s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[408])))
            r = s.post(self.url, data=data, timeout=30, verify=False)
            if r.status_code != 200:
                raise Exception(str(r))
            res = r.json()
            if res['code'] != 0:
                raise Exception(res['message'] + '-' + res['codeDesc'])

            if self.config['Action'] == 'DescribeProject':
                msg = self.__format_server_project_result(res)

        except Exception as e:
            success = False
            msg = str(e)
        finally:
            return success, msg
