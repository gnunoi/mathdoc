import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QMessageBox,
                             QLineEdit, QRadioButton, QPushButton, QGroupBox,
                             QVBoxLayout, QHBoxLayout, QFormLayout, QDesktopWidget,
                             QDialog)
from PyQt5.QtGui import (QFont, QPalette, QColor)
from PyQt5.QtCore import Qt

from exam import *


def GetScreenSize():
    screen = QDesktopWidget().screenGeometry()
    return screen.width(), screen.height()

"""
类名称：MathDoc
说明：数字博士App的UI

成员变量：
appname: 软件名称
author：软件作者
authorization: 软件授权
base_font: 基本字体
big_font: 大字体
height: 窗口高度
title: 软件标题
version: 软件版本
width: 窗口宽度

成员对象：
exam: 测试对象

成员函数：
Register(): 用户注册
InitUI(): UI初始化
UpdateQuestion(): 更新试题
SubmitAnswer(): 提交答案
SetWindowSize(): 设置窗口大小

"""
class MathDoc(QWidget):
    def __init__(self):
        super().__init__()
        self.appname = "数字博士"
        self.author = "致慧星空工作室出品"
        self.version = "2025.04.18(V1.1.2)"
        self.title = f"{self.appname}({self.author})，版本：{self.version}"
        self.width, self.height = GetScreenSize()

        self.exam = Exam()
        # self.exam.Dump(self.exam.setting)
        self.Register()
        self.authorization= Authorization()
        if os.name == "nt":
            self.base_font = QFont("SimSun", 24)
        else:
            self.base_font = QFont("Pingfang SC", 24)
        self.big_font = QFont("Arial", 32)
        self.InitUI()
        # self.exam.Dump(self)
        self.SetWindowSize()

    def UpdateQuestion(self):
        if self.authorization.authorization == False:
            QMessageBox.warning(None, "提醒", "软件超过使用期，请联系软件作者")
            self.ExitApp()
        self.exam.q.Generate()
        self.tips_label.setText(self.exam.q.check_tips)
        self.answer_tips_label.setText(self.exam.q.answer_tips)
        self.question_label.setText(f"当前题目：\n{self.exam.q.question}")

        total = self.exam.record.question_number - 1
        correct_rate = self.exam.record.correct_number / total * 100 if total > 0 else 0
        self.status_label.setText(
            f"已答题：{total} 道 | 正确：{self.exam.record.correct_number} 道 | "
            f"错误：{total - self.exam.record.correct_number} 道 | 正确率：{correct_rate:.1f}%"
        )
        self.answer_input.setFocus()

    def SubmitAnswer(self):
        self.exam.q.user_input = self.answer_input.text()
        print(self.exam.q.user_input)
        self.exam.SubmitAnswer()
        # self.exam.Dump(self.exam.q)
        self.answer_input.clear()
        if not self.exam.q.is_correct:
            self.tips_label.setText(f'用户答案：{self.exam.q.user_input}；检查提示：{self.exam.q.check_tips}')
            if self.exam.q.answer_tips:
                self.answer_tips_label.setText(f'答题提示：{self.exam.q.answer_tips}')
        else:
            self.UpdateQuestion()

    def Register(self):
        while not self.exam.user.IsCompleted():
            signup = SignupDialog(self.exam)
            signup.exec()

    def SetWindowSize(self):
        self.setGeometry(0, 0, self.width, self.height)

    def InitUI(self):
        self.setWindowTitle(self.title)
        main_layout = QVBoxLayout()
        control_panel = QHBoxLayout()

        # self.exam.Dump(self.exam.q)
        # 题型
        self.type_group = QGroupBox("题型")
        self.type_group.setFont(self.base_font)
        type_layout = QVBoxLayout()
        self.type_options = [
            QRadioButton('24点游戏'), # type = 0
            QRadioButton('乘法速算'), # type = 1
            QRadioButton('四则运算'), # type = 2
        ]
        self.type_options[self.exam.setting.type].setChecked(True)
        for rb in self.type_options:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            type_layout.addWidget(rb)
        self.type_group.setLayout(type_layout)
        control_panel.addWidget(self.type_group, 1)

        # 速算
        self.qc_group = QGroupBox("乘法速算")
        self.qc_group.setFont(self.base_font)
        qc_layout = QVBoxLayout()
        self.qc_options = [
            QRadioButton('平方数'),
            QRadioButton('平方差法'),
            QRadioButton('和十速算法'),
            QRadioButton('大数凑十法'),
            QRadioButton('逢五凑十法'),
            QRadioButton('双向凑十法'),
        ]
        if not any(rb.isChecked() for rb in self.qc_options):
            self.qc_options[self.exam.setting.subtype[0]].setChecked(True)
        for rb in self.qc_options:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            qc_layout.addWidget(rb)
        self.qc_group.setLayout(qc_layout)
        control_panel.addWidget(self.qc_group, 1)
        if self.exam.setting.type != 1:
            self.qc_group.setVisible(False)

        # 算术项式
        self.term_group = QGroupBox("算术项式")
        self.term_group.setFont(self.base_font)
        term_layout = QVBoxLayout()
        self.radio_terms = [QRadioButton(f'{i + 2}项式') for i in range(4)]
        if self.exam.setting.subtype[0] > 3:
            self.exam.setting.subtype[0] = 0
        self.radio_terms[self.exam.setting.subtype[0]].setChecked(True)
        for rb in self.radio_terms:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            term_layout.addWidget(rb)
        self.term_group.setLayout(term_layout)
        control_panel.addWidget(self.term_group, 1)
        if self.exam.setting.type != 2:
            self.term_group.setVisible(False)

        # 运算类型
        self.operator_group = QGroupBox("运算类型")
        self.operator_group.setFont(self.base_font)
        operator_layout = QVBoxLayout()
        self.radio_operator = [
            QRadioButton('加法'),
            QRadioButton('减法'),
            QRadioButton('乘法'),
            QRadioButton('除法'),
            QRadioButton('混合运算')
        ]
        self.radio_operator[self.exam.setting.subtype[1]].setChecked(True)
        for rb in self.radio_operator:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            operator_layout.addWidget(rb)
        self.operator_group.setLayout(operator_layout)
        control_panel.addWidget(self.operator_group, 1)
        if self.exam.setting.type != 2:
            self.operator_group.setVisible(False)

        # 数值范围
        self.range_group = QGroupBox("数值范围")
        self.range_group.setFont(self.base_font)
        range_layout = QFormLayout()
        labels = ["加减数最小值:", "加减数最大值:", "乘除数最小值:", "乘除数最大值:"]
        range_numbers = [self.exam.setting.min_addend, self.exam.setting.max_addend,
         self.exam.setting.min_divisor, self.exam.setting.max_divisor]
        self.exam.num_edit = [QLineEdit(str(n)) for n in range_numbers]
        for i in range(4):
            self.exam.num_edit[i].setFont(self.base_font)
            self.exam.num_edit[i].setFixedWidth(360)
            self.exam.num_edit[i].setAlignment(Qt.AlignCenter)
            range_layout.addRow(QLabel(labels[i], font=self.base_font), self.exam.num_edit[i])
            self.exam.num_edit[i].editingFinished.connect(self.UpdateSettings)
        self.range_group.setLayout(range_layout)
        control_panel.addWidget(self.range_group, 2)
        if self.exam.setting.type == 0:
            self.range_group.setVisible(False)
        main_layout.addLayout(control_panel)

        # 题目显示
        self.question_label = QLabel()
        self.question_label.setFont(self.big_font)
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setObjectName("question_label")
        main_layout.addWidget(self.question_label, 2)

        # 答案输入
        self.answer_input = QLineEdit()
        self.answer_input.setFont(self.big_font)
        self.answer_input.setAlignment(Qt.AlignCenter)
        self.answer_input.returnPressed.connect(self.SubmitAnswer)

        self.answer_label = QLabel()
        self.answer_label.setFont(self.big_font)
        self.answer_label.setAlignment(Qt.AlignCenter)
        self.answer_label.setText(self.exam.q.comments)
        main_layout.addWidget(self.answer_input, 1)
        main_layout.addWidget(self.answer_label, 1)


        # 提示栏
        self.tips_label = QLabel()
        self.tips_label.setFont(self.big_font)
        self.tips_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.tips_label, 1)
        self.answer_tips_label = QLabel()
        self.answer_tips_label.setFont(self.big_font)
        self.answer_tips_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.answer_tips_label, 1)

        # 状态栏
        self.status_label = QLabel()
        self.status_label.setFont(self.big_font)
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label, 1)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.submit_btn = QPushButton("提交答案 (Enter)")
        self.submit_btn.setFont(self.base_font)
        self.submit_btn.clicked.connect(self.SubmitAnswer)
        self.generate_error_btn = QPushButton("导出错题本")
        self.generate_error_btn.setFont(self.base_font)
        self.generate_error_btn.clicked.connect(lambda: self.ExportWorkbook(1))
        self.generate_hard_btn = QPushButton("导出难题本")
        self.generate_hard_btn.setFont(self.base_font)
        self.generate_hard_btn.clicked.connect(lambda: self.ExportWorkbook(2))
        self.generate_all_btn = QPushButton("导出习题本")
        self.generate_all_btn.setFont(self.base_font)
        self.generate_all_btn.clicked.connect(lambda: self.ExportWorkbook(0))
        self.exit_btn = QPushButton("退出程序")
        self.exit_btn.setFont(self.base_font)
        self.exit_btn.clicked.connect(self.ExitApp)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.generate_error_btn)
        btn_layout.addWidget(self.generate_hard_btn)
        btn_layout.addWidget(self.generate_all_btn)
        btn_layout.addWidget(self.exit_btn)
        btn_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.answer_input.setObjectName("answer_input")
        if os.name == "posix":
            self.apply_styles()
        self.answer_input.setFont(self.big_font)
        # 创建 QPalette 对象并设置颜色
        palette = QPalette()
        palette.setColor(QPalette.WindowText, QColor(0, 120, 215)) #0078D7
        self.tips_label.setPalette(palette)
        self.answer_tips_label.setPalette(palette)
        self.UpdateQuestion()

    def apply_styles(self):
        style = """
        QGroupBox {
            border: 2px solid #0078D7;
            border-radius: 10px;
            margin-top: 15px;
            padding: 15px;
            font-size: 24px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            color: #0078D7;
            font-size: 24px;
        }
        QPushButton {
            min-width: 300px;
            padding: 12px;
            font-size: 24px;
            background: #F0F0F0;
            border: 2px solid #CCCCCC;
            border-radius: 8px;
        }
        QPushButton:hover {
            background: #E0E0E0;
        }
        QLineEdit {
            border: 3px solid #0078D7;
            border-radius: 8px;
            padding: 10px;
            font-size: 24px;
        }
        QLineEdit#answer_input {
            font-size: 36px;
        }
        """
        self.setStyleSheet(style)

    def UpdateSettings(self):
        self.exam.setting.min_addend = int(self.exam.num_edit[0].text())
        self.exam.setting.max_addend = int(self.exam.num_edit[1].text())
        self.exam.setting.min_divisor = int(self.exam.num_edit[2].text())
        self.exam.setting.max_divisor = int(self.exam.num_edit[3].text())
        if self.exam.setting.min_addend > self.exam.setting.max_addend:
            self.exam.setting.min_addend, self.exam.setting.max_addend = (self.exam.setting.max_addend, self.exam.setting.min_addend)
            self.self.exam.num_edit[0].setText(str(self.exam.setting.min_addend))
            self.self.exam.num_edit[1].setText(str(self.exam.setting.max_addend))

        if self.exam.setting.min_divisor > self.exam.setting.max_divisor:
            self.exam.setting.min_divisor, self.exam.setting.max_divisor = (self.exam.setting.max_divisor, self.exam.setting.min_divisor)
            self.self.exam.num_edit[2].setText(str(self.exam.setting.min_divisor))
            self.self.exam.num_edit[3].setText(str(self.exam.setting.max_divisor))

        for i, rb in enumerate(self.type_options):
            if rb.isChecked():
                self.exam.setting.type = i
                if i == 0:
                    self.qc_group.setVisible(False)
                    self.term_group.setVisible(False)
                    self.operator_group.setVisible(False)
                    self.range_group.setVisible(False)
                    self.exam.UpdateSetting(type=self.exam.setting.type, subtype = [0], range = [1, 10])
                elif i == 1:
                    self.qc_group.setVisible(True)
                    self.term_group.setVisible(False)
                    self.operator_group.setVisible(False)
                    self.range_group.setVisible(True)
                    for i, rb in enumerate(self.qc_options):
                        if rb.isChecked():
                            self.exam.setting.subtype[0] = i
                            break
                    self.exam.UpdateSetting(type=self.exam.setting.type, subtype=self.exam.setting.subtype,
                                            range = [self.exam.setting.min_divisor, self.exam.setting.max_divisor])
                elif i == 2:
                    self.qc_group.setVisible(False)
                    self.term_group.setVisible(True)
                    self.operator_group.setVisible(True)
                    self.range_group.setVisible(True)
                    for i in range(4):
                        if self.radio_terms[i].isChecked():
                            self.exam.setting.subtype[0] = i
                            print(f'self.exam.setting.subtype[0]: {self.exam.setting.subtype[0]}')
                    for i in range(5):
                        if self.radio_operator[i].isChecked():
                            self.exam.setting.subtype[1] = i
                    self.exam.UpdateSetting(type=self.exam.setting.type, subtype=self.exam.setting.subtype,
                                            range = [self.exam.setting.min_addend, self.exam.setting.max_addend,
                                                     self.exam.setting.min_divisor, self.exam.setting.max_divisor])

        self.exam.setting.Write()
        self.UpdateQuestion()
        self.answer_label.setText(self.exam.q.comments)

    def closeEvent(self, event):
        self.exam.Exit()
        event.accept()

    def ExitApp(self):
        self.exam.Exit()
        QApplication.quit()

class SignupDialog(QDialog):
    def __init__(self, exam):
        super().__init__()
        self.exam = exam
        self.vcode = None
        self.ucode = None
        self.username = exam.user.username
        self.grade = exam.user.grade
        self.mobile = exam.user.mobile
        self.email = exam.user.email
        self.mentor_email = exam.user.mentor_email
        self.initSignupDialog()

    def initSignupDialog(self):
        if self.exam.os == "nt":
            self.base_font = QFont("SimSun", 24)
        else:
            self.base_font = QFont("Pingfang SC", 24)
        width, height = GetScreenSize()
        self.setWindowTitle("用户注册")
        self.setFixedSize(int(width*2/3), int(height*2/3))
        layout = QFormLayout()
        layout.setSpacing(48)
        self.username_label = QLabel("用 户 名:")
        self.username_label.setFont(self.base_font)
        self.username_input = QLineEdit()
        self.username_input.setFont(self.base_font)
        if self.username:
            self.username_input.setText(self.username)
            self.username_input.setEnabled(False)
        layout.addRow(self.username_label, self.username_input)

        self.grade_label = QLabel("年　　级:")
        self.grade_label.setFont(self.base_font)
        self.grade_input = QLineEdit()
        self.grade_input.setFont(self.base_font)
        if self.grade is not None and str(self.grade) != '':
            self.grade_input.setText(str(self.grade))
            self.grade_input.setEnabled(False)
        layout.addRow(self.grade_label, self.grade_input)

        self.mobile_label = QLabel("手　　机:")
        self.mobile_label.setFont(self.base_font)
        self.mobile_input = QLineEdit()
        self.mobile_input.setFont(self.base_font)
        if self.mobile is not None and self.mobile != '':
            self.mobile_input.setEnabled(False)
            self.mobile_input.setText(self.mobile)
        layout.addRow(self.mobile_label, self.mobile_input)

        self.email_label = QLabel("本人邮箱:")
        self.email_label.setFont(self.base_font)
        self.email_input = QLineEdit()
        self.email_input.setFont(self.base_font)
        if self.email is not None and self.email != '':
            self.email_input.setEnabled(False)
            self.email_input.setText(self.email)
        layout.addRow(self.email_label, self.email_input)

        self.mentor_email_label = QLabel("导师邮箱:")
        self.mentor_email_label.setFont(self.base_font)
        self.mentor_email_input = QLineEdit()
        self.mentor_email_input.setFont(self.base_font)
        if self.mentor_email is not None and self.email != '':
            self.mentor_email_input.setEnabled(False)
            self.mentor_email_input.setText(self.mentor_email)
        layout.addRow(self.mentor_email_label, self.mentor_email_input)

        self.send_code_btn = QPushButton("发送验证码")
        self.send_code_btn.setFont(self.base_font)
        self.send_code_btn.clicked.connect(self.SendVCode)
        layout.addRow("", self.send_code_btn)

        self.code_label = QLabel("验 证 码:")
        self.code_label.setFont(self.base_font)
        self.code_input = QLineEdit()
        self.code_input.setFont(self.base_font)
        layout.addRow(self.code_label, self.code_input)

        self.register_btn = QPushButton("注    册")
        self.register_btn.setFont(self.base_font)
        self.register_btn.clicked.connect(self.Register)
        layout.addRow("", self.register_btn)

        self.setLayout(layout)
        if self.exam.os == "posix":
            self.SetStyle()

    def Register(self):
        self.username = self.username_input.text()
        self.grade = self.grade_input.text()
        self.mobile = self.mobile_input.text()
        self.email= self.email_input.text()
        self.mentor_email = self.mentor_email_input.text()
        self.ucode = self.code_input.text()

        print(self.username, self.grade, self.mobile, self.email, self.ucode)
        if self.username == '':
            QMessageBox.warning(self, '用户名', '用户名不能为空')
            return
        if self.email == '' or self.email.find('@') == -1:
            QMessageBox.warning(self, '邮箱', '邮箱不能为空')
            return
        if self.mobile == '':
            QMessageBox.warning(self, '手机号', '手机号不能为空')
            return
        if self.ucode != self.vcode:
            QMessageBox.warning(self, '邮箱', '请输入正确的验证码')
            return

        QMessageBox.information(self, '注册成功', f'{self.username}用户注册成功，邮箱：{self.email}')

        self.exam.user.Register(username = self.username, email = self.email, mobile = self.mobile,
                 grade = self.grade, mentor_email = self.mentor_email)
        self.close()

    def SendVCode(self):
        self.email = self.email_input.text()
        if self.email == '' or self.email.find('@') == -1:
            QMessageBox.warning(self, '邮箱', '请输入有效的邮箱')
        else:
            m = Mail()
            self.vcode = str(random.randint(100000, 999999))
            # print(self.vcode)
            m.receiver = self.email
            m.subject = '验证码'
            m.body = '验证码：\n' + self.vcode
            print()
            m.Send()
            QMessageBox.information(self, '验证码已发送', f'验证码已发送，请在邮箱{self.email}中查收邮件。')

    def SetStyle(self):
        style = """
        QPushButton {
            min-width: 320px;
            padding: 12px;
            font-size: 24px;
            background: #F0F0F0;
            border: 2px solid #CCCCCC;
            border-radius: 8px;
        }
        QPushButton:hover {
            background: #E0E0E0;
        }
        QLineEdit {
            min-width: 320px;
            border: 3px solid #0078D7;
            border-radius: 8px;
            padding: 10px;
            font-size: 24px;
        }
        QLabel {
            font-size: 24px;
        }
        """
        self.setStyleSheet(style)

import ntplib
class Authorization:
    def __init__(self):
        self.magic_date = "2025-12-28"  # 月份2位，不满2位补0
        self.authorization = True
        self.GetNetTimeInThread(self.HandleAuthorization)
        # self.GetNetTime()

    def GetNetTime(self):
        servers = ['ntp.aliyun.com', 'time.hicloud.com', 'ntp.ntsc.ac.cn',
                   'ntp.tuna.tsinghua.edu.cn']
        ntp_client = ntplib.NTPClient()
        for server in servers:
            try:
                response = ntp_client.request(server)
                utc_time = datetime.fromtimestamp(response.tx_time)
                tz_time = utc_time.astimezone()
                local_date = tz_time.strftime("%Y-%m-%d")
                local_time = tz_time.strftime("%Y-%m-%d %H:%M:%S")
                print(f'Date from network: {local_date}')
                return local_date
            except Exception as e:
                print(f"Error fetching NTP time: {e}")
        return None

    def GetNetTimeInThread(self, callback):
        # print('GetNetTimeInThread()')
        def wrapper():
            callback(self.GetNetTime())

        Thread(target=wrapper).start()

    def HandleAuthorization(self, net_time):
        if net_time:
            self.authorization = net_time <= self.magic_date
        else:
            self.authorization = True


if __name__ == '__main__':
    local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app = QApplication(sys.argv)
    window = MathDoc()
    window.showMaximized()
    sys.exit(app.exec())