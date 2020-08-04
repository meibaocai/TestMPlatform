import os
from celery import Celery

# ����һ��Celeryʵ������
app = Celery('TestMPlatform')

# ����Ĭ�ϵ�django settingsģ�����ø�celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestMPlatform.settings')

# ͨ��app�����������
app.config_from_object('mycelery.config')

# ��������
#���������Ǹ��б������ÿһ�������������·������
app.autodiscover_tasks(["mycelery.runapicase",])

# ����celery������
#ǿ��������mycelery��Ŀ¼������
# celery -A mycelery.main worker --loglevel=info

if __name__ ==  '__main__':
    app.start()
