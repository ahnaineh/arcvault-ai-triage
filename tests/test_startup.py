import os
import subprocess
import sys


def test_wsgi_celery_new_process():
    subprocess.run([sys.executable, '-c', '''
import config.wsgi
from config.celery import app
from apps.triage.tasks import process
assert process.app is app
assert process.app.conf.broker_url == 'redis://localhost:6379/14'
assert process.app.connection_for_write().transport.driver_type == 'redis'
'''], env={**os.environ, 'REDIS_URL': 'redis://localhost:6379/14'}, check=True)


def test_raw_database_credentials_new_process():
    env = {**os.environ, 'POSTGRES_PASSWORD': 'test#/?password', 'DATABASE_URL': ''}
    subprocess.run([sys.executable, '-c', '''
from config.settings import DATABASES
assert DATABASES['default']['PASSWORD'] == 'test#/?password'
assert DATABASES['default']['HOST'] == 'db'
'''], env=env, check=True)
