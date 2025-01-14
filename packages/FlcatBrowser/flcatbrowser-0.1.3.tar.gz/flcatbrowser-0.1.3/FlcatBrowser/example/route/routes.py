from fastapi import APIRouter
import loguru
from example.browser.browser import Browser
from browser_task_queue import BrowserTaskQueue
from example.browser.cf_test.website import CFTestWebsite
from exception import NotSupportError, RequestParameterError, TaskError
from fastapi import HTTPException, Request
from utils.task_queue import Task, Worker

router = APIRouter(prefix='/v1')

tq = BrowserTaskQueue(Browser, num_workers=int(1), max_size=int(1))

@router.post("/test_cf",
            summary='测试过cf',)
async def test_cf(request: Request):
    """
    测试过cf
    """
    try:
        # 定义任务逻辑
        def my_task(task_obj: Task, worker_obj: Worker, *args, **kwargs):
            loguru.logger.info(f"Running in thread: {worker_obj.name}")
            website: CFTestWebsite = worker_obj.browser.website
            website.test()

        # 提交任务到任务队列
        t = tq.submit(func=my_task, args=[], retry=2)
        result = await t.wait_async()
        return result
    except RequestParameterError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TaskError as e:
        if e.code:
            raise HTTPException(status_code=e.code, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        loguru.logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))