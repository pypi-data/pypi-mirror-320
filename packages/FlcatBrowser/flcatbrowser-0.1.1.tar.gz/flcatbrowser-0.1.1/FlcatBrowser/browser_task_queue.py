import random
import threading
import time
from typing import Type
from browser import BaseBrowser
from utils.task_queue import TaskQueue, Worker

class BrowserWorker(Worker):
    def __init__(self, task_queue: "TaskQueue", browser: BaseBrowser, *args, **kwargs):
        super().__init__(task_queue, *args, **kwargs)
        self.browser = browser

class BrowserTaskQueue(TaskQueue):
    def __init__(self, browser_class: Type[BaseBrowser], num_workers: int = 2, max_size: int = 0, proxy_ip = ''):
        self.proxy_ip = proxy_ip
        self.browser_class =browser_class
        super().__init__(num_workers, max_size)

    def _init_workers_concurrence(self, num_workers: int, wait_time:tuple[int, int] = None) -> None:
        threads = []

        def create_worker(index):
            if wait_time:
                # 避免指纹浏览器api调用过快
                time.sleep(random.randint(**wait_time))
            worker = BrowserWorker(
                self, 
                self.browser_class(str(index+1), self.proxy_ip), 
                name=f"Worker-{index+1}"
            )
            worker.start()
            self.workers.append(worker)

        for i in range(num_workers):
            thread = threading.Thread(target=create_worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()  # 等待所有线程完成
