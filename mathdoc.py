'''
生成可执行文件的命令：
Windows: pyinstaller --noupx -F -w -i favicon.ico mathapp.py
MacOS: python3 setup.py py2app
'''
# mathdoc.py
import sys
import getpass
import os
import ntplib
from threading import Thread
from datetime import datetime
from math import isclose

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QMessageBox,
                             QLineEdit, QRadioButton, QPushButton, QGroupBox,
                             QVBoxLayout, QHBoxLayout, QFormLayout, QDesktopWidget)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

import configparser
import xlsxwriter

from question import Question

class MathQuizLogic:
    def __init__(self):
        self.appname = "数字博士"
        self.author = "致慧星空工作室出品"
        self.version_number = "2025.03.11"
        self.title = f"{self.appname}({self.author})，版本：{self.version_number}"
        self.magic_date = "2025-12-28"  # 月份2位，不满2位补0
        self.authorization = None
        self.os = self.GetOS()
        self.home = self.GetHome()
        self.num_range = [10, 30, 2, 10]
        self.q = Question()
        self.ops = [['+'], ['-'], ['*'], ['/'], ['+', '-', '*', '/']]
        self.question_number = 1
        self.current_question = None
        self.correct_answer = None
        self.error_count = 0
        self.correct_number = 0
        self.config_filename = "mathdoc.ini"
        self.file_path = None
        self.workbook = None
        self.worksheet = None
        self.current_row = 0
        self.column_widths = [12, 30, 12, 12, 12, 12, 12, 15]
        self.num_edit = []
        self.radio_operator = []
        self.radio_terms = []
        self.operator = 0
        self.bracket_prob = 30
        self.start_time = None
        self.end_time = None
        self.last_operator = None
        if self.os == "nt":
            self.base_font = QFont("SimSun", 24)  # 修改为24号字
        else:
            self.base_font = QFont("Pingfang SC", 24)  # 修改为24号字
        self.big_font = QFont("Arial", 32)
        self.LoadSettings()
        self.OpenWorkbook()
        self.GetNetTimeInThread(self.HandleAuthorization)

    def GetOS(self):
        return os.name

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
                return local_date
            except Exception as e:
                print(f"Error fetching NTP time: {e}")
        return None

    def GetNetTimeInThread(self, callback):
        def wrapper():
            callback(self.GetNetTime())
        Thread(target=wrapper).start()

    def HandleAuthorization(self, net_time):
        if net_time and net_time > self.magic_date:
            self.authorization = False
        else:
            self.authorization = True

    def SetWindowSize(self, window):
        screen = QDesktopWidget().screenGeometry()
        window.setGeometry(0, 0, screen.width(), screen.height())

    def GetHome(self):
        return os.path.expanduser("~")

    def LoadSettings(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_filename):
            try:
                config.read(self.config_filename)
                self.num_range = [
                    int(config['设置']['加减数最小值']),
                    int(config['设置']['加减数最大值']),
                    int(config['设置']['乘除数最小值']),
                    int(config['设置']['乘除数最大值'])
                ]
                self.operator = int(config['设置']['运算符'])
                self.q.term_count = int(config['设置']['项数'])
                self.bracket_prob = int(config['设置']['括号概率'])
            except Exception as e:
                QMessageBox.warning(None, '警告', f'配置文件错误: {str(e)}')
        self.q.Set(range=self.num_range, user_operators=self.ops[self.operator])

    def SaveSettings(self):
        config = configparser.ConfigParser()
        config['设置'] = {
            '加减数最小值': self.q.range[0],
            '加减数最大值': self.q.range[1],
            '乘除数最小值': self.q.range[2],
            '乘除数最大值': self.q.range[3],
            '运算符': self.operator,
            '项数': self.q.term_count,
            '括号概率': self.bracket_prob
        }
        with open(self.config_filename, 'w') as f:
            config.write(f)

    def UpdateSettings(self):
        for i in range(4):
            try:
                self.num_range[i] = int(self.num_edit[i].text())
            except:
                pass

        for pair in [(0, 1), (2, 3)]:
            if self.num_range[pair[0]] > self.num_range[pair[1]]:
                self.num_range[pair[0]], self.num_range[pair[1]] = self.num_range[pair[1]], self.num_range[pair[0]]
                self.num_edit[pair[0]].setText(str(self.num_range[pair[0]]))
                self.num_edit[pair[1]].setText(str(self.num_range[pair[1]]))
        for i in range(5):
            if self.radio_operator[i].isChecked():
                self.operator = i
        for i in range(4):
            if self.radio_terms[i].isChecked():
                self.q.term_count = i + 2
        self.q.Set(range=self.num_range,
                   term_count=self.q.term_count,
                   user_operators=self.ops[self.operator])

    def OpenWorkbook(self):
        username = getpass.getuser()
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        desktop_path = os.path.join(self.home, 'Desktop')
        filename = f"{username}_{current_datetime}.xlsx"
        self.file_path = os.path.join(desktop_path, filename)

        self.workbook = xlsxwriter.Workbook(self.file_path)
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.worksheet = self.workbook.add_worksheet("答题记录{}".format(current_date))

        format = self.workbook.add_format({
            "bg_color": "#FFFFFF",
            "align": "center",
            "valign": "vcenter",
            "font_size": "12",
        })
        self.worksheet.set_column(0, 100, None, format)
        for col in range(8):
            self.worksheet.set_column(col, col, self.column_widths[col], format)
        self.worksheet.set_zoom(150)
        for row in range(0, 1000):
            self.worksheet.set_row(row, 25)
        self.cell_format = self.workbook.add_format({
            "bg_color": "#FFFFFF",
            "border": 1,
            "border_color": "black",
            "align": "center",
            "valign": "vcenter",
            "font_size": "12",
        })
        self.Append([
            '题号', '题目', '用户答案', '正确答案', '是否正确',
            '开始时间', '结束时间', '用时(秒)'
        ])
        self.worksheet.freeze_panes(1, 1)

    def Append(self, data):
        self.worksheet.write_row(self.current_row, 0, data, self.cell_format)
        self.current_row += 1

    def SaveWorkbook(self):
        if self.workbook:
            self.worksheet.autofilter(0, 0, self.current_row-1, 7)
            self.workbook.close()

    def generate_question(self):
        if self.authorization == False:
            QMessageBox.warning(None, "提醒", "软件超过使用期，请联系软件作者")
            return ("", 0)
        self.q.Generate()
        return (self.q.question, self.q.correct_answer)

    def next_question(self):
        self.current_question, self.correct_answer = self.generate_question()
        self.start_time = datetime.now()
        return self.current_question

    def submit_answer(self, user_input):
        self.end_time = datetime.now()
        try:
            user_num = float(user_input)
            if user_num == int(user_num):
                user_num = int(user_num)
        except:
            return (False, "请输入有效数字")

        is_correct = isclose(user_num, self.correct_answer, rel_tol=1e-9)
        time_used = round((self.end_time - self.start_time).total_seconds(), 1)

        self.Append([
            self.question_number,
            self.current_question.strip(),
            user_num,
            self.correct_answer,
            "正确" if is_correct else "错误",
            self.start_time.strftime("%H:%M:%S"),
            self.end_time.strftime("%H:%M:%S"),
            time_used
        ])

        if is_correct:
            self.correct_number += 1
            self.question_number += 1
            return (True, "正确")
        else:
            self.error_count += 1
            if self.error_count >= 3:
                self.question_number += 1
                self.error_count = 0
                return (False, f"正确答案是：{self.correct_answer}")
            else:
                return (False, "请再试一次")

class MathQuizUI(QWidget):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.initUI()
        self.logic.SetWindowSize(self)

    def initUI(self):
        self.setWindowTitle(self.logic.title)
        main_layout = QVBoxLayout()
        control_panel = QHBoxLayout()

        # 算术项式
        term_group = QGroupBox("算术项式")
        term_group.setFont(self.logic.base_font)
        term_layout = QVBoxLayout()
        self.radio_terms = [QRadioButton(f'{i + 2}项式') for i in range(4)]
        self.radio_terms[self.logic.q.term_count - 2].setChecked(True)
        for rb in self.radio_terms:
            rb.setFont(self.logic.base_font)
            rb.toggled.connect(self.UpdateSettings)
            term_layout.addWidget(rb)
        term_group.setLayout(term_layout)
        control_panel.addWidget(term_group, 1)

        # 运算类型
        operator_group = QGroupBox("运算类型")
        operator_group.setFont(self.logic.base_font)
        operator_layout = QVBoxLayout()
        self.radio_operator = [
            QRadioButton('加法'), QRadioButton('减法'),
            QRadioButton('乘法'), QRadioButton('除法'),
            QRadioButton('混合运算')
        ]
        self.radio_operator[self.logic.operator].setChecked(True)
        for rb in self.radio_operator:
            rb.setFont(self.logic.base_font)
            rb.toggled.connect(self.UpdateSettings)
            operator_layout.addWidget(rb)
        operator_group.setLayout(operator_layout)
        control_panel.addWidget(operator_group, 1)

        # 数值范围
        range_group = QGroupBox("数值范围")
        range_group.setFont(self.logic.base_font)
        range_layout = QFormLayout()
        labels = ["加减数最小值:", "加减数最大值:", "乘除数最小值:", "乘除数最大值:"]
        self.logic.num_edit = [QLineEdit(str(n)) for n in self.logic.num_range]
        for i in range(4):
            self.logic.num_edit[i].setFont(self.logic.base_font)
            self.logic.num_edit[i].setFixedWidth(120)
            self.logic.num_edit[i].setAlignment(Qt.AlignCenter)
            range_layout.addRow(QLabel(labels[i], font=self.logic.base_font), self.logic.num_edit[i])
            self.logic.num_edit[i].editingFinished.connect(self.UpdateSettings)
        range_group.setLayout(range_layout)
        control_panel.addWidget(range_group, 2)

        main_layout.addLayout(control_panel)

        # 题目显示
        self.question_label = QLabel()
        self.question_label.setFont(self.logic.big_font)
        self.question_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.question_label, 2)

        # 答案输入
        self.answer_input = QLineEdit()
        self.answer_input.setFont(self.logic.big_font)
        self.answer_input.setAlignment(Qt.AlignCenter)
        self.answer_input.returnPressed.connect(self.submit_answer)
        main_layout.addWidget(self.answer_input, 1)

        # 状态栏
        self.status_label = QLabel()
        self.status_label.setFont(self.logic.big_font)
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label, 1)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.submit_btn = QPushButton("提交答案 (Enter)")
        self.submit_btn.setFont(self.logic.base_font)
        self.submit_btn.clicked.connect(self.submit_answer)
        self.exit_btn = QPushButton("退出程序")
        self.exit_btn.setFont(self.logic.base_font)
        self.exit_btn.clicked.connect(self.ExitApp)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.exit_btn)
        btn_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        if self.logic.os == "posix":
            self.apply_styles()
        self.answer_input.setFont(self.logic.big_font)
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
        self.logic.UpdateSettings()

    def UpdateQuestion(self):
        question = self.logic.next_question()
        self.question_label.setText(f"当前题目：\n{question}")

        total = self.logic.question_number - 1
        correct_rate = self.logic.correct_number / total * 100 if total > 0 else 0
        self.status_label.setText(
            f"已答题：{total} 道 | 正确：{self.logic.correct_number} 道 | "
            f"错误：{total - self.logic.correct_number} 道 | 正确率：{correct_rate:.1f}%"
        )
        self.answer_input.setFocus()

    def submit_answer(self):
        result = self.logic.submit_answer(self.answer_input.text().strip())
        self.answer_input.clear()
        if result[0]:
            self.UpdateQuestion()
        else:
            QMessageBox.warning(self, "答案错误", result[1])

    def ExitApp(self):
        self.logic.SaveSettings()
        self.logic.SaveWorkbook()
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    logic = MathQuizLogic()
    window = MathQuizUI(logic)
    app.aboutToQuit.connect(window.ExitApp)
    window.showMaximized()
    sys.exit(app.exec())