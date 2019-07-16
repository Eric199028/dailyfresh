from django.core.mail import send_mail
from celery import Celery
from django.conf import settings
import time
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()

app = Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/8')
Celery()

@app.task
def send_active_email(to_email,username,token):
	subject = '欢迎信息'
	message = ''
	sender = settings.EMAIL_FROM
	receiver = [to_email]
	html_message = '邮件正文<h1>%s 欢迎你请激活 </h1><br/><a>http://10.2.1.198:8001/user/active/%s</a>' % (username, token)

	send_mail(subject, message, sender, receiver, html_message=html_message)
	time.sleep(10)