## TODO
-[x] 附件名符合规格，在限制时间之内的邮件的下载

-[ ] 处理不同时区，时间格式不同的邮件，当前代码无法处理不同时间格式的邮件，
一旦出现格式与所检测格式不同的邮件，Celery就会崩溃

-[ ] 设计一个更好的查重算法

-[x] word内容的提取

-[x] 查重结果的导出

-[ ] 在一次下载邮件的过程中，如果已经下载了的话，在Celery未重启的情况下再次下载，会出现错误

-[ ] 在helper模块中将发件学生的Email和attachments用dict联系起来，保存到redis中
    (一对多映射，还要解决attachment名称的更新问题 )
-[ ] 在在线批阅模式中以网页嵌入PDF的方式实现，预设的模式是页面左侧是pdf文件，右侧是评分模块和查重的一些信息
-[ ] 文件上上传的时候上传JPG就会为None,不知道为啥

---

## 开发过程中用到的资料
各大免费邮箱提供的POP3,SMTP,IMAP地址

[各大免费邮箱提供的POP3,SMTP,IMAP地址](http://www.itmayun.com/it/files/1/article/269895007599415/1.html)

---

编写收发邮件模块参考的资料

[python批量下载邮件附件](https://blog.csdn.net/ghostresur/article/details/81875574)

[Python读取指定日期邮件](https://blog.csdn.net/tcl415829566/article/details/78481932)

[python一般发邮件方法](https://www.cnblogs.com/fnng/p/7967213.html)

[用yagmail模块发邮件](https://www.cnblogs.com/bendouyao/p/9077689.html)

---

编写前端文件上传代码时参考的资料

[Web Uploader上传组件官网](http://fex.baidu.com/webuploader/)

*学习过程中发现官网的Demo并不是可以直接拿来用的，需要做修改*

---
[基于Web Uploader开发的一个Demo](https://github.com/jinixin/upload-demo)

*这个Demo也存在问题，比如不能上传JPG文件，前端上传的过程中提取不到文件名，会是一个空值，猜测可能是组件内部屏蔽或者代码里未设置好*

[Celery Github](https://github.com/celery/celery)

[Celery的文档](http://docs.celeryproject.org/en/master/index.html)


PyCharm常用快捷键

[PyCharm常用快捷键](https://blog.csdn.net/fighter_yy/article/details/40860949)

---
## 注意事项
1. 邮箱列表中的第一个邮件的编号是1