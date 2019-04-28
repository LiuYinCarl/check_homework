import os
from redis import Redis
from flask import (request, session, jsonify, render_template as rt, send_from_directory, url_for,
                   render_template, Blueprint)

from app.tasks import jaccard, generate_report
from app.utils.auth_func import login_required
from app import attachment_dir, temp_dir

file = Blueprint('file', __name__)


@file.route('/upload_file', methods=['GET'])
def upload_file():
    return rt('upload_file.html')


@file.route('/file/file', methods=['POST'])
def upload_part():  # 接收前端上传的一个分片
    task = request.form.get('task_id')  # 获取文件的唯一标识符
    chunk = request.form.get('chunk', 0)  # 获取该分片在所有分片中的序号
    filename = '%s%s' % (task, chunk)  # 构造该分片的唯一标识符

    upload_file = request.files['file']
    path = '{0}/{1}'.format(temp_dir, filename)
    upload_file.save(path)  # 保存分片到本地
    return rt('upload_file.html')


@file.route('/file/merge', methods=['GET'])
def upload_success():  # 按序读出分片内容，并写入新文件
    email = session.get('email')
    target_filename = request.args.get('filename')  # 获取上传文件的文件名
    task = request.args.get('task_id')  # 获取文件的唯一标识符
    chunk = 0  # 分片序号
    final_path = '{0}/{1}/{2}'.format(attachment_dir, email, target_filename)
    with open(final_path, 'wb') as target_file:  # 创建新文件
        while True:
            try:
                filename = '{0}/{1}{2}'.format(temp_dir, task, chunk)
                with open(filename, 'rb') as source_file:
                    target_file.write(source_file.read())  # 读取分片内容写入新文件
            except Exception:
                break

            chunk += 1
            os.remove(filename)  # 删除该分片，节约空间

    return rt('upload_file.html', email=email)


@file.route('/show_upload_attachments', methods=['GET'])
@login_required
def show_upload_attachments():
    email = session.get('email')
    path = '{0}/{1}'.format(attachment_dir, email)
    files = os.listdir(path)  # 获取文件目录
    return rt('show_attachments.html', attachments=files, email=email)


@file.route('/file/download/<filename>', methods=['GET'])
def file_download(filename):
    email = session.get('email')
    upload_dir = '{0}/{1}'.format(attachment_dir, email)
    return send_from_directory(upload_dir, filename)


@file.route('/duplicate', methods=['GET', 'POST'])
def duplicate():
    email = session.get('email')
    if request.method == 'POST':
        file_dir = '{0}/{1}'.format(attachment_dir, email)
        task = jaccard.apply_async((file_dir, email), serializer='json')
        return jsonify({}), 202, {'Location': url_for('.duplicate_result', task_id=task.id)}
    else:
        return render_template('duplicate.html', email=email)


@file.route('/duplicate_status/<task_id>')
def duplicate_result(task_id):
    result = None
    email = session.get('email')
    task = jaccard.AsyncResult(task_id)
    print(task.state)
    if task.state == 'SUCCESS':
        conn = Redis(host='127.0.0.1', port=6379, db=1)
        email = session.get('email')
        name = email + ':duplicate_result'
        res = conn.hgetall(name)
        result = dict()
        for k, v in res.items():
            new_k = k.decode('utf-8')
            new_v = v.decode('utf-8')
            splited_v = new_v.rsplit(',', 1)
            tmp_v = dict()
            tmp_v['0'] = splited_v[0]
            tmp_v['1'] = splited_v[1]
            result[new_k] = tmp_v
        generate_report.apply_async((email,), serializer='json')  # 这里直接在查重完成后就生成报表
    response = {'state': task.state, 'result': result}
    return jsonify(response)
