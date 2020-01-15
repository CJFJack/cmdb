# -*- encoding: utf-8 -*-

"""热更新后端传文件到管理机的配置
"""

RSYNC_MANAGERS = [
    {
        "project": "ssss", "area": "大陆", "ip": "123.207.124.150",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/ssss.password", "port": 10022
    },
    {
        "project": "snqxz", "area": "台湾", "ip": "203.66.5.37",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/snqxz_taiwan.password", "port": 10022
    },
    {
        "project": "snqxz", "area": "越南", "ip": "203.66.5.37",
        "module": "cmdb_hot_server_vng", "user": "xyyo_user", "pass_file": "/etc/snqxz_yuenan.password", "port": 10022
    },
    {
        "project": "snqxz", "area": "大陆", "ip": "122.227.23.166",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/snqxz_dalu.password", "port": 10022
    },
    {
        "project": "snqxz", "area": "英语", "ip": "119.28.62.182",
        "module": "cmdb_snqxz_en", "user": "cmdb_hot", "pass_file": "/etc/snqxz_en.password", "port": 10022
    },
    {
        "project": "jyjh", "area": "大陆YY", "ip": "61.160.42.144",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/jyjh_daluyy.password", "port": 30000
    },
    {
        "project": "jyjh", "area": "大陆QQ", "ip": "119.29.94.221",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/jyjh_daluqq.password", "port": 10022
    },
    {
        "project": "jyjh", "area": "台湾", "ip": "203.74.37.187",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/jyjh_taiwan.password", "port": 30000
    },
    {
        "project": "jyjh", "area": "越南", "ip": "203.74.37.187",
        "module": "cmdb_hot_server_vn", "user": "cmdb_user", "pass_file": "/etc/jyjh_taiwan.password", "port": 30000
    },
    {
        "project": "jyjh", "area": "韩国", "ip": "211.110.141.34",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/jyjh_hanguo.password", "port": 30000
    },
    {
        "project": "snsy", "area": "大陆", "ip": "119.29.208.40",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/snsy_dalu.password", "port": 10022
    },
    {
        "project": "syjy", "area": "大陆", "ip": "139.199.172.173",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/sysj_dalu.password", "port": 10022
    },
    {
        "project": "syjy", "area": "越南", "ip": "61.28.243.14",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/sysj_vn.password", "port": 10022
    },
    {
        "project": "syjy", "area": "台湾", "ip": "119.28.140.163",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/syjy_tw.password", "port": 10022
    },

    {
        "project": "syjy", "area": "越南", "ip": "61.28.243.14",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/syjy_vn.password", "port": 10022
    },
    {
        "project": "h5cc", "area": "大陆创畅", "ip": "111.230.135.108",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/h5cc.password", "port": 10022
    },
    {
        "project": "h5cc", "area": "大陆奇域", "ip": "193.112.132.153",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/h5cc.password", "port": 10022
    },
    {
        "project": "h5cc", "area": "台湾创畅", "ip": "47.52.21.173",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/h5cc.password", "port": 10022
    },
    {
        "project": "snsy", "area": "越南", "ip": "61.28.254.136",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/snsy_vn.password", "port": 10022
    },
    {
        "project": "mjfz", "area": "大陆创畅", "ip": "129.204.29.8",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/mjfz.password", "port": 10022
    },
    {
        "project": "slqy3d", "area": "大陆", "ip": "129.204.138.89",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/slqy3d.password", "port": 10022
    },
    {
        "project": "cyh5s7", "area": "大陆", "ip": "129.204.130.25",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/cyh5s7_cn.pass", "port": 10022
    },
    {
        "project": "sn3d", "area": "大陆", "ip": "123.207.234.37",
        "module": "cmdb_hot_server", "user": "cmdb_user", "pass_file": "/etc/sn3d_cn.password", "port": 10022
    },
]

RSYNC_MAP = {
    'ssss': {
        'hot_client': {
            '大陆': ['cn'],
        },
        'hot_server': {
            '大陆': ['cn'],
        }
    },
    'snqxz': {
        'hot_client': {
            '大陆': ['cn'],
            '台湾': ['tw'],
            '越南': ['vn'],
            '英语': ['en'],
        },
        'hot_server': {
            '大陆': ['cn'],
            '台湾': ['tw'],
            '越南': ['vn'],
            '英语': ['en'],
        }
    },
    'jyjh': {
        'hot_client': {
            '大陆YY': ['cn_yy'],
            '大陆QQ': ['cn_qq'],
            '台湾': ['tw'],
            '韩国': ['kr'],
            '越南': ['vn'],
        },
        'hot_server': {
            '大陆YY': ['cn_yy'],
            '大陆QQ': ['cn_qq'],
            '台湾': ['tw'],
            '韩国': ['kr'],
            '越南': ['vn'],
        }
    },
    'snsy': {
        'hot_client': {
            '大陆': ['cn'],
        },
        'hot_server': {
            '大陆': ['cn'],
        }
    },
    'syjy': {
        'hot_client': {
            '大陆': ['cn'],
            '越南': ['vn'],
            '台湾': ['tw'],
        },
        'hot_server': {
            '大陆': ['cn'],
            '越南': ['vn'],
            '台湾': ['tw'],
        },
    },
    'csxy': {
        'hot_client': {
            '大陆': ['cn'],
            '香港': ['hk'],
            '新马泰': ['xmt'],
        },
        'hot_server': {
            '大陆': ['cn'],
            '香港': ['hk'],
            '新马泰': ['xmt'],
        }
    },
    'h5cc': {
        'hot_client': {
            '大陆创畅': ['cn_cc'],
            '大陆奇域': ['cn_qy'],
            '台湾创畅': ['tw'],
        },
        'hot_server': {
            '大陆创畅': ['cn_cc'],
            '大陆奇域': ['cn_qy'],
            '台湾创畅': ['tw'],
        }
    },
    'mjfz': {
        'hot_client': {
            '大陆创畅': ['cn'],
        },
        'hot_server': {
            '大陆创畅': ['cn'],
        }
    },
    'slqy3d': {
        'hot_client': {
            '大陆': ['cn'],
        },
        'hot_server': {
            '大陆': ['cn'],
        }
    },
    'cyh5s7': {
        'hot_client': {
            '大陆': ['cn'],
        },
        'hot_server': {
            '大陆': ['cn'],
        }
    },
    'sn3d': {
        'hot_client': {
            '大陆': ['cn'],
        },
        'hot_server': {
            '大陆': ['cn'],
        }
    },
}

# 项目英文名到celery任务队列的对应关系
PROJECT_CELERY_QUEUE_MAP = {
    'file_push8': ['jyjh', 'snqxz', 'ssss', 'csxy', 'h5cc'],
    'file_push15': ['snsy', 'syjy', 'sn3d'],
    'file_push_cc': ['mjfz'],
    'file_push_slqy3d_cn': ['slqy3d'],
    'file_push_cyh5s7': ['cyh5s7'],
}

CSXY_TYPES = ['android', 'ios', 'iosmj2', 'iosmj4']
CSXY_TYPES = {
    'cn': ['android', 'ios', 'iosmj2', 'iosmj4'],
    'hk': ['android', 'ios'],
    'xmt': ['android', 'ios'],
}
