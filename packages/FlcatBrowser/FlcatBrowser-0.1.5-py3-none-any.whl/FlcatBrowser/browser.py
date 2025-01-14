from abc import abstractmethod
import os
import threading
import time
from DrissionPage import ChromiumPage, ChromiumOptions
import loguru
from .utils.port import find_free_port
from .website import BaseWebsite
class BaseBrowser:
    """
    Browser类负责业务逻辑与页面操作。
    """

    def __init__(self, browser_id, data_dir= "", proxy_ip = ""):
        self.browser_id = browser_id
        self.data_dir= data_dir
        self.proxy_ip = proxy_ip
        self.website: "BaseWebsite" = None
        self._init_browser()
        self._after_init_browser()

    def _init_browser(self):
        try:
            options = ChromiumOptions().auto_port().set_paths(local_port=find_free_port(),
                user_data_path=os.path.join(self.data_dir ,f"user/{self.browser_id}"),
                cache_path=os.path.join(self.data_dir ,"cache"))
        
            # 代理ip只支持无验证的代理
            if self.proxy_ip:
                options.set_proxy(self.proxy_ip)

            try:
                self.page = ChromiumPage(addr_or_opts=options)
            except Exception as e:
                loguru.logger.exception(e)
                tip="\n启动浏览器失败！请按照以下步骤检查错误：\n" \
                "1. 请检查是否安装了Chrome浏览器（谷歌浏览器）\n" \
                "2. 关闭正在运行的Chrome浏览器后重启本程序。\n" \
                "3. 请不要同时运行多个本程序。\n"
                loguru.logger.exception(tip)
                time.sleep(1e9)
            self._init_website()
            self.page.set.auto_handle_alert(accept=True)
            self.page.set.window.max()
            self.page.console.start()
            self.page.listen.start(self.website.listen_paths)
            threading.Thread(target=self.listen_console, daemon=True).start()
            threading.Thread(target=self.listen_path, daemon=True).start()
            self.website.open_base_url()
        except Exception as e:
            loguru.logger.exception(f"[BrowserInit] 异常: {e}")
            self.close()

    def _after_init_browser(self):
        pass

    def _init_website(self):
        pass

    def listen_path(self):
        """进行请求监听"""
        while True:
            try:
                for response in self.page.listen.steps():
                    if self.website.listen_path_callback:
                        self.website.listen_path_callback(response)
            except Exception as e:
                loguru.logger.exception(f"[listen_path]错误{e}")

    def listen_console(self):
        """进行控制台监听"""
        while True:
            try:
                for response in self.page.console.steps():
                    if self.website.listen_console_callback:
                        self.website.listen_console_callback(response)
            except Exception as e:
                loguru.logger.exception(f"[listen_console] 错误{e}")

    def close(self):
        """关闭浏览器"""
        try:
            self.page.quit()
        except Exception:
            pass