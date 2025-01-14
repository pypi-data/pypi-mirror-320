from example.browser.cf_test.website import CFTestWebsite
from browser import BaseBrowser
class Browser(BaseBrowser):
    """
    Browser类负责业务逻辑与页面操作。
    """

    def __init__(self, browser_id, proxy_ip = ""):
        super().__init__(browser_id, "browser_data", proxy_ip)

    def _init_website(self):
        self.website = CFTestWebsite(self)