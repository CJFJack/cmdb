"""导出热更新数据为Excel的格式
"""

import time
import os

import pandas as pd
from collections import OrderedDict

from myworkflows.models import ServerHotUpdate, ClientHotUpdate
from assets.models import Area


def gen_hotupdate_excel(project_name_en, hotupdate_iter):
    if project_name_en in ('snsy',):
        file_suffix = int(time.time())
        file_name = '热更新汇总' + str(file_suffix) + '.xlsx'
        download_path = os.path.join(os.path.dirname(__file__), 'hotupdate_download', file_name)

        data = OrderedDict()
        field_names = ('时间 项目 类型 申请人 标题 原因 地区 '
                       '后端版本号 运营平台名 发布系统 详细').split()
        for f in field_names:
            data[f] = []

        for s in hotupdate_iter:
            create_time = s.create_time.strftime('%Y-%m-%d %H:%M')
            project = s.project.project_name
            hot_type = '后端' if isinstance(s, ServerHotUpdate) else '前端'
            applicant = s.applicant.username
            title = s.title
            reason = s.reason
            area_obj = Area.objects.filter(short_name=s.area_name)
            if area_obj:
                area_name = area_obj[0].chinese_name
            else:
                area_name = s.area_name
            version = s.server_version if isinstance(s, ServerHotUpdate) else ''
            cdn_dir = s.get_cdn_dir_and_type()[0] if isinstance(s, ClientHotUpdate) else ''
            client_type = s.get_cdn_dir_and_type()[1] if isinstance(s, ClientHotUpdate) else ''
            url = 'https://192.168.100.66/myworkflows/myworkflow_hotupdate/?update_type=' + hot_type + '&id=' + str(s.id)
            link = '=HYPERLINK("%s", "查看")' % (url)
            data['时间'].append(create_time)
            data['项目'].append(project)
            data['类型'].append(hot_type)
            data['申请人'].append(applicant)
            data['标题'].append(title)
            data['原因'].append(reason)
            data['地区'].append(area_name)
            data['后端版本号'].append(version)
            data['运营平台名'].append(cdn_dir)
            data['发布系统'].append(client_type)
            data['详细'].append(link)

        writer = pd.ExcelWriter(download_path, engine='xlsxwriter')
        df = pd.DataFrame(data)
        df.to_excel(writer, 'Sheet1', index=False)
        # 设置一些格式
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        # 换行
        new_line_fmt = workbook.add_format({'text_wrap': True})
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('E:E', 60)
        worksheet.set_column('F:F', 60, new_line_fmt)
        worksheet.set_column('I:I', 15, new_line_fmt)
        worksheet.set_column('J:J', 15, new_line_fmt)
        writer.save()

        return file_name, True

    else:
        raise Exception('没有和运维对接该项目')
