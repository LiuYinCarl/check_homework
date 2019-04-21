from app.helper import EmailSpider, Saver
from redis import Redis
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/1')


# Celery tasks
# http://www.pythondoc.com/flask-celery/first.html
# todo 检测单用户多账号同时操作，并提供防混乱机制
@celery.task
def download_email(email, email_password, start_time, end_time, report_name):
    saver = Saver(email, email_password, start_time, end_time, report_name)
    spider = EmailSpider(saver)
    attachments = spider.run()
    save_attachments(attachments, email)


# todo 查阅redis连接是否需要释放问题
def save_attachments(attachments, email):
    conn = Redis(host='127.0.0.1', port=6379, db=1)
    key = email + ':attachments'
    # 先清空再添加
    conn.delete(key)
    for attach in attachments:
        conn.rpush(key, attach)
