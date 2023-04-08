from celery_task.home_task import add

res = add.apply_async(args=[7, 8])

print(res)

