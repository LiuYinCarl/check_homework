import jieba

from app.helper import EmailSpider, Saver, EmailSender, get_smtp_host
from redis import Redis
from celery import Celery
import docx
import os

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


@celery.task
def jaccard(file_dir, email):
    text_list = save_text(file_dir)
    result = dict()  # key = filename1, value = [filename2, jaccard_score]
    files = os.listdir(file_dir)
    for file in files:  # 初始化
        result[file] = ['', 0]
    for i in text_list:
        for j in text_list:
            if i[0] != j[0]:  # i与j不是同一个文件
                ret1 = i[1].intersection(j[1])
                ret2 = i[1].union(j[1])
                jaccard_score = 1.0 * len(ret1) / len(ret2)
                if result[i[0]][1] < jaccard_score:
                    result[i[0]][0] = j[0]
                    result[i[0]][1] = jaccard_score
                if result[j[0]][1] < jaccard_score:
                    result[j[0]][0] = i[0]
                    result[i[0]][1] = jaccard_score
    conn = Redis(host='127.0.0.1', port=6379, db=1)
    name = email + ':duplicate_result'
    for k, v in result.items():
        tmp = [str(arg) for arg in v]
        value = ','.join(tmp)
        conn.hset(name, k, value)
    # return result


def cut_text(text):
    words = set()
    for word in jieba.lcut_for_search(text):
        words.add(word)
    return words


def save_text(file_dir):
    files = os.listdir(file_dir)
    text_list = []
    for file in files:
        path = '{0}/{1}'.format(file_dir, file)
        text = get_text(path)
        text_set = cut_text(text)
        tmp = [file, text_set]
        print(tmp)
        text_list.append(tmp)
    return text_list


def get_text(path):
    file = docx.Document(path)
    t = [para.text for para in file.paragraphs]
    text = ''.join(t)
    # print(text)
    return text
