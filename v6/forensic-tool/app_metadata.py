"""
应用名称和图标映射配置文件
支持包名到应用名称的映射，以及图标显示
"""

APP_NAME_MAP = {
    # 社交类
    "com.tencent.mm": ("微信", "chat"),
    "com.tencent.mobileqq": ("QQ", "chat"),
    "com.tencent.qqlite": ("QQ轻聊版", "chat"),
    "com.tencent.tim": ("TIM", "chat"),
    "com.alibaba.android.rimet": ("钉钉", "chat"),
    "com.ss.android.ugc.aweme": ("抖音", "social"),
    "com.smile.gifmaker": ("快手", "social"),
    "com.tencent.weishi": ("微视", "social"),
    "com.instagram.android": ("Instagram", "social"),
    "com.facebook.katana": ("Facebook", "social"),
    "com.twitter.android": ("Twitter", "social"),
    "com.zhihu.android": ("知乎", "social"),
    "com.sankuai.meituan.takeoutnew": ("美团外卖", "food"),
    "com.sankuai.meituan": ("美团", "food"),
    "com.sankuai.meituan.im": ("美团点评", "food"),
    "com.ele.me": ("饿了么", "food"),
    "com.dianping.v1": ("大众点评", "food"),

    # 购物类
    "com.taobao.taobao": ("淘宝", "shopping"),
    "com.tmall.wireless": ("天猫", "shopping"),
    "com.jingdong.app.mall": ("京东", "shopping"),
    "com.pinduoduo.pdd": ("拼多多", "shopping"),
    "com.suning.mobile.ebuy": ("苏宁易购", "shopping"),
    "com.gome.minigold": ("国美", "shopping"),
    "com.amazon.mShop.android.shopping": ("亚马逊", "shopping"),

    # 金融类
    "com.eg.android.AlipayGphone": ("支付宝", "finance"),
    "com.unionpay": ("银联", "finance"),
    "com.icbc": ("中国工商银行", "finance"),
    "com.ccb": ("中国建设银行", "finance"),
    "com.boc": ("中国银行", "finance"),
    "com.bankcomm": ("交通银行", "finance"),

    # 音乐视频类
    "com.tencent.qqmusic": ("QQ音乐", "media"),
    "com.kugou.android": ("酷狗音乐", "media"),
    "com.kuwo.kwmusic": ("酷我音乐", "media"),
    "cn.kuwo.player": ("酷我音乐", "media"),
    "com.netease.cloudmusic": ("网易云音乐", "media"),
    "com.tencent.qqlive": ("腾讯视频", "media"),
    "com.youku.phone": ("优酷", "media"),
    "com.iqiyi.i18n": ("爱奇艺", "media"),
    "tv.danmaku.bili": ("哔哩哔哩", "media"),
    "com.bilibili.app.in": ("哔哩哔哩", "media"),

    # 地图导航类
    "com.autonavi.minimap": ("高德地图", "map"),
    "com.baidu.BaiduMap": ("百度地图", "map"),
    "com.tencent.map": ("腾讯地图", "map"),
    "com.mapbar.android.map": ("图吧导航", "map"),
    "com.sogou.map.android.maps": ("搜狗地图", "map"),

    # 工具类
    "com.cleanmaster.security": ("猎豹清理大师", "tool"),
    "cn.ks.ssr": ("手机助手", "tool"),
    "com.tencent.android.qqdownloader": ("腾讯应用宝", "tool"),
    "com.android.packageinstaller": ("应用安装器", "system"),
    "com.android.settings": ("设置", "system"),
    "com.android.contacts": ("联系人", "system"),
    "com.android.mms": ("短信", "system"),
    "com.android.phone": ("电话", "system"),
    "com.android.camera": ("相机", "system"),
    "com.android.gallery3d": ("相册", "system"),
    "com.android.calendar": ("日历", "system"),
    "com.android.calculator2": ("计算器", "system"),
    "com.android.clock": ("时钟", "system"),

    # 办公类
    "cn.wps.moffice_eng": ("WPS Office", "office"),
    "com.microsoft.office.word": ("Word", "office"),
    "com.microsoft.office.excel": ("Excel", "office"),
    "com.microsoft.office.powerpoint": ("PowerPoint", "office"),
    "com.tencent.wework": ("企业微信", "office"),
    "com.larksuite.suite": ("飞书", "office"),
    "com.alibaba.android.dingtalk": ("钉钉", "office"),

    # 游戏类
    "com.tencent.tmgp.sgame": ("王者荣耀", "game"),
    "com.tencent.tmgp.pubgmhd": ("和平精英", "game"),
    "com.miHoYo.GenshinImpact": ("原神", "game"),
    "com.levelinfinite.hotta.gp": ("幻塔", "game"),
    "com.netease.dwrg": ("第五人格", "game"),
    "com.pearlabyss.blackdesertm": ("黑色沙漠", "game"),
    "com.tencent.ig": ("英雄联盟手游", "game"),

    # 学习教育类
    "com.iflytek.inputmethod": ("讯飞输入法", "education"),
    "com.baidu.input": ("百度输入法", "education"),
    "com.tencent.qidian": ("起点读书", "education"),
    "com.zy.flt_ee": ("掌阅", "education"),
    "com.cmcc.cmvideo": ("咪咕视频", "education"),
    "com.peopledailychina": ("人民日报", "education"),
    "com.tencent.news": ("腾讯新闻", "education"),

    # 浏览器类
    "com.UCMobile": ("UC浏览器", "tool"),
    "com.tencent.mtt": ("QQ浏览器", "tool"),
    "com.miui.home": ("小米桌面", "system"),
    "com.huawei.android.launcher": ("华为桌面", "system"),
    "com.oppo.launcher": ("OPPO桌面", "system"),
    "com.vivo.launcher": ("vivo桌面", "system"),
    "com.samsung.android.launcher": ("三星桌面", "system"),

    # 常见系统应用
    "com.android.systemui": ("系统界面", "system"),
    "com.android.settings": ("设置", "system"),
    "com.android.contacts": ("联系人", "system"),
    "com.android.mms": ("短信", "system"),
    "com.android.phone": ("电话", "system"),
    "com.android.camera": ("相机", "system"),
    "com.android.gallery3d": ("相册", "system"),
    "com.android.calendar": ("日历", "system"),
    "com.android.calculator2": ("计算器", "system"),
    "com.android.clock": ("时钟", "system"),
    "com.android.downloads": ("下载管理", "system"),
    "com.android.filemanager": ("文件管理", "system"),
    "com.android.music": ("音乐", "media"),
    "com.android.video": ("视频", "media"),
}

CATEGORY_KEYWORDS = {
    "账号密码": ["password", "passwd", "密码", "pwd", "login", "auth", "token", "secret", "credential", "account", "用户名", "username", "api_key", "api-key"],
    "管理员权限": ["admin", "administrator", "root", "sudo", "su", "管理员", "特权", "privilege", "elevated", "superuser"],
    "网络配置": ["ip", "mac", "network", "wifi", "lan", "wan", "proxy", "端口", "port", "dns", "gateway", "subnet", "netmask", "ssid", "bssid"],
    "数据库连接": ["database", "mysql", "postgresql", "mongodb", "redis", "oracle", "sql", "db_", "connection", "host:", "port:", "username:", "password:"],
    "API密钥": ["api_key", "apikey", "api-key", "secret_key", "access_token", "refresh_token", "bearer", "jwt", "oauth", "client_id", "client_secret"],
    "加密信息": ["encrypt", "decrypt", "cipher", "crypto", "hash", "md5", "sha", "rsa", "aes", "des", "私钥", "公钥", "private_key", "public_key", "证书", "certificate", "cert"],
    "位置信息": ["latitude", "longitude", "lat", "lng", "lat:", "lon:", "gps", "location", "坐标", "经度", "纬度", "位置", "address", "street", "city", "country", "province", "geo"],
    "设备信息": ["imei", "imsi", "device_id", "android_id", "mac_address", "serial", "model", "brand", "manufacturer", "设备", "型号", "硬件", "hardware"],
    "通信记录": ["phone", "mobile", "tel", "call", "sms", "message", "chat", "通话", "短信", "消息", "聊天", "phone_number", "mobile_number", "contact", "联系人"],
    "文件路径": ["path", "dir", "directory", "folder", "file://", "C:\\", "D:\\", "/home", "/usr", "file_path", "filename", "filepath"],
    "日志信息": ["log", "error", "warning", "debug", "info", "trace", "stack", "exception", "crash", "日志", "错误", "警告", "调试", "traceback"],
    "时间戳": ["timestamp", "datetime", "date:", "time:", "created_at", "updated_at", "expire", "expiry", "时间", "日期", "created", "updated"],
    "配置文件": ["config", "settings", "setting", "conf", "cfg", "ini", "xml", "json", "yaml", "yml", "properties", "配置", "设置"],
    "用户数据": ["user", "username", "nickname", "avatar", "profile", "user_id", "uid", "email", "mail", "用户", "昵称", "头像", "资料"],
    "支付信息": ["payment", "pay", "order", "transaction", "trade", "amount", "price", "cost", "money", "currency", "alipay", "wechatpay", "支付", "订单", "交易", "金额", "价格"],
    "会话信息": ["session", "cookie", "csrf", "token", "sid", "会话", "session_id", "csrf_token", "session_token"],
}

CATEGORY_ICONS = {
    "账号密码": "🔐",
    "管理员权限": "👤",
    "网络配置": "🌐",
    "数据库连接": "🗄️",
    "API密钥": "🔑",
    "加密信息": "🔒",
    "位置信息": "📍",
    "设备信息": "📱",
    "通信记录": "📞",
    "文件路径": "📁",
    "日志信息": "📝",
    "时间戳": "⏰",
    "配置文件": "⚙️",
    "用户数据": "👥",
    "支付信息": "💰",
    "会话信息": "🍪",
}

APP_TYPE_ICONS = {
    "chat": "💬",
    "social": "👥",
    "food": "🍔",
    "shopping": "🛒",
    "finance": "💰",
    "media": "🎵",
    "map": "🗺️",
    "tool": "🔧",
    "system": "⚙️",
    "office": "📊",
    "game": "🎮",
    "education": "📚",
    "unknown": "📱",
}

# Windows兼容的图标（文字版本，避免emoji显示问题）
APP_TYPE_ICONS_COMPAT = {
    "chat": "[聊天]",
    "social": "[社交]",
    "food": "[美食]",
    "shopping": "[购物]",
    "finance": "[金融]",
    "media": "[媒体]",
    "map": "[地图]",
    "tool": "[工具]",
    "system": "[系统]",
    "office": "[办公]",
    "game": "[游戏]",
    "education": "[教育]",
    "unknown": "[应用]",
}

def get_app_info(package_name):
    """
    根据包名获取应用名称和类型

    Args:
        package_name: 应用包名

    Returns:
        tuple: (应用名称, 应用类型)
    """
    return APP_NAME_MAP.get(package_name, (package_name, "unknown"))

def get_app_icon(app_type, use_emoji=True):
    """
    根据应用类型获取对应的图标

    Args:
        app_type: 应用类型
        use_emoji: 是否使用emoji图标（Windows下可能显示异常）

    Returns:
        str: 图标字符串
    """
    icon_map = APP_TYPE_ICONS if use_emoji else APP_TYPE_ICONS_COMPAT
    return icon_map.get(app_type, APP_TYPE_ICONS["unknown"] if use_emoji else APP_TYPE_ICONS_COMPAT["unknown"])

def classify_content_enhanced(content):
    """
    增强的内容分类，使用关键词匹配

    Args:
        content: 要分类的内容

    Returns:
        str: 分类名称
    """
    content_lower = content.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in content_lower:
                return category

    return "其他"

def get_category_icon(category):
    """
    获取分类对应的图标

    Args:
        category: 分类名称

    Returns:
        str: 图标字符串
    """
    return CATEGORY_ICONS.get(category, "📄")

def get_all_categories():
    """
    获取所有分类列表

    Returns:
        list: 分类名称列表
    """
    return list(CATEGORY_KEYWORDS.keys())
