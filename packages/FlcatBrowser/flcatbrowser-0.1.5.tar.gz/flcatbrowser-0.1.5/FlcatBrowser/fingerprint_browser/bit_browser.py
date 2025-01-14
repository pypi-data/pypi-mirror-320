import json
import loguru
import requests

# 比特浏览器

url = "http://127.0.0.1:54345"
headers = {'Content-Type': 'application/json'}

def open_browser(id):
    json_data = {"id": f'{id}'}
    res = requests.post(f"{url}/browser/open", data=json.dumps(json_data), headers=headers).json()
    return res

def create_and_open_browser(self):
    self.browser_id = create_browser()
    browser_info = open_browser(self.browser_id)
    browser_http = browser_info['data']['http']
    return browser_http

def create_browser(browser_id = "",proxy_host = "", proxy_port = "",  proxy_user_name = "", proxy_password = ""):  # 创建或者更新窗口，指纹参数 browserFingerPrint 如没有特定需求，只需要指定下内核即可，如果需要更详细的参数，请参考文档
    json_data = {
        'name': 'google',  # 窗口名称
        'remark': '',  # 备注
        'proxyMethod': 2,  # 代理方式 2自定义 3 提取IP
        # 代理类型  ['noproxy', 'http', 'https', 'socks5', 'ssh']
        'proxyType': 'http',
        'host': proxy_host,  # 代理主机
        'port': proxy_port,  # 代理端口
        'proxyUserName': proxy_user_name,  # 代理账号
        "proxyPassword": proxy_password, # 代理密码
        "browserFingerPrint": {  # 指纹对象
            'coreVersion': '124'  # 内核版本，注意，win7/win8/winserver 2012 已经不支持112及以上内核了，无法打开
        },
        'syncTabs': False
    }
    if browser_id != '':
        json_data.update({'id': browser_id})

    res = requests.post(f"{url}/browser/update",
                        data=json.dumps(json_data), headers=headers).json()
    browser_id = res['data']['id']
    return browser_id

def close_browser(id):  # 关闭窗口
    json_data = {'id': f'{id}'}
    res = requests.post(f"{url}/browser/close",
                        data=json.dumps(json_data), headers=headers).json()
    loguru.logger.info("[关闭窗口]:%s", json.dumps(res))