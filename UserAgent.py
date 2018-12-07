#ua类，省去每次再代码里修改不同的UA的麻烦

class UserAgentBox:
    init_ok = 0
    wap_spider = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25(compatible; Sogou wap spider/4.0; http://www.sogou.com/docs/help/webmasters.htm#07)'
    pc_spider = 'Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)'
    wap_normal_user = 'Mozilla/5.0 (Linux; U; Android 7.0; en-us; MI 5 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.146 Mobile Safari/537.36 XiaoMi/MiuiBrowser/9.0.3'
    pc_normal_user = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'

    def __init__(self):
        self.init_ok = 1