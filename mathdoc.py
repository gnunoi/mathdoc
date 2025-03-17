import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QMessageBox,
                             QLineEdit, QRadioButton, QPushButton, QGroupBox,
                             QVBoxLayout, QHBoxLayout, QFormLayout, QDesktopWidget,
                             QDialog)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from exam import Exam
from mail import Mail
import random
from datetime import datetime

class MathQuizUI(QWidget):
    def __init__(self):
        super().__init__()
        self.exam = Exam()
        user = self.exam.GetUser()
        # print(user)
        while user[0] is None:
            self.Signup = SignupDialog(self.exam)
            self.Signup.exec()
            # print(self.Signup.username, self.Signup.email)
            self.Signup.close() # 退出对话框
            user = self.exam.GetUser()
            self.exam.username = user[1]
            self.exam = Exam()
        self.userid = user[0]
        self.username = user[1]
        self.email = user[2]

        # print(self.userid, self.username, self.email)
        if self.exam.os == "nt":
            self.base_font = QFont("SimSun", 24)  # 修改为24号字
        else:
            self.base_font = QFont("Pingfang SC", 24)  # 修改为24号字
        self.big_font = QFont("Arial", 32)
        self.initUI()
        self.SetWindowSize(self)

    def SetWindowSize(self, window):
        screen = QDesktopWidget().screenGeometry()
        window.setGeometry(0, 0, screen.width(), screen.height())

    def initUI(self):
        self.setWindowTitle(self.exam.title)
        main_layout = QVBoxLayout()
        control_panel = QHBoxLayout()

        # 算术项式
        term_group = QGroupBox("算术项式")
        term_group.setFont(self.base_font)
        term_layout = QVBoxLayout()
        self.radio_terms = [QRadioButton(f'{i + 2}项式') for i in range(4)]
        self.radio_terms[self.exam.q.term_count - 2].setChecked(True)
        for rb in self.radio_terms:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            term_layout.addWidget(rb)
        term_group.setLayout(term_layout)
        control_panel.addWidget(term_group, 1)

        # 运算类型
        operator_group = QGroupBox("运算类型")
        operator_group.setFont(self.base_font)
        operator_layout = QVBoxLayout()
        self.radio_operator = [
            QRadioButton('加法'), QRadioButton('减法'),
            QRadioButton('乘法'), QRadioButton('除法'),
            QRadioButton('混合运算')
        ]
        self.radio_operator[self.exam.operator].setChecked(True)
        for rb in self.radio_operator:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            operator_layout.addWidget(rb)
        operator_group.setLayout(operator_layout)
        control_panel.addWidget(operator_group, 1)

        # 数值范围
        range_group = QGroupBox("数值范围")
        range_group.setFont(self.base_font)
        range_layout = QFormLayout()
        labels = ["加减数最小值:", "加减数最大值:", "乘除数最小值:", "乘除数最大值:"]
        self.exam.num_edit = [QLineEdit(str(n)) for n in self.exam.num_range]
        for i in range(4):
            self.exam.num_edit[i].setFont(self.base_font)
            self.exam.num_edit[i].setFixedWidth(120)
            self.exam.num_edit[i].setAlignment(Qt.AlignCenter)
            range_layout.addRow(QLabel(labels[i], font=self.base_font), self.exam.num_edit[i])
            self.exam.num_edit[i].editingFinished.connect(self.UpdateSettings)
        range_group.setLayout(range_layout)
        control_panel.addWidget(range_group, 2)

        main_layout.addLayout(control_panel)

        # 题目显示
        self.question_label = QLabel()
        self.question_label.setFont(self.big_font)
        self.question_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.question_label, 2)

        # 答案输入
        self.answer_input = QLineEdit()
        self.answer_input.setFont(self.big_font)
        self.answer_input.setAlignment(Qt.AlignCenter)
        self.answer_input.returnPressed.connect(self.submit_answer)
        main_layout.addWidget(self.answer_input, 1)

        # 状态栏
        self.status_label = QLabel()
        self.status_label.setFont(self.big_font)
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label, 1)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.submit_btn = QPushButton("提交答案 (Enter)")
        self.submit_btn.setFont(self.base_font)
        self.submit_btn.clicked.connect(self.submit_answer)
        self.generate_error_btn = QPushButton("导出错题本")
        self.generate_error_btn.setFont(self.base_font)
        self.generate_error_btn.clicked.connect(lambda: self.ExportWorkbook(1))  # 导出错题
        self.generate_hard_btn = QPushButton("导出难题本")
        self.generate_hard_btn.setFont(self.base_font)
        self.generate_hard_btn.clicked.connect(lambda: self.ExportWorkbook(2))  # 导出难题
        self.generate_all_btn = QPushButton("导出习题本")
        self.generate_all_btn.setFont(self.base_font)
        self.generate_all_btn.clicked.connect(lambda: self.ExportWorkbook(0))  # 导出所有习题
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
        if self.exam.os == "posix":
            self.apply_styles()
        self.answer_input.setFont(self.big_font)
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
        }
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
            border: 3px solid #0078D7;
            border-radius: 8px;
            padding: 10px;
            font-size: 24px;
        }
        """
        self.setStyleSheet(style)

    def UpdateSettings(self):
        # 更新数值范围
        for i in range(4):
            try:
                self.exam.num_range[i] = int(self.exam.num_edit[i].text())
            except:
                pass

        # 更新运算符
        for i in range(5):
            if self.radio_operator[i].isChecked():
                self.exam.operator = i

        # 更新项数
        for i in range(4):
            if self.radio_terms[i].isChecked():
                self.exam.q.term_count = i + 2

        # 更新题目生成器
        self.exam.q.Set(
            range=self.exam.num_range,
            term_count=self.exam.q.term_count,
            user_operators=self.exam.ops[self.exam.operator]
        )

        # 保存设置到数据库
        self.exam.SaveSettingsToDB()

    def UpdateQuestion(self):
        if self.exam.authorization == False:
            QMessageBox.warning(None, "提醒", "软件超过使用期，请联系软件作者")
            self.ExitApp()
        question = self.exam.next_question()
        self.question_label.setText(f"当前题目：\n{question}")

        total = self.exam.question_number - 1
        correct_rate = self.exam.correct_number / total * 100 if total > 0 else 0
        self.status_label.setText(
            f"已答题：{total} 道 | 正确：{self.exam.correct_number} 道 | "
            f"错误：{total - self.exam.correct_number} 道 | 正确率：{correct_rate:.1f}%"
        )
        self.answer_input.setFocus()

    def submit_answer(self):
        result = self.exam.submit_answer(self.answer_input.text().strip())
        self.answer_input.clear()
        if result[0]:
            self.UpdateQuestion()
        else:
            QMessageBox.warning(self, "答案错误", result[1])


    def ExportWorkbook(self, type=None):
        wb = None
        if type == 1:
            wb = "错题本"
        elif type == 2:
            wb = "难题本"
        elif type == 0:
            wb = "习题本"
        else:
            pass
        self.exam.export_workbook(type)
        QMessageBox.information(self, "导出成功", f"{wb}已成功导出。")

    def ExitApp(self):
        self.exam.SaveSettingsToDB()
        self.exam.SaveWorkbook()
        self.exam.CloseDatabase()
        if self.exam.current_row == 1:
            # print(f"self.exam.current_row = {self.exam.current_row}")
            try:
                if os.path.exists(self.exam.workbook_file): os.remove(self.exam.workbook_file)
            except Exception as e:
                print(f"删除文件时出错: {e}")
        else:
            # print(f"Send mail to {self.email}")
            self.exam.mail.Send(attach=self.exam.workbook_file)
            self.exam.mail.Send(receiver=self.email, attach=self.exam.workbook_file)
            QMessageBox.information(self, '作业发送', f'今日作业发送至邮箱：{self.email}')
        QApplication.quit()

class SignupDialog(QDialog):
    def __init__(self, exam):
        super().__init__()
        self.exam = exam
        self.VerificationCode = None
        self.email = None
        self.username = None
        self.usercode = None
        self.initSignupDialog()

    def GetWindowSize(self):
        screen = QDesktopWidget().screenGeometry()
        return screen.width(), screen.height()

    def initSignupDialog(self):
        if self.exam.os == "nt":
            self.base_font = QFont("SimSun", 24)  # 修改为24号字
        else:
            self.base_font = QFont("Pingfang SC", 24)  # 修改为24号字
        width, height = self.GetWindowSize()
        print(width, height)
        self.setWindowTitle("用户注册")
        self.setFixedSize(int(width*2/3), int(height*2/3))
        layout = QFormLayout()
        layout.setSpacing(48)
        self.username_label = QLabel("用户名:")
        self.username_label.setFont(self.base_font)
        self.username_input = QLineEdit()
        self.username_input.setFont(self.base_font)
        layout.addRow(self.username_label, self.username_input)

        self.email_label = QLabel("邮箱:")
        self.email_label.setFont(self.base_font)
        self.email_input = QLineEdit()
        self.email_input.setFont(self.base_font)
        layout.addRow(self.email_label, self.email_input)

        self.send_code_btn = QPushButton("发送验证码")
        self.send_code_btn.setFont(self.base_font)
        self.send_code_btn.clicked.connect(self.SendVCode)
        layout.addRow("", self.send_code_btn)

        self.code_label = QLabel("验证码:")
        self.code_label.setFont(self.base_font)
        self.code_input = QLineEdit()
        self.code_input.setFont(self.base_font)
        layout.addRow(self.code_label, self.code_input)

        self.register_btn = QPushButton("注册")
        self.register_btn.setFont(self.base_font)
        self.register_btn.clicked.connect(self.Register)
        layout.addRow("", self.register_btn)

        self.setLayout(layout)
        if self.exam.os == "posix":
            self.SetStyle()

    def Register(self):
        self.username = self.username_input.text()
        self.usercode = self.code_input.text()
        if self.username is None or self.username == '':
            QMessageBox.warning(self, '用户名', '用户名不能为空')
            return

        if self.usercode is None or self.usercode != self.VerificationCode:
            QMessageBox.warning(self, '邮箱', '请输入正确的验证码')
            return
        QMessageBox.information(self, '注册成功', f'{self.username}用户注册成功，邮箱：{self.email}')
        self.exam.SaveUserToDB(self.username, self.email)

    def SendVCode(self):
        self.email = self.email_input.text()
        if self.email is None or self.email == "" or self.email.find('@') == -1:
            QMessageBox.warning(self, '邮箱', '请输入有效的邮箱')
        else:
            m = Mail()
            self.VerificationCode = str(random.randint(100000, 999999))
            m.Receiver = self.email
            m.Subject = '验证码'
            m.Body = '验证码' + self.VerificationCode
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

if __name__ == '__main__':
    local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # print(local_time)
    app = QApplication(sys.argv)
    window = MathQuizUI()
    window.showMaximized()
    window.exam.mail.Subject = f'{window.username}[{window.email}]在{local_time}发来的作业'
    window.exam.SubmitHomework()
    sys.exit(app.exec())
