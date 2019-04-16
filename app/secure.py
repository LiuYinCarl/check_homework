SQLALCHEMY_DATABASE_URI = 'mysql+cymysql://root:root@127.0.0.1:3306/check_homework'
SECRET_KEY = 'squirrel'

# email configuration
MAIL_SERVER = 'smtp.email.qq.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TSL = False
MAIL_USERNAME = 'bearcarl@qq.com'
MAIL_PASSWORD = 'tuvufevrdbhmbagf'
MAIL_SUBJECT_PREFIX = '[check homework]'
MAIL_SENDER = 'check homework<robot>'

# 开启数据库查询性能测试
SQLALCHEMY_RECORD_QUERIES = True

# 性能测试的阀值
DATABASE_QUERY_TIMEOUT = 0.5

SQLALCHEMY_TRACK_MODIFICATIONS = True

WTF_CSRF_CHECK_DEFAULT = False

SQLALCHEMY_ECHO = True

from datetime import timedelta
REMEMBER_COOKIE_DURATION = timedelta(days=30)