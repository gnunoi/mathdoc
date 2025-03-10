'''
生成可执行文件的命令：
Windows: pyinstaller -F -w -i favicon.ico mathapp.py
MacOS: python3 setup.py py2app
'''
import sys
import random
import getpass
import os
import ntplib
from time import sleep
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


class MathQuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.version_number = "2025.03.10"
        self.magic_date = "2025-02-28" # 月份2位，不满2位补0
        self.authorization = None
        self.home = self.GetHome()
        self.num_range = [10, 99, 10, 50]
        self.question_number = 1
        self.current_question = None
        self.correct_answer = None
        self.error_count = 0
        self.correct_number = 0
        self.config_filename = "mathapp.ini"
        self.file_path = None
        self.workbook = None
        self.worksheet = None
        self.current_row = 0
        self.column_widths = [8, 30, 12, 12, 10, 12, 12, 12]
        self.num_edit = []
        self.radio_operator = []
        self.radio_terms = []
        self.operator = 0
        self.term_count = 2
        self.bracket_prob = 30
        self.start_time = None
        self.end_time = None
        self.last_operator = None
        self.base_font = QFont("PingFang SC", 24)  # 修改为24号字
        self.big_font = QFont("Arial", 32)
        self.LoadSettings()
        self.OpenWorkbook()
        self.initUI()
        self.SetWindowSize()

    def GetNetTime(self):
        servers = ['ntp.aliyun.com', 'time.hicloud.com', 'ntp.ntsc.ac.cn',
                   'ntp.tuna.tsinghua.edu.cn']
        ntp_client = ntplib.NTPClient()
        for server in servers:
            try:
                # 请求NTP服务器（这里使用 'pool.ntp.org' 作为示例）
                response = ntp_client.request('ntp.aliyun.com')
                # 获取并返回网络时间
                utc_time = datetime.fromtimestamp(response.tx_time)
                tz_time = utc_time.astimezone()
                local_date = tz_time.strftime("%Y-%m-%d")
                local_time = tz_time.strftime("%Y-%m-%d %H:%M:%S")
                print("{}: {}".format(server, local_time))
                return local_date
            except Exception as e:
                print(f"Error fetching NTP time: {e}")
        return None


    def GetNetTimeInThread(self, callback):
        def wrapper():
            callback(self.GetNetTime())
        Thread(target=wrapper).start()

    # 回调函数
    def HandleAuthorization(self, net_time):
        sleep(30)
        print(net_time)
        print(self.magic_date)
        if net_time and net_time > self.magic_date:
            self.authorization = False
        else:
            self.authorization = True

    def SetWindowSize(self):
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())

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
                self.term_count = int(config['设置']['项数'])
                self.bracket_prob = int(config['设置']['括号概率'])
            except Exception as e:
                QMessageBox.warning(self, '警告', f'配置文件错误: {str(e)}')

    def SaveSettings(self):
        config = configparser.ConfigParser()
        config['设置'] = {
            '加减数最小值': self.num_range[0],
            '加减数最大值': self.num_range[1],
            '乘除数最小值': self.num_range[2],
            '乘除数最大值': self.num_range[3],
            '运算符': self.operator,
            '项数': self.term_count,
            '括号概率': self.bracket_prob
        }
        with open(self.config_filename, 'w') as f:
            config.write(f)

    def UpdateConfig(self):
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
                self.term_count = i + 2

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
        self.workbook = xlsxwriter.Workbook(self.file_path)  # 工作簿名称
        self.worksheet = self.workbook.add_worksheet("答题记录{}".format(current_date))
        # 定义白色背景格式，水平居中，垂直居中
        format = self.workbook.add_format({
            "bg_color": "#FFFFFF",
            "align": "center", # 水平居中
            "valign": "vcenter", # 垂直居中
            "font_size": "12", # 字号12
            })
        # 设置所有列的默认格式（从第0列到第16383列）
        self.worksheet.set_column(0, 100, None, format)

        # 设置 B 列（列索引从0开始，B列对应索引1）的列宽为25字符
        self.worksheet.set_column(1, 1, 25, format)  # 参数：起始列、结束列、宽度
        # 设置行高
        row_height = 25  # 单位：点（points）
        for row in range(0,1000):
            self.worksheet.set_row(row, row_height)

        self.worksheet.set_zoom(150)
        self.cell_format = self.workbook.add_format({
            "bg_color": "#FFFFFF",
            "border": 1,
            "border_color": "black",
            "align": "center",  # 水平居中
            "valign": "vcenter",  # 垂直居中
            "font_size": "12",  # 字号12
        })
        self.Append([
            '题号', '题目', '用户答案', '正确答案', '是否正确',
            '开始时间', '结束时间', '用时（秒）'
        ])
        self.worksheet.freeze_panes(1, 1)  # 冻结第一行第一列

    def Append(self, data):
        for idx, value in enumerate(data):
            cell_len = len(str(value)) * 2.5
            self.column_widths[idx] = max(self.column_widths[idx], cell_len)

        self.worksheet.write_row(self.current_row, 0, data, self.cell_format)
        self.current_row += 1

    def SaveWorkbook(self):
        if self.workbook:
            # for col_num, width in enumerate(self.column_widths):
            #     self.worksheet.set_column(col_num, col_num, width * 1.2, self.cell_format)
            self.workbook.close()

    def initUI(self):
        self.setWindowTitle(f'初中数学练习软件 版本：V{self.version_number}')
        main_layout = QVBoxLayout()
        control_panel = QHBoxLayout()

        # 算术项式
        term_group = QGroupBox("算术项式")
        term_group.setFont(self.base_font)
        term_layout = QVBoxLayout()
        self.radio_terms = [QRadioButton(f'{i + 2}项式') for i in range(4)]
        self.radio_terms[self.term_count - 2].setChecked(True)
        for rb in self.radio_terms:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateConfig)
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
        self.radio_operator[self.operator].setChecked(True)
        for rb in self.radio_operator:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateConfig)
            operator_layout.addWidget(rb)
        operator_group.setLayout(operator_layout)
        control_panel.addWidget(operator_group, 1)

        # 数值范围
        range_group = QGroupBox("数值范围")
        range_group.setFont(self.base_font)
        range_layout = QFormLayout()
        labels = ["加减数最小值:", "加减数最大值:", "乘除数最小值:", "乘除数最大值:"]
        self.num_edit = [QLineEdit(str(n)) for n in self.num_range]
        for i in range(4):
            self.num_edit[i].setFont(self.base_font)
            self.num_edit[i].setFixedWidth(120)
            self.num_edit[i].setAlignment(Qt.AlignCenter)
            range_layout.addRow(QLabel(labels[i], font=self.base_font), self.num_edit[i])
            self.num_edit[i].editingFinished.connect(self.UpdateConfig)
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
        self.exit_btn = QPushButton("退出程序")
        self.exit_btn.setFont(self.base_font)
        self.exit_btn.clicked.connect(self.ExitApp)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.exit_btn)
        btn_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.apply_styles()
        self.next_question()

        # 判断软件是否超过有效期
        self.GetNetTimeInThread(self.HandleAuthorization)

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
            font-size: 32px;
        }
        """
        self.setStyleSheet(style)

    def add_brackets(self, parts):
        if len(parts) < 5 or random.randint(1,100) > self.bracket_prob:
            return parts
        try:
            pos = random.randint(0, len(parts)//2 - 2)
            parts.insert(pos*2, '(')
            parts.insert(pos*2 + 3, ')')
        except:
            pass
        return parts

    def generate_question(self):
        if self.authorization == False:
            QMessageBox.warning(self, "提醒", "软件超过使用期，请联系软件作者",
                                QMessageBox.Yes | QMessageBox.No)
            self.ExitApp()
        while True:
            current_op = self.operator if self.operator != 4 else random.choice([0, 1, 2, 3])

            # 避免连续乘除
            if self.last_operator in [2] and current_op in [2]:
                current_op = random.choice([0, 1, 3])
            if self.last_operator in [3] and current_op in [3]:
                current_op = random.choice([0, 1, 2])

            nums = [random.randint(self.num_range[i % 2 * 2], self.num_range[i % 2 * 2 + 1])
                    for i in range(self.term_count)]
            ops = []
            for _ in range(self.term_count - 1):
                if current_op == 0:
                    ops.append('+')
                elif current_op == 1:
                    ops.append('-')
                elif current_op == 2:
                    ops.append('×')
                else:
                    ops.append('÷')

            parts = []
            for i in range(self.term_count * 2 - 1):
                parts.append(str(nums[i // 2]) if i % 2 == 0 else ops[i // 2])

            parts = self.add_brackets(parts)
            expr = ' '.join(parts)

            try:
                calc_expr = expr.replace('×', '*').replace('÷', '/')
                answer = round(eval(calc_expr), 2)
                if int(answer) == answer:
                    answer = int(answer)
                self.last_operator = current_op
                return f"{expr} = ", answer
            except:
                continue

    def next_question(self):
        self.current_question, self.correct_answer = self.generate_question()
        self.start_time = datetime.now()
        self.question_label.setText(f"当前题目：\n{self.current_question}")

        total = self.question_number - 1
        correct_rate = self.correct_number / total * 100 if total > 0 else 0
        self.status_label.setText(
            f"已答题：{total} 道 | 正确：{self.correct_number} 道 | "
            f"错误：{total - self.correct_number} 道 | 正确率：{correct_rate:.1f}%"
        )
        self.answer_input.setFocus()

    def submit_answer(self):
        self.end_time = datetime.now()
        user_input = self.answer_input.text().strip()
        if not user_input:
            return

        try:
            user_num = float(user_input)
            if user_num == int(user_num):
                user_num = int(user_num)
        except:
            QMessageBox.warning(self, "输入错误", "请输入有效数字")
            return

        is_correct = isclose(user_num, self.correct_answer, rel_tol=1e-9)
        time_used = round((self.end_time - self.start_time).total_seconds(), 2)

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
            self.next_question()
        else:
            self.error_count += 1
            if self.error_count >= 3:
                QMessageBox.information(self, "正确答案",
                                        f"正确答案是：{self.correct_answer}")
                self.question_number += 1
                self.error_count = 0
                self.next_question()
            else:
                QMessageBox.warning(self, "答案错误", "请再试一次")

        self.answer_input.clear()

    def ExitApp(self):
        self.SaveSettings()
        self.SaveWorkbook()
        QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MathQuizApp()
    app.aboutToQuit.connect(window.ExitApp)
    window.show()
    sys.exit(app.exec())