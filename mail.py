import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class Mail():
    def __init__(self):
        self.Receiver="mathdb@163.com"
        self.Sender="mathdoc@163.com"
        self.Authority = "466066c2a4aac05abcc0c4aacc845e68"
        self.Subject = "数字博士作业"            # 邮件主题
        self.Body = "数字博士作业，包含一个附件。"  # 邮件正文
        # 设置163邮箱的SMTP服务器和端口
        self.Server = 'smtp.163.com'
        self.Port = 465  # 163邮箱使用SSL加密
        self.Home = os.path.expanduser("~")
        self.Database = os.path.join(self.Home, "Desktop", ".mathdoc", "mathdoc.db")  # 附件文件路径

    def Send(self, attachment_path):
        # 创建MIMEMultipart对象
        msg = MIMEMultipart()
        msg['From'] = self.Sender
        msg['To'] = self.Receiver
        msg['Subject'] = self.Subject

        # 添加邮件正文
        msg.attach(MIMEText(self.Body, 'plain'))

        # 添加附件
        if attachment_path:
            try:
                with open(attachment_path, "rb") as attachment:
                    part = MIMEApplication(attachment.read(), Name=attachment_path.split('/')[-1])
                    part['Content-Disposition'] = f'attachment; filename="{attachment_path.split("/")[-1]}"'
                    msg.attach(part)
            except Exception as e:
                print(f"附件读取错误: {e}")
                return False

        try:
            # 创建SMTP会话
            server = smtplib.SMTP_SSL(self.Server, self.Port)  # 使用SSL加密
            server.login(self.Sender, self.Decode(self.Authority))  # 登录SMTP服务器
            server.sendmail(self.Sender, self.Receiver, msg.as_string())  # 发送邮件
            print("邮件发送成功！")
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
        finally:
            server.quit()

    def SendDB(self):
        # print(self.Sender)
        # print(self.Receiver)
        # print(self.Decode(self.Authority))
        # print(self.Server)
        # print(self.Port)
        # print(self.Database)
        try:
            self.Send(self.Database)
        except Exception as e:
            print(e)

    def Encode(self, s):
        rs = s[::-1] # 字符串逆序
        # 将每个字符的 ASCII 值-20再*2，并以十六进制格式拼接成一个字符串
        hex = ''.join(format((ord(char) - 20 )* 2, 'x') for char in rs)
        return hex

    def Decode(self, hex):
        # 每个十六进制值为2个字符，分割字符串
        values = [hex[i:i + 2] for i in range(0, len(hex), 2)]

        # 将每个十六进制值转换回整数，除以2再加上20还原为原始ASCII值，再转换为字符
        str = [chr(int(value, 16) // 2 + 20) for value in values]

        # 将字符逆序排列，还原为原始字符串
        str = ''.join(str[::-1])
        return str

    def TestCode(self):
        # 测试
        str = m.Authority
        hex = m.Encode(str)
        print("原始字符串:", str)
        print("编码后的十六进制字符串:", hex)

        # 将十六进制字符串解码为原始字符串
        nstr = m.Decode(hex)
        print("解码后的字符串:", nstr)

# 示例用法
if __name__ == "__main__":
    m = Mail()
    # m.TestCode()
    m.SendDB()