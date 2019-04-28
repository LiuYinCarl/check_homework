import unittest
from app.utils.helper import allowed_file, get_smtp_host

#                            _ooOoo_
#                           o8888888o
#                           88" . "88
#                           (| -_- |)
#                            O\ = /O
#                        ____/`---'\____
#                      .   ' \\| |# `.
#                       / \\||| : |||# \
#                     / _||||| -:- |||||- \
#                       | | \\\ - #/ | |
#                     | \_| ''\---/'' | |
#                      \ .-\__ `-` ___/-. /
#                   ___`. .' /--.--\ `. . __
#                ."" '< `.___\_<|>_/___.' >'"".
#               | | : `- \`.;`\ _ /`;.`/ - ` : | |
#                 \ \ `-. \_ __\ /__ _/ .-` / /
#         ======`-.____`-.___\_____/___.-`____.-'======
#                            `=---='
#
#         .............................................
#                  佛祖保佑             永无BUG
#          佛曰:    写完代码就写单测真的有用。。。。


# 测试helper模块里面的函数
class TestHelper(unittest.TestCase):

    def test_to_timestamp(self):
        pass

    def test_allow_file(self):
        file1 = 'abc.doc'
        file2 = '哈哈.doc'
        file3 = 'abc .doc'
        file4 = '123-孙真意 .doc'

        file5 = 'abcdef'
        file6 = 'abcffre.txt.docxx'

        self.assertEqual(allowed_file(file1), True)
        self.assertEqual(allowed_file(file2), True)
        self.assertEqual(allowed_file(file3), True)
        self.assertEqual(allowed_file(file4), True)
        self.assertEqual(allowed_file(file5), False)
        self.assertEqual(allowed_file(file6), False)

    def test_get_smtp_host(self):
        email1 = '1234789@qq.com'
        email2 = '12345@gmail.com'
        email3 = '1234@126.com'
        email4 = '1234@163.com'
        email5 = '1234@sohu.com'
        email6 = '1234@sina.com'
        email7 = '1234@139.com'

        self.assertEqual(get_smtp_host(email1), 'smtp.qq.com')
        self.assertEqual(get_smtp_host(email2), 'smtp.gmail.com')
        self.assertEqual(get_smtp_host(email3), 'smtp.126.com')
        self.assertEqual(get_smtp_host(email4), 'smtp.163.com')
        self.assertEqual(get_smtp_host(email5), 'smtp.sohu.com')
        self.assertEqual(get_smtp_host(email6), 'smtp.sina.com')
        self.assertEqual(get_smtp_host(email7), 'smtp.139.com')


if __name__ == '__main__':
    unittest.main()