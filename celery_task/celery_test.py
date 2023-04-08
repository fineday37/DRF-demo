from datetime import timedelta

from celery import Celery
import redis
from celery.schedules import crontab

broker = 'redis://47.92.76.123:6379/3'
backend = 'redis://47.92.76.123:6379/4'

app = Celery("test", broker=broker, backend=backend, include=[
    'celery_task.home_task'
])
app.conf.timezone = 'Asia/Shanghai'  # 调整时间为本地
app.conf.enable_utc = False  # 不使用UTC时间
app.conf.beat_schedule = {
    'send_sms_task': {
        'task': 'celery_task.home_task.add',
        # 'schedule': timedelta(seconds=20),
        'schedule': crontab(minute=10, hour=11, day_of_month=29, month_of_year=3),  # 每年4月11号，8点42分执行
        'args': (233, 233),
    }
}
print(app)
