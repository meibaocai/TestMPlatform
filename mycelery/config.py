# �첽�������Celery��Django�е�ʹ������

CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Asia/Shanghai'
BROKER_URL = 'amqp://yoho:yoho@192.168.102.45:5672/yoho'
RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_TASK_RESULT_EXPIRES = 7200  # celery����ִ�н���ĳ�ʱʱ�䣬
CELERYD_CONCURRENCY = 10  # celery worker�Ĳ����� Ҳ��������-cָ������Ŀ ���ݷ���������ʵ�ʸ��� һ��25����
CELERYD_MAX_TASKS_PER_CHILD = 200  # ÿ��workerִ���˶�������ͻ��������ҽ����������Դ�һЩ������200