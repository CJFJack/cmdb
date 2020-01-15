# -*- encoding: utf-8 -*-

import requests
import json


def BScloudRefresh(type, objs, token):
    """白山云CDN刷新"""
    try:
        url = "https://api.qingcdn.com/v2/cache/refresh?token="
        post_url = url + token
        headers = {"Content-Type": "application/json"}
        data = {
            "urls": objs,
            "type": type,
        }
        postdata = json.dumps(data)
        res = requests.post(post_url, data=postdata, headers=headers, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            if r['code'] == 0:
                task_id = r['data']['task_id']
                return {'success': True, 'task_id': task_id}
            else:
                msg = r['data']['err_urls']
                return {'success': False, 'msg': msg}
        else:
            return {'success': False, 'msg': str(res)}
    except Exception as e:
        return {'success': False, 'msg': str(e)}


def BScloudRefreshResultQuery(task_id, token):
    """查询白山云CDN刷新结果"""
    try:
        url = "https://api.qingcdn.com/v2/cache/refresh?token="
        post_url = url + token + '&task_id=' + task_id
        res = requests.get(post_url, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            if r['code'] == 0:
                status = r['data']['list'][0]['status']
                return {'success': True, 'status': status}
            else:
                return {'success': False, 'status': r['message']}
        else:
            return {'success': False, 'msg': str(res)}
    except Exception as e:
        return {'success': False, 'msg': str(e)}


def BScloudRefreshResultQueryByTime(token, start_time=None, end_time=None):
    """根据时间范围查询白山云CDN刷新结果"""
    try:
        url = "https://api.qingcdn.com/v2/cache/refresh?token="
        if start_time is not None and end_time is not None:
            post_url = url + token + '&start_time=' + start_time + '&end_time=' + end_time + '&page_number=100'
        else:
            raise Exception('参数缺失')
        res = requests.get(post_url, timeout=60, verify=False)
        if res.status_code == 200:
            r = res.json()
            if r['code'] == 0:
                msg = r['data']['list']
                return {'success': True, 'msg': msg}
            else:
                return {'success': False, 'msg': r['message']}
        else:
            return {'success': False, 'msg': str(res)}
    except Exception as e:
        return {'success': False, 'msg': str(e)}


if __name__ == '__main__':
    # res = BScloudRefresh(type='dir', token="e1d763c033b7d861ce1f228371a294dc", objs=['http://resslqy3d.forcegames.cn/c1/', 'http://resslqy3d.forcegames.cn/c1/'])
    # if res['success']:
    #     print(res['task_id'])
    #     print(BScloudRefreshResultQuery(task_id=res['task_id'], token="e1d763c033b7d861ce1f228371a294dc"))
    # else:
    #     print(res['msg'])

    # print(BScloudRefreshResultQuery(token="e1d763c033b7d861ce1f228371a294dc", task_id='81961057'))

    print(BScloudRefreshResultQueryByTime(token="12312412513634675475686583568", start_time='2019-01-16', end_time='2019-01-16'))
