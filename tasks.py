from app.helper import EmailSpider, Saver, EmailSender, get_smtp_host
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
    attachments, sender_emails = spider.run()
    print('附件列表：', attachments)
    print('emails:', sender_emails)
    save_attachments_and_emails(attachments, sender_emails, email)


# todo 查阅redis连接是否需要释放问题
def save_attachments_and_emails(attachments, send_emails, email):
    conn = Redis(host='127.0.0.1', port=6379, db=1)
    key = email + ':attachments'
    key2 = email + ':sender_emails'
    # 先清空再添加
    conn.delete(key)
    for attach in attachments:
        conn.rpush(key, attach)

    conn.delete(key2)
    for send_email in send_emails:
        conn.rpush(key2, send_email)


@celery.task
def send_receipt(email, email_password, receive_list, subject, content):
    host = get_smtp_host(email)
    outbox = EmailSender()
    outbox.conn_server(email, email_password, host)
    outbox.send_email(receive_list, subject, content)
