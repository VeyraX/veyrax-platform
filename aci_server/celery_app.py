from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "aci_server",
    include=['flow.tasks', 'vector_tools.tasks']
)

celery_app.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery_app.conf.result_backend = os.environ.get("CELERY_BROKER_URL")
celery_app.conf.broker_connection_retry_on_startup = True

celery_app.conf.task_acks_late = True
celery_app.conf.task_max_retries = 3
celery_app.conf.worker_prefetch_multiplier = 2

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# No need for autodiscover_tasks when explicitly including task modules
# celery_app.autodiscover_tasks(packages=['flow', 'vector_tools'])