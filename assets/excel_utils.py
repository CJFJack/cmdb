"""导出主机数据为Excel的格式
"""

import time
import os

from collections import OrderedDict

import pandas as pd


def gen_host_excel(host_queryset):
    """生成主机导出excel数据
    """

    file_suffix = int(time.time())
    file_name = '主机表' + str(file_suffix) + '.xlsx'
    download_path = os.path.join(os.path.dirname(__file__), 'host_download', file_name)

    data = OrderedDict()
    field_names = ('游戏项目 状态 内网IP 电信IP 联通IP').split()

    for f in field_names:
        data[f] = []

    for h in host_queryset:
        project = h.belongs_to_game_project.project_name
        data['游戏项目'].append(project)

        status = h.get_status_display()
        data['状态'].append(status)

        internal_ip = h.internal_ip
        data['内网IP'].append(internal_ip)

        telecom_ip = h.telecom_ip
        data['电信IP'].append(telecom_ip)

        unicom_ip = h.unicom_ip
        data['联通IP'].append(unicom_ip)

    writer = pd.ExcelWriter(download_path, engine='xlsxwriter')
    df = pd.DataFrame(data)
    df.to_excel(writer, 'Sheet1', index=False)

    # 设置一些格式
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 30)
    worksheet.set_column('D:D', 30)
    worksheet.set_column('E:E', 30)
    writer.save()

    return file_name, True
