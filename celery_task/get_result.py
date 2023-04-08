from celery_task.celery_test import app
from celery.result import AsyncResult

pk = '8e50bf0e-e380-4d59-bfe6-95a744b91057'
if __name__ == '__main__':
    res = AsyncResult(id=pk, app=app)
    if res.successful():
        result = res.get()
        print('任务执行成功')
        print(result)  # 15
    elif res.failed():
        print('任务失败')
    elif res.status == 'PENDING':
        print('任务等待中被执行')
    elif res.status == 'RETRY':
        print('任务异常后正在重试')
    elif res.status == 'STARTED':
        print('任务已经开始被执行')
