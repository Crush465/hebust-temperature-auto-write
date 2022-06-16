import requests as r
from lxml import etree
import time
import smtplib
import random
from email.mime.text import MIMEText
from email.header import Header

# 此段代码用于个人测试用。
# 在__init__方法内修改信息即可使用
# 想全天监控填写情况建议把此段代码放在阿里云的函数计算上面，并用触发器设置执行时间

class AuotoWrite:
    # 加载所有信息
    def __init__(self):

        # ?处是要填写的
        self.data = None
        self.param = {
            "stuNum": "?",  # 学号
            "pwd": "?",  # 密码
            "vcode": "",
        }
        self.my_email = "?"  # 此处是python发送邮件利用的邮箱
        self.send_mail = "?"  # 此处是接收填写情况的邮箱
        self.license_code = "?"  # 发送邮箱的pop授权码
        self.smtp_server = "smtp.qq.com"  # qq smtp 的服务器
        # 以下已设置好
        # 设填写的体温a是36.3~36.7的随机数
        # 此处是找到当前时间戳定位url
        self.a = random.uniform(36.3, 36.7)
        self.a = str(self.a)[:4:]
        self.timetamp = time.mktime(time.localtime())
        self.timetamp = int(self.timetamp)

        # header参数，防止检测到非人类
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.62"
        }
        # 各个链接
        self.url = "http://xscfw.hebust.edu.cn/survey/ajaxLogin"  # 登录链接
        self.url2 = "http://xscfw.hebust.edu.cn/survey/index"  # 获取sid链接
        self.url3 = f"http://xscfw.hebust.edu.cn/survey/surveySave?timestamp={self.timetamp}"  # 填报体温的地址

    def send_email(self, content):
        # 发送邮件函数
        try:

            if content == "未完成":
                msg = MIMEText(f"你尚未完成填写+你将要填写的体温是{self.a}", "plain", "utf-8")
            else:
                msg = MIMEText(f"你已完成填写，无须再填写", "plain", "utf-8")
            # 判断填写情况并发送邮件
            msg['From'] = Header(self.my_email)
            msg['To'] = Header(self.send_mail)
            msg['Subject'] = Header("健康填报情况")
            server = smtplib.SMTP_SSL(host=self.smtp_server)
            server.connect(self.smtp_server, 465)
            server.login(self.my_email, password=self.license_code)
            server.sendmail(self.my_email, self.send_mail, msg.as_string())
            server.quit()
            print("填写情况是" +self.a)
            # 连接服务器
        except:
            print('邮件发送失败')
            # 程序运行失败的报错信息

    def tianbao(self):
        # 填报程序
        try:
            rep = r.post(url=self.url3, params=self.data, headers=self.header, cookies=self.cookies)
            print(rep)
        except:
            print("填报出错")

    # 账号信息
    def start(self):
        try:
            response = r.post(url=self.url, params=self.param, headers=self.header)
            cookiesJAR = response.cookies  # 获取cookies
            self.cookies = cookiesJAR.get_dict()  # 把cookies写成字典形式
            res = r.get(url=self.url2, headers=self.header, cookies=self.cookies, params=self.param)
            print("登录成功")
        except:
            print("登录失败")
        # 获取完成情况
        try:
            res.encoding = 'uft-8'
            html = etree.HTML(res.text)
            content = html.xpath('/html/body/ul/li[1]/div/span/text()')
        except:
            print("获取失败")
        # 获取当前日期要填的文档的sid
        try:
            url4 = 'http://xscfw.hebust.edu.cn/survey/index.action'
            rek = r.get(url=url4, cookies=cookies, headers=self.header)
            rek.encoding = 'utf-8'
            html3 = etree.HTML(rek.text)
            sid = html3.xpath('/html/body/ul/li[1]/@sid')[0]
            print(f"获取sid成功：{sid}")
        except:
            print("获取sid失败,请检查你的学号和密码是否填写正确")
        #####获取stuId和qid
        try:
            url5 = f'http://xscfw.hebust.edu.cn/survey/surveyEdit?id={sid}'
            rej = r.get(url=url5, cookies=cookies, headers=self.header)
            rej.encoding = 'utf-8'
            html2 = etree.HTML(rej.text)
            stuId = html2.xpath('//*[@id="surveyForm"]/input[2]/@value')[0]
            qid = html2.xpath('//*[@id="surveyForm"]/input[3]/@value')[0]
            print(f"获取stuId成功：{stuId}")
            print(f"获取qid成功:{qid}")
        except:
            print("获取stuId qid 失败")
        #####要填写的数据,其中a是36.3~36.7的随机数
        try:
            self.data = {
                "id": sid,
                "stuId": stuId,
                "qid": qid,
                "location": '',
                "c0": "不超过37.3℃，正常",
                "c1": self.a,
                "c3": "不超过37.3℃，正常",
                "c4": self.a,
                "c6": "健康",
            }
        except:
            print("获取信息有误")
        # 判断程序
        try:
            print("开始执行")
            if content[0] == '已完成':
                self.send_email('已完成')
            if content[0] == '未完成':
                self.send_email('未完成')
                print("填写开始")
                self.tianbao()
            print("已发送填写情况邮件")
        except:
            print("判断填写情况失败")
A = AuotoWrite()
A.start()
