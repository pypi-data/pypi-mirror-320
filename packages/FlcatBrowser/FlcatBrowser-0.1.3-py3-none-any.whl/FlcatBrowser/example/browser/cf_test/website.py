import json
from example.browser import browser
from example.browser.website import Website
from utils.id import generate_unique_id
class CFTestWebsite(Website):
    def __init__(self, browser: "browser.Browser"):
        self.browser: "browser.Browser"
        super().__init__(
            browser,
            'https://cf_test.flcat-test.top/'
            )

    def test(self, task_id = generate_unique_id()):
        
        res = self.process_request("cf_test", 'js_example/requests.js', task_id)
        print(res)
    