from celery.schedules import crontab
# 异步任务队列Celery在Django中的使用配置
CELERY_TIMEZONE = 'Asia/Shanghai'
BROKER_URL = 'amqp://yoho:yoho@192.168.102.45:5672/yoho'
RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
# CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
# CELERYBEAT_SCHEDULER = 'amqp://yoho:yoho@192.168.102.45:5672/yoho'

CELERYBEAT_SCHEDULE = {
    'run_case-task': {
        'task': 'mycelery.runcase.tasks.run_search_case',
        # 定时任务一：　每5分钟执行一次任务(refresh1)
        # 'schedule': crontab(hour='*/5'),
        #定时任务二:　每天的凌晨2:00，执行任务(refresh2)
        'schedule': crontab(minute=0, hour=2),
        # 定时任务三:每个月的１号的6:00启动，执行任务(refresh3)
        # 'schedule': crontab(hour=6, minute=0, day_of_month='1'),
        #  pid:项目id, search_key：搜索关键字, select_env：环境, select_service：服务, username：用户名
        'args': (25, '', '', '', 'meibaocai'),
    }
}
