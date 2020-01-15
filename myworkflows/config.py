# -*- encoding: utf-8 -*-

"""流程的一些配置文件
"""

USERADD = 'user/user_add/'

CLIENT_HOT = 'hot/hot_update/'

# 原力电脑故障问题分类对应的处理人员
FAILURE_DECLARE_WITH_ADMIN = {
    1: ['梁家龙', '赖名耀'],
    2: ['梁家龙', '赖名耀'],
    3: ['梁家龙', '赖名耀'],
    4: ['梁家龙', '赖名耀'],
    5: ['梁家龙', '赖名耀'],
    6: ['梁家龙', '赖名耀'],
    7: ['梁家龙', '赖名耀'],
    8: ['梁家龙', '赖名耀'],
}

# 原力wifi管理员
WIFI_WITH_ADMIN = ['梁家龙', '赖名耀']

MACHINE_CONFIG = [
    {'id': 0, 'text': 'CPU:4核-内存:8G-硬盘:100G'},
    {'id': 1, 'text': 'CPU:8核-内存:8G-硬盘:100G'},
    {'id': 2, 'text': 'CPU:8核-内存:16G-硬盘:100G'},
    {'id': 3, 'text': '自定义'},
]

# 网络管理员
NETWORK_ADMINISTRATOR = [
    '梁家龙', '赖名耀', '姚伟楠'
]

# 服务器申请管理员
MACHINE_ADMINISTRATOR = [
    '梁保明', '梁家龙', '黎小龙'
]

# 创畅网络管理员
CC_NETWORK_ADMINISTRATOR = [
    '姚伟楠'
]

# 云平台负责人
YUN_PLATFORM_ADMINISTRATOR = [
    '梁家龙'
]
