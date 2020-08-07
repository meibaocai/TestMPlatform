import os
from celery import Celery
from celery.schedules import crontab


# ����Ĭ�ϵ�django settingsģ�����ø�celery
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestMPlatform.settings.settings')

    # ����һ��Celeryʵ������
app = Celery('TestMPlatform')
# ͨ��app�����������
app.config_from_object('mycelery.config')

# ��������
#���������Ǹ��б������ÿһ�������������·������
app.autodiscover_tasks(["mycelery.runapicase",])
# ����celery������
#ǿ��������mycelery��Ŀ¼������
# celery -A mycelery.main worker --loglevel=info
# �첽�������Celery��Django�е�ʹ������


BROKER_URL = 'amqp://yoho:yoho@192.168.102.45:5672/yoho'
RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERYBEAT_SCHEDULER = 'amqp://yoho:yoho@192.168.102.45:5672/yoho'
if __name__ == '__main__':
    app.start()
