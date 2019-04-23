from . import upload

import os

from flask import request, Response, render_template as rt


@upload.route('/upload_file', methods=['GET'])
def upload_file():
    return rt('upload_file.html')


@upload.route('/file/upload', methods=['POST'])
def upload_part():  # 接收前端上传的一个分片
    task = request.form.get('task_id')  # 获取文件的唯一标识符
    chunk = request.form.get('chunk', 0)  # 获取该分片在所有分片中的序号
    filename = '%s%s' % (task, chunk)  # 构造该分片的唯一标识符

    upload_file = request.files['file']
    base_path = os.path.dirname(__file__)
    path = '{0}/../tmp/{1}'.format(base_path, filename)
    upload_file.save(path)  # 保存分片到本地
    return rt('upload_file.html')


@upload.route('/file/merge', methods=['GET'])
def upload_success():  # 按序读出分片内容，并写入新文件
    target_filename = request.args.get('filename')  # 获取上传文件的文件名
    task = request.args.get('task_id')  # 获取文件的唯一标识符
    chunk = 0  # 分片序号
    base_path = os.path.dirname(__file__)
    final_path = '{0}/../Attachments/{1}'.format(base_path, target_filename)
    with open(final_path, 'wb') as target_file:  # 创建新文件
        while True:
            filename = '{0}/../tmp/{1}{2}'.format(base_path, task, chunk)
            try:
                source_file = open(filename, 'rb')  # 按序打开每个分片
                target_file.write(source_file.read())  # 读取分片内容写入新文件
                source_file.close()
            # except IOError, msg:
            #     break
            except Exception:
                break

            chunk += 1
            os.remove(filename)  # 删除该分片，节约空间

    return rt('upload_file.html')


@upload.route('/file/list', methods=['GET'])
def file_list():
    files = os.listdir('./upload/')  # 获取文件目录
    files = map(lambda x: x if isinstance(x, unicode) else x.decode('utf-8'), files)  # 注意编码
    return rt('./list.html', files=files)


@upload.route('/file/download/<filename>', methods=['GET'])
def file_download(filename):
    def send_chunk():  # 流式读取
        store_path = './upload/%s' % filename
        with open(store_path, 'rb') as target_file:
            while True:
                chunk = target_file.read(20 * 1024 * 1024)
                if not chunk:
                    break
                yield chunk

    return Response(send_chunk(), content_type='application/octet-stream')
