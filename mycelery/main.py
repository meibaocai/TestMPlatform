import os
from celery import Celery
from celery.schedules import crontab


# 把置默认的django settings模块配置给celery
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestMPlatform.settings.settings')

    # 创建一个Celery实例对象
app = Celery('TestMPlatform')
# 通过app对象加载配置
app.config_from_object('mycelery.config')

# 加载任务
#参数必须是个列表，里面的每一个任务都是任务的路径名称
app.autodiscover_tasks(["mycelery.runapicase",])
# 启动celery的命令
#强力建议再mycelery根目录下启动
# celery -A mycelery.main worker --loglevel=info
# 异步任务队列Celery在Django中的使用配置


BROKER_URL = 'amqp://yoho:yoho@192.168.102.45:5672/yoho'
RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERYBEAT_SCHEDULER = 'amqp://yoho:yoho@192.168.102.45:5672/yoho'
if __name__ == '__main__':
    app.start()
