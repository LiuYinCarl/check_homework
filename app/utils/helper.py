from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import poplib
import os
import email
import yagmail
from datetime import datetime
import time

# 可执行文件拓展名
LEGAL_EXTENSION = ['docx', 'doc', 'txt']


def to_timestamp(date_time):
    """将形如2019-4-18日这种格式转换为时间戳（10位）"""
    time_array = time.strptime(date_time, "%Y-%m-%d")
    timestamp = time.mktime(time_array)
    return timestamp


def allowed_file(filename):
    """检查文件名是否合法"""
    return '.' in filename and filename.split('.')[-1] in LEGAL_EXTENSION


def get_smtp_host(email):
    """获取邮箱对应的服务商的SMTP服务器地址"""
    maps = {
        'qq.com': 'smtp.qq.com',
        'gmail.com': 'smtp.gmail.com',
        '126.com': 'smtp.126.com',
        '163.com': 'smtp.163.com',
        'sohu.com': 'smtp.sohu.com',
        'sina.com': 'smtp.sina.com',
        '139.com': 'smtp.139.com',
    }
    tail = email.split('@')[1]
    if tail in maps:
        return maps[tail]


def get_pop3_host(email):
    maps = {
        'qq.com': 'pop.qq.com'
    }
    tail = email.split('@')[1]
    if tail in maps:
        return maps[tail]


def get_now_time():
    """获取当前时间并转换成2018_7_5_12_14这种格式
    :return: 返回特定格式的当前时间
    """
    return time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))


def create_dir(abs_path):
    """创建附件下载文件夹
    :return: None
    """
    if not os.path.exists(abs_path):
        os.mkdir(abs_path)


def delete_file(abs_path):
    """删除文件"""
    os.remove(abs_path)


def split_file_name(filenames):
    """分割附件名，提取出学号/姓名/作业名
    :param filenames: 附件名列表
    :return: （学号,姓名,作业名,）元组
    """
    filename_info = []
    for name in filenames:
        filename_info.append(name.split('-'))
    return filename_info


def get_file_name_list(sender_info):
    """从senfer_info中提取出所有附件名并保存为一个集合
    :param sender_info: 发件人列表
    :return: （学号,姓名,作业名,）元组
    """
    name_list = []
    for sender in sender_info:
        name_list += sender.attachments
    return split_file_name(name_list)


class Saver(object):
    """用户账户信息/下载偏好"""

    def __init__(self, account, password,
                 start=None, end=None, report_name='error'):
        self.account = account  # 账号
        self.password = password  # 密码/授权码
        self.start_date = start  # 接受报告开始时间
        self.end_date = end  # 接收报告终止时间
        self.report_name = report_name  # 报告名称


class Sender(object):
    """发信人对象"""

    def __init__(self):
        self.nickname = None  # 昵称
        self.address = None  # 邮箱
        self.timestamp = None  # 时间戳
        self.attachments = None  # 附件名称列表
        # self.FLAG = 2                # 附件标志


# TODO(bearcarl@qq.com) 对附件名拆分出学号，姓名的时候写的更灵活一些 separators = ['-', '--', '_', '——', ' ']
# TODO(bearcarl@qq.com) 未考虑附件重名的情况
class EmailSpider:
    pop3_server = 'pop.qq.com'
    smtp_server = 'smtp.qq.com'
    save_path = 'Attachments'

    def __init__(self, saver):
        self.saver = saver
        self.sender_info = []  # 发送者集合
        self.attachments = []  # 附件集合
        self.emails = []  # 发件学生邮箱集合
        self.server = poplib.POP3_SSL(EmailSpider.pop3_server)

    def _connect(self):
        try:
            self.server.set_debuglevel(1)  # 调试信息
            self.server.user(self.saver.account)  # 身份信息
            self.server.pass_(self.saver.password)
        except Exception as e:
            print('connect error: ', e.args)

    def _disconnect(self):
        try:
            self.server.quit()
        except Exception as e:
            print('disconnect error: ', e.args)

    def _get_email_num(self):
        """获取邮件数量
        :return: 邮件列表中邮件的数量
        """
        num, size = self.server.stat()
        return num

    @staticmethod
    def _decode_str(s):
        """转换编码
        :param s:
        :return:
        """
        try:
            value, charset = decode_header(s)[0]
            if charset:
                value = value.decode(charset)
            return value
        except Exception as e:
            print('decode string error:', e.args)

    def _download(self, part, filename):
        msg = '_download:{0}'.format(filename)
        print(msg)
        data = part.get_payload(decode=True)
        save_dir = '{0}/{1}'.format(self.save_path, self.saver.account)
        save_path = '{0}/{1}/{2}'.format(self.save_path, self.saver.account, filename)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        with open(save_path, 'wb') as f:
            f.write(data)

    def _download_attachment(self, message, email):
        attachments = []
        for part in message.walk():
            filename = part.get_filename()
            if filename:
                filename = self._decode_str(filename)
                print(filename)
                if allowed_file(filename) and self.saver.report_name in filename:  # 检查文件名是否符合规则
                    self._download(part=part, filename=filename)
                    attachments.append(filename)
                    if email not in self.emails:
                        self.emails.append(email)
        return attachments

    # TODO 更改self.sender_info的数据结构使查找更快
    def _check_update(self, tmp_sender):
        """检查发件人列表
        :param tmp_sender: 当前邮件发件人信息
        """
        for sender in self.sender_info:
            # 如果符合
            if sender.address == tmp_sender.address:
                # 当前邮件时间戳更大
                if sender.timestamp < tmp_sender.timestamp:
                    # 删除原来的文件
                    for filename in sender.attachments:
                        delete_file(self.save_path + '\\' + filename)
                    # 删除原来的发信人
                    self.sender_info.remove(sender)
                    return 'update'
                else:
                    return 'jump_over'
        return 'update'

    def _parse_email(self, index, time_stamp):
        """根据邮件在邮件列表中的编号，解析邮件
        :param index: 邮件在邮件列表中的编号
        :return: None
        """
        # 实例化发信人对象
        tmp_sender = Sender()
        # 存储时间戳
        tmp_sender.timestamp = time_stamp

        byte_lines = self.server.retr(index)[1]
        str_lines = []
        for x in byte_lines:  # 转码
            str_lines.append(x.decode())
        # 拼接邮件内容
        msg_content = '\n'.join(str_lines)
        # 把邮件内容解析成Message对象
        msg = Parser().parsestr(msg_content)
        # 获取发信人昵称/邮箱并保存
        sender_info = self._get_from(msg)
        tmp_sender.nickname = sender_info[0]
        tmp_sender.address = sender_info[1]

        if self._check_update(tmp_sender) == 'update':
            attachments = self._download_attachment(msg, tmp_sender.address)
            # 存储附件名称列表
            tmp_sender.attachments = attachments
            self.sender_info.append(tmp_sender)
            self.attachments += attachments

    @classmethod
    def _get_from(cls, msg):
        """获取发送人昵称/邮箱
        :param msg: Message对象
        :return: (昵称,邮箱)
        """
        value = msg.get('From', '')
        if value:
            name, addr = parseaddr(value)
            name = cls._decode_str(name)
            from_info = (name, addr)
            return from_info

    def _get_time_stamp(self, index):
        """获取邮件的UNIX时间戳
        :param index: 邮件在邮件列表中的编号
        :return: 该邮件的UNIX时间戳
        """
        print('邮件编号：{}'.format(index))
        # 获取邮件内容
        messages = self.server.retr(index)[1]
        # 转码
        mail = email.message_from_bytes('\n'.encode('utf-8').join(messages))
        # 获取邮件发送时间
        date = email.header.decode_header(mail.get('Date'))[0][0]
        # 设置时区
        # tiem_zone = timezone(timedelta(hours=8))
        print('时间：{}'.format(date))
        try:
            beijing_time = datetime.strptime(date[5:31], '%d %b %Y %H:%M:%S %z')
            localtimestamp = beijing_time.timestamp()
            print(localtimestamp)
            return localtimestamp
        except ValueError as e:
            print('time stamp value error:', e.args)

    def find_emails(self):
        """二分法查找时间间隔内的邮件
        开始时的左右边界分别是邮件列表中的第一封邮件和最后一封邮件
        :return: None
        """
        # 先找到一个在正确时间内的邮件，再从左向右遍历即可
        email_count = self._get_email_num()
        left = 1
        right = email_count
        left_time_stamp = self._get_time_stamp(left)
        right_time_stamp = self._get_time_stamp(right)
        print(self.saver.start_date)
        if left_time_stamp > self.saver.start_date:
            self._right_traveler(left, right)
        elif right_time_stamp < self.saver.end_date:
            self._left_traveler(left, right)
        else:
            while left < right:
                mid_index = (right + left) // 2
                mid_time_stamp = self._get_time_stamp(mid_index)
                if (self.saver.start_date <= mid_time_stamp) and (self.saver.end_date >= mid_time_stamp):
                    self._left_traveler(left, mid_index)
                    self._right_traveler(mid_index, right)
                    break
                elif self.saver.start_date <= mid_time_stamp:
                    right = mid_index - 1
                else:
                    left = mid_index + 1

    def _left_traveler(self, left, right):
        """从right向左遍历邮件列表， 直到left
        :param left: 遍历范围内最左侧（时间最早）的邮件编号
        :param right: 遍历范围内最右侧（时间最晚）的邮件编号
        :return: None
        """
        left = left
        right = right
        for i in range(right, left - 1, -1):
            i_time_stamp = self._get_time_stamp(i)
            if (self.saver.start_date < i_time_stamp) and (self.saver.end_date > i_time_stamp):
                # 解析邮件
                self._parse_email(i, i_time_stamp)
            else:
                break

    def _right_traveler(self, left, right):
        """从left向右遍历， 直到right
        :param left: 遍历范围内最左侧（时间最早）的邮件编号
        :param right: 遍历范围内最右侧（时间最晚）的邮件编号
        :return: None
        """
        left = left
        right = right
        for i in range(left, right + 1):
            i_time_stamp = self._get_time_stamp(i)
            print('start_data', self.saver.start_date)
            print('i_time', i_time_stamp)
            if (self.saver.start_date < i_time_stamp) and (self.saver.end_date > i_time_stamp):
                # 解析邮件
                self._parse_email(i, i_time_stamp)
            else:
                break

    def run(self):
        """主控方法，控制服务器的连接/断开/邮件遍历等
        :return: 发送人邮件列表/附件名列表
        """
        self._connect()
        create_dir(self.save_path)
        self.find_emails()
        self._disconnect()
        print('self.attach', self.attachments)
        return self.attachments, self.emails


class EmailSender(object):
    def __init__(self):
        self.server = None

    def conn_server(self, account, password, host):
        try:
            self.server = yagmail.SMTP(user=account,
                                       password=password,
                                       host=host,
                                       smtp_ssl=True)
        except Exception as e:
            print('EmailSender connect server error:', e.args)

    def send_email(self, receiver_list, subject, contents, attachment_list=[]):
        if len(receiver_list) <= 0:
            print('发送列表为空')
            return
        try:
            self.server.send(to=receiver_list,
                             subject=subject,
                             contents=contents,
                             attachments=attachment_list)
        except Exception as e:
            print('EmailSender send email error:', e.args)



