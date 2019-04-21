from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import poplib
import os
import email
import xlwt
import yagmail
from datetime import datetime
import time


def to_timestamp(date_time):
    # 转换成时间数组
    time_array = time.strptime(date_time, "%Y-%m-%d")
    # 转换成时间戳
    timestamp = time.mktime(time_array)
    return timestamp


# 可执行文件拓展名
LEGAL_EXTENSION = ['.docx', '.doc', '.txt']


# 参考
# https://blog.csdn.net/ghostresur/article/details/81875574
# https://blog.csdn.net/tcl415829566/article/details/78481932
# https://www.cnblogs.com/fnng/p/7967213.html
# https://www.cnblogs.com/bendouyao/p/9077689.html

# 细节
# 邮箱列表中的第一个邮件的编号是1


def get_now_time():
    """获取当前时间并转换成2018_7_5_12_14这种格式
    :return: 返回特定格式的当前时间
    """
    now_time = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
    return now_time


def create_dir(save_path):
    """创建附件下载文件夹
    :return: None
    """
    path_exist = os.path.exists(save_path)
    # 如果文件夹不存在
    if not path_exist:
        os.mkdir(save_path)
    else:
        pass


def delete_file(file_path):
    """删除文件
    :param file_path: 文件路径
    :return: None
    """
    os.remove(file_path)


def split_file_name(filenames):
    """分割附件名，提取出学号/姓名/作业名
    :param filenames: 附件名列表
    :return: （学号,姓名,作业名,）元组
    """
    filename_info = []

    for name in filenames:
        info = name.split('-')
        filename_info.append(info)
    return filename_info


def get_file_name_list(sender_info):
    """
    从senfer_info中提取出所有附件名并保存为一个集合
    :param sender_info: 发件人列表
    :return: （学号,姓名,作业名,）元组
    """
    name_list = []
    for sender in sender_info:
        name_list += sender.attachments
    return split_file_name(name_list)


class Saver(object):
    """
    用户账户信息/下载偏好
    """

    def __init__(self, account, password,
                 start=None, end=None, report_name='error'):
        # 账号
        self.account = account
        # 密码/授权码
        self.password = password
        # 接受报告开始时间
        self.start_date = start
        # 接收报告终止时间
        self.end_date = end
        # 报告名称
        self.report_name = report_name


class Sender(object):
    """
    发信人对象
    """

    def __init__(self):
        # 昵称
        self.nickname = None
        # 邮箱
        self.address = None
        # 时间戳
        self.timestamp = None
        # 附件名称列表
        self.attachments = None
        # 附件标志
        self.FLAG = 2


# TODO 对附件名拆分出学号，姓名的时候写的更灵活一些 separators = ['-', '--', '_', '——', ' ']
# TODO 对学生学号进行排序
# TODO 未考虑附件重名的情况

class EmailSpider:
    pop3_server = 'pop.qq.com'
    smtp_server = 'smtp.qq.com'
    server = poplib.POP3_SSL(pop3_server)
    save_path = 'Attachments'

    def __init__(self, saver):
        self.saver = saver
        # 发送者集合
        self.sender_info = []

    def _connect(self):
        try:
            # 调试信息
            EmailSpider.server.set_debuglevel(1)
            # 身份信息
            EmailSpider.server.user(self.saver.account)
            EmailSpider.server.pass_(self.saver.password)
        except Exception as e:
            print('connect error: ', e.args)

    @classmethod
    def _disconnect(cls):
        try:
            cls.server.quit()
        except Exception as e:
            print('disconnect error: ', e.args)

    @classmethod
    def _get_email_num(cls):
        """获取邮件数量
        :return: 邮件列表中邮件的数量
        """
        num, size = cls.server.stat()
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

    @classmethod
    def _download(cls, part, filename):
        data = part.get_payload(decode=True)
        with open(cls.save_path + '\\' + filename, 'wb') as f:
            f.write(data)

    def _download_attachment(self, message):
        attachments = []
        for part in message.walk():
            filename = part.get_filename()
            if filename:
                filename = self._decode_str(filename)
                print('附件 ', filename)
                extension_name = os.path.splitext(filename)[1]
                print('拓展名 ', extension_name)
                print(self.saver.report_name)
                if extension_name in LEGAL_EXTENSION and self.saver.report_name in filename:
                    print('可以下载==========')
                    self._download(part=part, filename=filename)
                    attachments.append(filename)
        return attachments

    # TODO 更改self.sender_info的数据结构使查找更快
    def _check_update(self, tmp_sender):
        """
        检查发件人列表
        返回参数：
        1: 发件人列表中无此人或者有此人但由于时间戳比当前时间戳小，所以已删除
        2: 发件人列表中有此人且时间戳大于当前时间戳
        :param tmp_sender: 当前邮件发件人信息
        :return: 1/2
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
        # 转码
        str_lines = []
        for x in byte_lines:
            str_lines.append(x.decode())
        # 拼接邮件内容
        msg_content = '\n'.join(str_lines)
        # 把邮件内容解析成Message对象
        msg = Parser().parsestr(msg_content)
        # 获取发信人昵称/邮箱并保存
        sender_info = self._get_from(msg)
        tmp_sender.nickname = sender_info[0]
        tmp_sender.address = sender_info[1]

        attachments = None
        if self._check_update(tmp_sender) == 'update':
            attachments = self._download_attachment(msg)
            # 存储附件名称列表
            tmp_sender.attachments = attachments
            self.sender_info.append(tmp_sender)
        return attachments

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
            # print(name, addr)
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
        """
        二分法查找时间间隔内的邮件
        开始时的左右边界分别是邮件列表中的第一封邮件和最后一封邮件
        :return: None
        """
        # 先找到一个在正确时间内的邮件，再从左向右遍历即可
        email_count = self._get_email_num()
        left = 1
        right = email_count
        attachments = []
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
                    attachments += self._left_traveler(left, mid_index)
                    attachments += self._right_traveler(mid_index, right)
                    break
                elif self.saver.start_date <= mid_time_stamp:
                    right = mid_index - 1
                else:
                    left = mid_index + 1
        return attachments

    def _left_traveler(self, left, right):
        """
        从right向左遍历邮件列表， 直到left
        :param left: 遍历范围内最左侧（时间最早）的邮件编号
        :param right: 遍历范围内最右侧（时间最晚）的邮件编号
        :return: None
        """
        left = left
        right = right
        attachments = []  # 附件列表
        for i in range(right, left - 1, -1):
            i_time_stamp = self._get_time_stamp(i)
            if (self.saver.start_date < i_time_stamp) and (self.saver.end_date > i_time_stamp):
                # 解析邮件
                attach = self._parse_email(i, i_time_stamp)
                attachments.append(attach)
            else:
                break
        return attachments

    def _right_traveler(self, left, right):
        """
        从left向右遍历， 直到right
        :param left: 遍历范围内最左侧（时间最早）的邮件编号
        :param right: 遍历范围内最右侧（时间最晚）的邮件编号
        :return: None
        """
        left = left
        right = right
        attachments = []
        for i in range(left, right + 1):
            i_time_stamp = self._get_time_stamp(i)
            print('start_data', self.saver.start_date)
            print('i_time', i_time_stamp)
            if (self.saver.start_date < i_time_stamp) and (self.saver.end_date > i_time_stamp):
                # 解析邮件
                attach = self._parse_email(i, i_time_stamp)
                attachments.append(attach)
            else:
                break
        return attachments

    def run(self):
        """
        主控方法，控制服务器的连接/断开/邮件遍历等
        :return: 发送人邮件列表/附件名列表
        """
        self._connect()
        create_dir(self.save_path)
        attachments = self.find_emails()
        self._disconnect()
        return attachments


class Export2Excel(object):
    def __init__(self, name):
        self.excel_name = name
        self.save_path = '..\\excel'
        create_dir(self.save_path)
        # 创建EXCEL表格对象
        self.workbook = xlwt.Workbook()
        self.sheet1 = self.workbook.add_sheet(self.excel_name, cell_overwrite_ok=True)

    # 创建表头
    def _create_sheet_head(self):
        try:
            self.sheet1.write(0, 0, '学号')
            self.sheet1.write(0, 1, '姓名')
            self.sheet1.write(0, 2, '作业名')
        except Exception as e:
            print('create table head error:', e.args)

    # 写入信息
    def _insert_info(self, info):
        try:
            for i in range(len(info)):
                for j in range(len(info[i])):
                    self.sheet1.write(i + 1, j, info[i][j])
        except Exception as e:
            print('insert info into sheet error: ', e.args)

    # 保存表格
    def _save_workbook(self):
        try:
            times = time.strftime('%Y_%m_%d_%H_%M', time.localtime(time.time()))
            workbook_name = self.excel_name + times + '.xls'
            self.workbook.save(self.save_path + '\\' + workbook_name)
        except Exception as e:
            print('save workbook error: ', e.args)

    def run(self, info):
        self._create_sheet_head()
        self._insert_info(info)
        self._save_workbook()


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

# if __name__ == '__main__':
#     demo = EmailSpider()
#     demo.set_account_data(account='bearcarl@qq.com', password='ouhpsdombtrngeea')
#     demo.set_date(1545878777, 1545965177)
#     demo.set_download_settings(save_attachments=True, save_executable_files=True, report_name='数据库实验')
#     demo.set_receipt(send_receipt=True)
#     demo.run()
