"""获取手游cdn根和目录的配置
"""

WEB_URL = {
    'snsy': {
        'cn': 'http://web.manager.chuangyunet.com/admin.php?s=ApiServer/getCdnList/game_id/5/'
    },
    'syjy': {
        'cn': 'http://web.manager.chuangyunet.com/admin.php?s=ApiServer/getCdnList/game_id/2/',
        'vn': 'http://web_manager.jysy.kiemvumobi.360game.vn/admin.php?s=ApiServer/getCdnList/game_id/2/',
        'tw': 'http://servermanager.gat.chuangyunet.com/admin.php?s=ApiServer/getCdnList/game_id/2/',
    },
    'sn3d': {
        'cn': 'http://web.manager.forcegames.cn/admin.php?s=ApiServer/getCdnList/game_id/11/',
    },
}


CLIENT_TYPE = {
    'snsy': {
        'cn': ['cn_ios', 'cn_android'],
    },
    'syjy': {
        'cn': ['ios', 'android'],
        'vn': ['ios', 'android'],
        'tw': ['ios', 'android'],
    }
}


CDN_ROOT_URL = {
    'snsy': {
        'cn': ['res.snsy.chuangyunet.com'],
    },
    'syjy': {
        'cn': ['cdncy.jysy.chuangyunet.com'],
        'vn': ['kvm.vcdn.vn/real'],
        'tw': ['d2ixemx6rpy7ut.cloudfront.net'],
    }
}
