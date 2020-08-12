from celery.schedules import crontab
# �첽�������Celery��Django�е�ʹ������
CELERY_TIMEZONE = 'Asia/Shanghai'
BROKER_URL = 'amqp://yoho:yoho@192.168.102.45:5672/yoho'
RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
# CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
# CELERYBEAT_SCHEDULER = 'amqp://yoho:yoho@192.168.102.45:5672/yoho'

CELERYBEAT_SCHEDULE = {
    'run_case-task': {
        'task': 'mycelery.runcase.tasks.run_search_case',
        # ��ʱ����һ����ÿ5����ִ��һ������(refresh1)
        # 'schedule': crontab(hour='*/5'),
        #��ʱ�����:��ÿ����賿2:00��ִ������(refresh2)
        'schedule': crontab(minute=0, hour=2),
        # ��ʱ������:ÿ���µģ��ŵ�6:00������ִ������(refresh3)
        # 'schedule': crontab(hour=6, minute=0, day_of_month='1'),
        #  pid:��Ŀid, search_key�������ؼ���, select_env������, select_service������, username���û���
        'args': (25, '', '', '', 'meibaocai'),
    }
}
