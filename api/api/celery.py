from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.signals import worker_ready
from celery import chain
from celery.signals import worker_ready

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')


app = Celery('api')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related config keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@worker_ready.connect
def worker_ready_handler(sender, **kwargs):
    # Trigger the tasks in sequence, waiting for the first to finish before starting the second.
    from loan.tasks import ingest_loan_data
    from customer.tasks import ingest_customer_data

    # Chain the tasks together
    task_chain = chain(
        ingest_customer_data.s(),  # First task
        ingest_loan_data.s()      # Second task, will execute after the first completes
    )

    # Execute the chain of tasks
    task_chain()
