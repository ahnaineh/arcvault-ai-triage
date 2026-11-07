import os
import secrets
import sys
import threading
import time

sys.path.insert(0,os.getcwd())
os.environ.update(DJANGO_SETTINGS_MODULE='config.settings',DJANGO_SECRET_KEY=secrets.token_hex(32),DATABASE_URL='sqlite:////tmp/arcaccept.sqlite',DJANGO_DEBUG='true')
import django

django.setup()
from django.conf import settings

settings.STORAGES={'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}}
from django.core.management import call_command

call_command('migrate',verbosity=0)
from django.contrib.auth import get_user_model

password=secrets.token_urlsafe(24)
u,_=get_user_model().objects.get_or_create(username='synthetic-reviewer');u.set_password(password);u.save()
from types import SimpleNamespace
from unittest.mock import patch

from django.db import connections

from apps.triage.tasks import process
from tests.test_backend import analysis


def dispatch(pk,countdown=0):
 def work():
  time.sleep(2)
  with patch('apps.triage.tasks.get_provider') as provider:
   provider.return_value.analyze.return_value=SimpleNamespace(analysis=analysis(),model='mock',prompt_version='v1',schema_version='v1',latency_ms=1,usage=None)
   process(str(pk))
  connections.close_all()
 threading.Thread(target=work,daemon=True).start()
import apps.intake.service

apps.intake.service.dispatch=dispatch
threading.Thread(target=lambda:call_command('runserver','127.0.0.1:18766',use_reloader=False,verbosity=0),daemon=True).start()
time.sleep(1)
from pathlib import Path

from playwright.sync_api import sync_playwright

out=Path('docs/evidence/pr6-browser');out.mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
 page=b.new_page()
 page.goto('http://127.0.0.1:18766/tester/')
 page.locator('[name=username]').fill('synthetic-reviewer');page.locator('[name=password]').fill(password);page.locator('button').click()
 page.goto('http://127.0.0.1:18766/tester/')
 posts=[]
 def intercept(route):
  posts.append(route.request.post_data_json)
  response=route.fetch()
  if len(posts)==1:
   assert response.status==202
   route.abort()
  else: route.fulfill(response=response)
 page.route('**/api/v1/requests/',intercept)
 page.locator('#message').fill('usage?');page.locator('#submit').click()
 page.wait_for_function("!document.querySelector('#resume').hidden")
 page.locator('#resume').click()
 page.wait_for_function("document.querySelector('#progress').textContent.includes('completed')")
 assert len(posts)==2 and posts[0]==posts[1]
 from apps.triage.models import Request
 assert Request.objects.filter(idempotency_key=posts[0]['idempotency_key']).count()==1
 page.locator('#detail').click();page.go_back()
 print('Back navigation type:',page.evaluate("performance.getEntriesByType('navigation')[0].type"))
 print('PASS Chrome accepted response abort, two identical POSTs, one DB row, completion and Back')
 b.close()
