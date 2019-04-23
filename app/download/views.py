from . import download
from flask import session, render_template, jsonify, request, url_for
from app.auth.auth_func import login_required
from app.helper import to_timestamp
from tasks import download_email
from redis import Redis


@download.route('/save_emails', methods=['GET', 'POST'])
@login_required
def save_emails():
    email = session.get('email')
    return render_template('save_emails.html', email=email)


# todo email_password在网络上传送的安全问题
@download.route('/email_status', methods=['GET', 'POST'])
def email_status():
    if request.method == 'POST':
        email = session.get('email')
        email_password = request.form['email_password']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        report_name = request.form['report_name']
        # receipt_ctx = request.form['receipt_ctx']
        # send_receipt = request.form.getlist('send_receipt')
        # 将时间转换为时间戳
        start_time = to_timestamp(start_time)
        end_time = to_timestamp(end_time)

        info = (email, email_password, start_time, end_time, report_name)
        task = download_email.apply_async(info, serializer='json')
        return jsonify({}), 202, {'Location': url_for('.save_emails_status', task_id=task.id)}
    else:
        pass


@download.route('/save_emails_status/<task_id>')
def save_emails_status(task_id):
    task = download_email.AsyncResult(task_id)
    response = {'state': task.state}
    return jsonify(response)


@download.route('/show_attachments', methods=['GET'])
@login_required
def show_attachments():
    email = session.get('email')

    conn = Redis(host='127.0.0.1', port=6379, db=1)
    key = email + ':attachments'
    attachments = conn.lrange(key, 0, -1)
    res = []
    for attach in attachments:
        print(type(attach))
        res.append(attach.decode('utf-8'))
    return render_template('show_attachments.html', attachments=res, email=email)
