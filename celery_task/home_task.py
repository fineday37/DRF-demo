from celery_task.celery_test import app


@app.task
def add(a, b):
    import time
    time.sleep(1)
    return a + b
