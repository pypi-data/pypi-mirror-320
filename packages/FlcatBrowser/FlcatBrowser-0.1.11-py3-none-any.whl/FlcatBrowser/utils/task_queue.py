import asyncio
import queue
import random
import threading
import time
from typing import Any, Callable, Optional

import loguru

class QueueFullError(Exception):
    """队列已满异常

    当任务队列达到最大容量，无法接受更多任务时抛出此异常。

    :param message: 异常的消息字符串。
    :param max_size: 队列的最大容量。
    """
    def __init__(self, message: str = "任务队列已满，无法提交新任务。", max_size: int | None = None) -> None:
        """
        初始化 QueueFullError 异常。

        :param message: 异常的消息内容，默认提示队列已满。
        :param max_size: 可选的队列最大容量。
        """
        self.message: str = message
        self.max_size: int | None = max_size
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        返回异常的字符串表示形式。

        :return: 格式化的队列已满异常信息字符串。
        """
        if self.max_size is not None:
            return f"{self.message} 队列最大容量为: {self.max_size}."
        return self.message

class Task:
    """
    表示一个需要执行的任务
    """
    def __init__(
        self,
        func: Callable[..., Any],
        args: tuple = (),
        kwargs: dict = None,
        retry: int = 3,
        timeout: float = 5.0,
    ):
        """
        :param func: 任务函数
        :param args: 函数位置参数
        :param kwargs: 函数关键字参数
        :param retry: 最大重试次数
        :param timeout: 超时时间（秒）
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs if kwargs is not None else {}
        self.retry = retry
        self.timeout = timeout

        # 任务执行结果以及状态
        self.result = None
        self.exception = None
        self.finished = threading.Event()

    def run(self, worker: "Worker" = None) -> None:
        """
        执行任务，并支持超时/异常处理。
        新增 worker 参数，用于在任务函数中访问当前执行该任务的 Worker。
        """
        try:
            start_time = time.time()

            while True:
                elapsed = time.time() - start_time
                if elapsed >= self.timeout:
                    raise TimeoutError(f"Task exceeded timeout: {self.timeout}s")

                # 调用用户自定义的任务函数时，将 self（Task对象）和 worker 都传入
                self.result = self.func(self, worker, *self.args, **self.kwargs)
                break

        except Exception as e:
            self.exception = e

        finally:
            # 无论成功或失败，都触发事件表示执行结束
            self.finished.set()

    def wait(self, timeout: Optional[float] = None) -> Any:
        """
        等待任务执行结束，可指定等待时间。
        如果没有超时，返回执行结果或者抛出异常。
        """
        finished_in_time = self.finished.wait(timeout=timeout)
        if not finished_in_time:
            raise TimeoutError("Wait for task result timed out")

        # 如果任务执行抛出异常，这里可以再次向上层抛出
        if self.exception is not None:
            raise self.exception
        return self.result

    async def wait_async(self, timeout: Optional[float] = None) -> Any:
        """
        等待任务执行结束，非阻塞方式，支持 asyncio。
        如果没有超时，返回执行结果或者抛出异常。
        """
        try:
            loop = asyncio.get_event_loop()
            # 将线程的 Event 转换为 asyncio 的 Future
            await asyncio.wait_for(loop.run_in_executor(None, self.finished.wait), timeout=timeout)

            # 如果任务执行抛出异常，这里可以再次向上层抛出
            if self.exception is not None:
                raise self.exception
            return self.result
        except asyncio.TimeoutError:
            raise TimeoutError("Wait for task result timed out")

class Worker(threading.Thread):
    """
    工作线程，不断从队列中取出任务执行
    """
    def __init__(self, task_queue: "TaskQueue", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_queue = task_queue
        self.daemon = True

    def run(self) -> None:
        while True:
            try:
                task = self.task_queue.queue.get(block=True)
                if task is None:
                    # 收到关闭信号，跳出循环结束线程
                    self.task_queue.queue.task_done()
                    break

                retries_left = task.retry
                while retries_left > 0:
                    task.run(worker=self)  # 在这里传递 worker 本身
                    if task.exception is None:
                        # 执行成功
                        break
                    else:
                        # 执行失败，重试次数减一
                        retries_left -= 1
                        if retries_left > 0:
                            loguru.logger.error(f"[Worker-{self.name}] Task failed, retrying... {retries_left} retries left.")
                
                self.task_queue.queue.task_done()
                
                # 如果重试用完依然失败，可根据需要做额外处理
                if task.exception is not None:
                    loguru.logger.error(f"[Worker-{self.name}] Task completely failed after all retries:")
                    loguru.logger.exception(task.exception)

            except Exception as e:
                loguru.logger.exception(f"[Worker-{self.name}] Unexpected error:", e)


class TaskQueue:
    """
    任务队列，用于提交和管理任务
    """
    def __init__(self, num_workers: int = 2, max_size: int = 0):
        self.queue = queue.Queue(maxsize=max_size)
        self.workers = []
        self._init_workers_concurrence(num_workers)

    def _init_workers(self, num_workers: int) -> None:
        for i in range(num_workers):
            worker = Worker(self, name=f"Worker-{i+1}")
            worker.start()
            self.workers.append(worker)
            
    def _init_workers_concurrence(self, num_workers: int, wait_time: tuple[int, int] = None) -> None:
        threads = []

        def create_worker(index):
            if wait_time:
                # 可选的每个线程从开始等待多久进行创建，避免在同一时刻开始创建
                time.sleep(random.randint(**wait_time))
            worker = Worker(self, name=f"Worker-{i+1}")
            worker.start()
            self.workers.append(worker)

        for i in range(num_workers):
            thread = threading.Thread(target=create_worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()  # 等待所有线程完成

    def submit(
        self,
        func: Callable[..., Any],
        args: tuple = (),
        kwargs: dict = None,
        retry: int = 3,
        timeout: float = 5.0,
    ) -> Task:
        """
        向任务队列提交一个任务，并返回封装的 Task 对象
        """
        task = Task(func, args, kwargs, retry, timeout)
        try:
            # 非阻塞模式 put，如果队列满了会抛出 queue.Full
            self.queue.put(task, block=False)
            return task
        except queue.Full:
            raise QueueFullError("[TaskQueue] 队列已满，无法提交新任务。",self.queue.maxsize)

    def shutdown(self, wait: bool = True):
        """
        关闭线程池，发送结束信号
        :param wait: 是否等待所有任务完成后再返回
        """
        # 向队列中放入 N 个 None，让所有 Worker 线程停止
        for _ in self.workers:
            self.queue.put(None)

        if wait:
            self.queue.join()

        for w in self.workers:
            w.join()


# ========== 测试示例 ==========
if __name__ == "__main__":

    def my_task(task_obj, worker_obj, x, y):
        """
        任务函数示例：
        - task_obj: 当前任务的 Task 实例
        - worker_obj: 正在执行该任务的 Worker 实例
        - x, y: 具体业务参数
        """
        print(f"[{worker_obj.name}] Executing my_task with x={x}, y={y}")
        time.sleep(1)
        return x + y

    def error_task(task_obj, worker_obj):
        """
        用于测试错误与重试的任务函数
        """
        print(f"[{worker_obj.name}] Executing error_task (will raise error)")
        time.sleep(1)
        raise ValueError("Intentional Error")

    # 创建任务队列
    tq = TaskQueue(num_workers=2)

    # 提交几个成功任务
    tasks = []
    for i in range(3):
        t = tq.submit(func=my_task, args=(i, i + 1), retry=2, timeout=3)
        tasks.append(t)

    # 提交一个一定会报错的任务
    error_t = tq.submit(func=error_task, retry=2, timeout=2)

    # 等待并获取结果
    for i, task in enumerate(tasks):
        try:
            result = task.wait()
            print(f"[Main] Task {i} result: {result}")
        except Exception as e:
            print(f"[Main] Task {i} failed: {e}")

    # 等待并获取报错任务的结果
    try:
        error_t.wait()
    except Exception as e:
        print(f"[Main] Error task failed as expected: {e}")

    # 优雅关闭队列
    tq.shutdown(wait=True)
    print("[Main] All tasks done, queue shut down.")