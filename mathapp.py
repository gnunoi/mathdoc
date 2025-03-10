'''
生成一个完整的可执行文件的命令如下：
Windows: pyinstaller -F -w -i favicon.ico mathapp.py
MacOS: python3 setup.py py2app
'''
import sys
import random
import getpass
import os
import ntplib
from threading import Thread
from datetime import datetime, timezone

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QMessageBox,
                             QLineEdit, QRadioButton, QPushButton, QGroupBox,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout)
from PyQt5.QtGui import QFont

import configparser
import xlsxwriter

class MathQuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.version_number = "2025.03.02"
        self.magic_time = "2025-12-31"
        self.GetNetTimeInThread(self.HandleTime)
        self.home = self.GetHome()
        self.num_range = [10, 99, 10, 50]
        self.question_number = 1
        self.current_question = None
        self.correct_answer = None
        self.error_count = 0  # 错误计数器
        self.correct_number = 0  # 做对的题目数
        self.font=QFont()
        self.config_filename = "mathapp.ini"
        self.file_path = None
        self.workbook = None # 工作簿
        self.worksheet = None
        self.current_row = 0
        self.cell_format = None
        self.num_edit = []
        self.radio_operator = []
        self.operator = 0
        self.LoadSettings()
        self.OpenWorkbook()
        self.initUI()

    def GetNetTime(self):
        servers = ['ntp.aliyun.com', 'time.hicloud.com', 'ntp.ntsc.ac.cn',
                   'ntp.tuna.tsinghua.edu.cn']
        ntp_client = ntplib.NTPClient()
        for server in servers:
            try:
                # 请求NTP服务器（这里使用 'pool.ntp.org' 作为示例）
                response = ntp_client.request('ntp.aliyun.com')
                # 获取并返回网络时间
                utc_time = datetime.fromtimestamp(response.tx_time, timezone.utc)
                tz_time = utc_time.astimezone()
                local_time = tz_time.strftime("%Y-%m-%d")
                print("{}: {}".format(server, local_time))
                return local_time
            except Exception as e:
                print(f"Error fetching NTP time: {e}")
        return None

    def GetNetTimeInThread(self, callback):
        def wrapper():
            net_time = self.GetNetTime()
            callback(net_time)

        # 创建并启动新线程
        thread = Thread(target=wrapper)
        thread.start()

    # 示例回调函数，用于处理获取到的网络时间
    def HandleTime(self, net_time):
        if net_time == None:
            return
        if net_time > self.magic_time:
            QMessageBox.warning("超时","请联系软件作者")
            self.ExitApp()
        else:
            print("软件在有效期内...")

    def GetHome(self):
        home = os.path.expanduser("~")
        print(home)
        return home

    def LoadSettings(self):
        """从配置文件加载设置"""
        config = configparser.ConfigParser()
        if os.path.exists(self.config_filename):
            try:
                config.read(self.config_filename)
                self.num_range[0] = int(config['设置']['第一个数最小值'])
                self.num_range[1] = int(config['设置']['第一个数最大值'])
                self.num_range[2] = int(config['设置']['第二个数最小值'])
                self.num_range[3] = int(config['设置']['第二个数最大值'])
                self.operator = int(config['设置']['运算符'])
            except:
                QMessageBox.warning(self, '警告', '配置文件损坏，已使用默认设置')

    def SaveSettings(self):
            config = configparser.ConfigParser()
            config['设置'] = {
                '第一个数最小值': self.num_range[0],
                '第一个数最大值': self.num_range[1],
                '第二个数最小值': self.num_range[2],
                '第二个数最大值': self.num_range[3],
                '运算符': self.operator,
            }
            with open(self.config_filename, 'w') as f:
                config.write(f)

    def UpdateConfig(self):
        n = 0
        f = 0.0
        for i in range(0,4):
            try:
                text = self.num_edit[i].text()
                f = float(text)
                n = int(f)
                self.num_range[i] = n
                if f"{n}" != f"{f}": self.num_edit[i].setText(str(n))
            except ValueError:
                print("Error: {} {} {}".format(i,n,self.num_range[i]))
                pass
        for i in range(0,4):
            self.num_edit[i].setText(str(self.num_range[i]))
            print("{}: {}".format(i, self.num_range[i]))

        if self.num_range[0] > self.num_range[1]:
            t = self.num_range[0]
            self.num_range[0] = self.num_range[1]
            self.num_range[1] = t
            self.num_edit[0].setText(str(self.num_range[0]))
            self.num_edit[1].setText(str(self.num_range[1]))

        if self.num_range[2] > self.num_range[3]:
            t = self.num_range[2]
            self.num_range[2] = self.num_range[3]
            self.num_range[3] = t
            self.num_edit[2].setText(str(self.num_range[2]))
            self.num_edit[3].setText(str(self.num_range[3]))

        for i in range(0,5):
            if self.radio_operator[i].isChecked(): self.operator = i

    def OpenWorkbook(self):
        # 获取当前用户名
        username = getpass.getuser()
        # 获取当前日期和时间
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 构建文件名和保存路径
        desktop_path = os.path.join(self.home, 'Desktop')
        filename = f"{username}_{current_datetime}.xlsx"
        self.file_path = os.path.join(desktop_path, filename)

        # 创建工作簿和工作表
        current_date = datetime.now().strftime("%Y-%m-%d")
        ws_name = current_date
        self.workbook = xlsxwriter.Workbook(self.file_path)  # 工作簿名称
        self.worksheet = self.workbook.add_worksheet(ws_name)  # 工作表名称
        # 定义白色背景格式，水平居中，垂直居中
        format = self.workbook.add_format({
            "bg_color": "#FFFFFF",
            "align": "center", # 水平居中
            "valign": "vcenter", # 垂直居中
            "font_size": "12", # 字号12
            })
        # 设置所有列的默认格式（从第0列到第16383列）
        self.worksheet.set_column(0, 16383, None, format)
        # 设置 B 列（列索引从0开始，B列对应索引1）的列宽为25字符
        self.worksheet.set_column(1, 1, 25, format)  # 参数：起始列、结束列、宽度
        row_height = 25  # 单位：点（points）
        for row in range(0,1048576):
            self.worksheet.set_row(row, row_height)
        self.worksheet.set_zoom(150)
        self.cell_format = self.workbook.add_format({
            "bg_color": "#FFFFFF",
            "align": "center",  # 水平居中
            "valign": "vcenter",  # 垂直居中
            "left": 1,
            "right": 1,
            "top": 1,
            "bottom": 1,
            "border_color": "black",
            "font_size": "12",  # 字号12
        })
        self.Append(['题号', '题目', '用户答案', '正确答案', '是否正确'])

    def Append(self, data):
        self.worksheet.write_row(self.current_row, 0, data, self.cell_format)
        self.current_row += 1

    def SaveWorkbook(self):
        self.workbook.close()

    def initUI(self):
        self.setWindowTitle('初中数学练习软件，版本：V{}，致慧星空工作室出品（抖音号：taihangyishu）'.format(self.version_number))
        screens = QApplication.screens()
        self.setGeometry(screens[0].geometry())
        self.showMaximized()

        self.layout = QGridLayout()
        self.font.setPointSize(16)
        self.num_edit.append(QLineEdit(str(self.num_range[0])))
        self.num_edit.append(QLineEdit(str(self.num_range[1])))
        self.num_edit.append(QLineEdit(str(self.num_range[2])))
        self.num_edit.append(QLineEdit(str(self.num_range[3])))
        settings_group = QGroupBox("题目设置")
        settings_layout = QHBoxLayout()

        operator_group = QGroupBox("运算选择")
        operator_layout = QVBoxLayout()
        self.radio_operator.append(QRadioButton('加法'))
        self.radio_operator.append(QRadioButton('减法'))
        self.radio_operator.append(QRadioButton('乘法'))
        self.radio_operator.append(QRadioButton('除法'))
        self.radio_operator.append(QRadioButton('混合运算'))
        for i in range(0,5):
            operator_layout.addWidget(self.radio_operator[i])
            # 连接信号到槽函数
            self.radio_operator[i].toggled.connect(self.UpdateConfig)

        operator_group.setLayout(operator_layout)
        operator_group.setFont(self.font)
        settings_layout.addWidget(operator_group, stretch=1)

        range_group = QGroupBox("范围设置")
        range_layout = QFormLayout()
        # "加数/减数/第1个乘数/商的最小值:","加数/减数/第1个乘数/商的最大值:"
        # "第2个乘数/除数的最小值:","第2个乘数/除数的最大值:",
        range_layout.addRow("加数/减数/第1个乘数/商的最小值:", self.num_edit[0])
        range_layout.addRow("加数/减数/第1个乘数/商的最大值:", self.num_edit[1])
        range_layout.addRow("第2个乘数/除数的最小值:", self.num_edit[2])
        range_layout.addRow("第2个乘数/除数的最大值:", self.num_edit[3])
        self.num_edit[0].editingFinished.connect(self.UpdateConfig)
        self.num_edit[1].editingFinished.connect(self.UpdateConfig)
        self.num_edit[2].editingFinished.connect(self.UpdateConfig)
        self.num_edit[3].editingFinished.connect(self.UpdateConfig)

        self.radio_operator[self.operator].setChecked(True)

        range_group.setLayout(range_layout)
        range_group.setFont(self.font)
        settings_layout.addWidget(range_group, stretch=1)

        settings_group.setLayout(settings_layout)
        settings_group.setFont(self.font)
        self.layout.addWidget(settings_group)
        self.font.setPointSize(32)
        self.question_label = QLabel('题目', self)
        self.layout.addWidget(self.question_label)
        self.question_label.setFont(self.font)

        self.answer_input = QLineEdit(self)
        self.answer_input.setFont(self.font)
        self.layout.addWidget(self.answer_input)
        self.answer_input.returnPressed.connect(self.submit_answer)

        self.correct_answer_label = QLabel('答题判断：', self)
        self.layout.addWidget(self.correct_answer_label)
        self.correct_answer_label.setFont(self.font)

        self.status_label = QLabel('提示：输入答案后直接按下回车，或鼠标点击提交按钮。', self)
        self.layout.addWidget(self.status_label)
        self.status_label.setFont(self.font)

        self.submit_button = QPushButton('提交', self)
        self.submit_button.setFont(self.font)
        self.submit_button.clicked.connect(self.submit_answer)
        self.layout.addWidget(self.submit_button)

        self.exit_button = QPushButton('退出', self)
        self.exit_button.clicked.connect(self.Quit)
        self.layout.addWidget(self.exit_button)
        self.exit_button.setFont(self.font)
        self.setLayout(self.layout)

        self.next_question()

    def next_question(self):
        if self.question_number - 1 == 0:
            percentage="  "
        else:
            percentage='{:.0f}%'.format(self.correct_number*100.0/(self.question_number - 1))

        text="答题统计：已答题{}道，做对{}道，做错{}道，正确率：{}...".format(self.question_number - 1,
            self.correct_number, self.question_number - 1 - self.correct_number,percentage)

        self.correct_answer_label.setText(text)
        self.current_question, self.correct_answer = self.generate_question()
        self.question_label.setText("题目：\n\n" + self.current_question)

    def generate_question(self):
        operators = ['+', '−', '×', '÷']
        opr = self.operator
        if opr == 4:
            opr = random.randrange(0,4) # start:0, stop:4, not include
        # print(opr)

        if opr == 0:
            num1 = random.randint(self.num_range[0], self.num_range[1])
            num2 = random.randint(self.num_range[0], self.num_range[1])
            answer = num1 + num2
        elif opr == 1:
            num1 = random.randint(self.num_range[0], self.num_range[1])
            num2 = random.randint(self.num_range[0], self.num_range[1])
            answer = num1 - num2
        elif opr == 2:
            num1 = random.randint(self.num_range[0], self.num_range[1])
            num2 = random.randint(self.num_range[2], self.num_range[3])
            answer = num1 * num2
        else:
            num1 = random.randint(self.num_range[0], self.num_range[1])
            num2 = random.randint(self.num_range[2], self.num_range[3])
            # 确保除法结果为整数，将num1作商，num2作除数。
            answer = num1
            num1 = num1 * num2

        if num2 < 0:
            question = f"{num1} {operators[opr]} ({num2}) = "
        else:
            question = f"{num1} {operators[opr]} {num2} = "

        return question, answer

    def submit_answer(self):
        user_answer = self.answer_input.text()
        if user_answer.lower() == 'exit':
            self.exit_app()
            return
        try:
            user_answer = int(user_answer)
        except ValueError:
            QMessageBox.warning(self, '输入错误', '请输入有效的数字或输入"exit"退出。')
            return
        if user_answer == self.correct_answer:
            result = '正确'
            self.correct_number += 1
            self.error_count = 0  # 重置错误计数器
            self.Append([self.question_number, self.current_question, user_answer, self.correct_answer, result])
            self.answer_input.clear()
            self.question_number += 1
            self.next_question()
        else:
            self.error_count += 1
            if self.error_count >= 3:
                result = '错误'
                self.Append([self.question_number, self.current_question, user_answer, self.correct_answer, result])
                self.answer_input.clear()
                self.question_number += 1
                self.next_question()
                self.error_count = 0  # 重置错误计数器
            else:
                result = '错误'
                self.Append([self.question_number, self.current_question, user_answer, self.correct_answer, result])
                self.answer_input.clear()

    def Quit(self):
        QApplication.quit()

    def ExitApp(self):
        self.SaveSettings()
        if self.current_row >= 2: self.SaveWorkbook() # 已做题，保存工作簿。


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MathQuizApp()
    app.aboutToQuit.connect(ex.ExitApp)  # 关联退出信号到清理函数
    ex.show()
    sys.exit(app.exec())
