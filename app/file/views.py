from . import file
from app.auth.auth_func import login_required
import os
from flask import request, session, Response, render_template as rt, send_from_directory


@file.route('/upload_file', methods=['GET'])
def upload_file():
    return rt('upload_file.html')


@file.route('/file/file', methods=['POST'])
def upload_part():  # 接收前端上传的一个分片
    task = request.form.get('task_id')  # 获取文件的唯一标识符
    chunk = request.form.get('chunk', 0)  # 获取该分片在所有分片中的序号
    filename = '%s%s' % (task, chunk)  # 构造该分片的唯一标识符

    upload_file = request.files['file']
    base_path = os.path.dirname(__file__)
    path = '{0}/tmp/{1}'.format(base_path, filename)
    upload_file.save(path)  # 保存分片到本地
    return rt('upload_file.html')


@file.route('/file/merge', methods=['GET'])
def upload_success():  # 按序读出分片内容，并写入新文件
    email = session.get('email')
    target_filename = request.args.get('filename')  # 获取上传文件的文件名
    task = request.args.get('task_id')  # 获取文件的唯一标识符
    chunk = 0  # 分片序号
    base_path = os.path.dirname(__file__)
    final_path = '{0}/../../Attachments/{1}/{2}'.format(base_path, email, target_filename)
    with open(final_path, 'wb') as target_file:  # 创建新文件
        while True:
            try:
                filename = '{0}/tmp/{1}{2}'.format(base_path, task, chunk)
                with open(filename, 'rb') as source_file:
                    target_file.write(source_file.read())  # 读取分片内容写入新文件
            except Exception:
                break

            chunk += 1
            os.remove(filename)  # 删除该分片，节约空间

    return rt('upload_file.html')


@file.route('/show_upload_attachments', methods=['GET'])
@login_required
def show_upload_attachments():
    email = session.get('email')
    base_path = os.path.dirname(__file__)
    path = '{0}/../../Attachments/{1}'.format(base_path, email)
    files = os.listdir(path)  # 获取文件目录
    return rt('show_attachments.html', attachments=files, email=email)


@file.route('/file/download/<filename>', methods=['GET'])
def file_download(filename):
    base_path = os.path.dirname(__file__)
    email = session.get('email')
    UPLOAD_FOLDER = '{0}/../../Attachments/{1}'.format(base_path, email)
    return send_from_directory(UPLOAD_FOLDER, filename)
