# mathdoc.py
import sys
import getpass
import os
import ntplib
from threading import Thread
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QMessageBox,
                             QLineEdit, QRadioButton, QPushButton, QGroupBox,
                             QVBoxLayout, QHBoxLayout, QFormLayout, QDesktopWidget)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

import configparser
import xlsxwriter
import sqlite3

from question import Question


class MathQuizLogic:
    def __init__(self):
        self.appname = "数字博士"
        self.author = "致慧星空工作室出品"
        self.version_number = "2025.03.12"
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
        self.InitDatabase()
        self.LoadSettingsFromDB()
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
        if net_time:
            self.authorization = net_time <= self.magic_date
        else:
            self.authorization = True

    def SetWindowSize(self, window):
        screen = QDesktopWidget().screenGeometry()
        window.setGeometry(0, 0, screen.width(), screen.height())

    def GetHome(self):
        return os.path.expanduser("~")

    def InitDatabase(self):
        # 初始化 SQLite 数据库
        print(f"{self.home}")
        self.db_path = os.path.join(self.home, "Desktop", "mathdoc.db")
        print(f"{self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.CreateTable()
        self.CreateSettingsTable()

    def CreateTable(self):
        # 创建表格 Exam01，如果不存在则创建
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Exam01 (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            QuestionNumber INTEGER,
            Question TEXT,
            UserAnswer TEXT,
            CorrectAnswer TEXT,
            IsCorrect TEXT,
            StartTime TEXT,
            EndTime TEXT,
            TimeUsed REAL
        )
        ''')
        self.conn.commit()

    def CreateSettingsTable(self):
        # 创建表格 Settings，如果不存在则创建
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Settings (
            Key TEXT PRIMARY KEY,
            Value TEXT
        )
        ''')
        self.conn.commit()

    def LoadSettingsFromDB(self):
        desktop_path = os.path.join(self.home, 'Desktop')
        ini_file = os.path.join(desktop_path, 'mathdoc.ini')
        if os.path.exists(ini_file):
            os.remove(ini_file)
        # 从数据库加载设置
        default_settings = {
            '加减数最小值': '10',
            '加减数最大值': '30',
            '乘除数最小值': '2',
            '乘除数最大值': '10',
            '运算符': '0',
            '项数': '2',
            '括号概率': '30'
        }

        for key, default_value in default_settings.items():
            self.cursor.execute("SELECT Value FROM Settings WHERE Key = ?", (key,))
            result = self.cursor.fetchone()
            value = result[0] if result else default_value

            if key == '加减数最小值':
                self.num_range[0] = int(value)
            elif key == '加减数最大值':
                self.num_range[1] = int(value)
            elif key == '乘除数最小值':
                self.num_range[2] = int(value)
            elif key == '乘除数最大值':
                self.num_range[3] = int(value)
            elif key == '运算符':
                self.operator = int(value)
            elif key == '项数':
                self.q.term_count = int(value)
            elif key == '括号概率':
                self.bracket_prob = int(value)

            # 确保设置已保存到数据库
            if not result:
                self.cursor.execute("INSERT INTO Settings (Key, Value) VALUES (?, ?)", (key, default_value))
                self.conn.commit()

        self.q.Set(range=self.num_range, user_operators=self.ops[self.operator])

    def SaveSettingsToDB(self):
        # 将设置保存到数据库
        settings = {
            '加减数最小值': str(self.q.range[0]),
            '加减数最大值': str(self.q.range[1]),
            '乘除数最小值': str(self.q.range[2]),
            '乘除数最大值': str(self.q.range[3]),
            '运算符': str(self.operator),
            '项数': str(self.q.term_count),
            '括号概率': str(self.bracket_prob)
        }

        for key, value in settings.items():
            self.cursor.execute("INSERT OR REPLACE INTO Settings (Key, Value) VALUES (?, ?)", (key, value))

        self.conn.commit()

    def OpenWorkbook(self):
        username = getpass.getuser()
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        desktop_path = os.path.join(self.home, 'Desktop')
        filename = f"{username}_{current_datetime}.xlsx"
        self.file_path = os.path.join(desktop_path, filename)

        self.workbook = xlsxwriter.Workbook(self.file_path)
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.worksheet = self.workbook.add_worksheet("答题记录{}".format(current_date))
        print(self.worksheet)

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
        print(self.worksheet)
        self.worksheet.write_row(self.current_row, 0, data, self.cell_format)
        self.current_row += 1

    def SaveWorkbook(self):
        if self.workbook:
            self.worksheet.autofilter(0, 0, self.current_row - 1, 7)
            self.workbook.close()

    def generate_question(self):
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

        if user_num == self.correct_answer:
            is_correct = True
        else:
            is_correct = False
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

        self.SaveToDatabase(
            self.question_number,
            self.current_question.strip(),
            user_num,
            self.correct_answer,
            is_correct,
            self.start_time,
            self.end_time,
            time_used)

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

    def SaveToDatabase(self, question_number, question, user_answer, correct_answer, is_correct, start_time, end_time,
                       time_used):
        # 将记录保存到数据库
        self.cursor.execute('''
        INSERT INTO Exam01 (QuestionNumber, Question, UserAnswer, CorrectAnswer, IsCorrect, StartTime, EndTime, TimeUsed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (question_number, question, str(user_answer), str(correct_answer), "正确" if is_correct else "错误",
              start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S"), time_used))
        self.conn.commit()
        self.ReorganizeExamData()

    def CloseDatabase(self):
        # 关闭数据库连接
        if self.conn:
            self.conn.close()

    def ReorganizeExamData(self):
        print("ReorganizeExamData()")
        try:
            # 获取当前Exam01表中的所有数据，并按StartTime排序
            self.cursor.execute("SELECT * FROM Exam01 ORDER BY ID")
            data = self.cursor.fetchall()

            if not data:
                print("Exam01表中没有数据需要整理")
                return

            # 初始化新的QuestionNumber
            new_question_number = 1
            previous_question = data[0][2]  # 第一行的Question

            # 遍历数据，整理QuestionNumber
            for row in data:
                current_id = row[0]
                current_question = row[2]

                print(current_question, previous_question)
                # 如果当前Question与上一行不同，则递增new_question_number
                if current_question != previous_question:
                    new_question_number += 1
                # 更新当前行的QuestionNumber
                self.cursor.execute("UPDATE Exam01 SET QuestionNumber = ? WHERE ID = ?", (new_question_number, current_id))
                previous_question = current_question
            # 提交更改
            self.conn.commit()
            print("Exam01表数据整理完成")

        except Exception as e:
            print(f"整理Exam01表数据时出错: {e}")


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
        self.generate_error_btn = QPushButton("生成错题本")
        self.generate_error_btn.setFont(self.logic.base_font)
        self.generate_error_btn.clicked.connect(lambda: self.export_workbook(1))  # 导出错题
        self.generate_all_btn = QPushButton("导出习题本")
        self.generate_all_btn.setFont(self.logic.base_font)
        self.generate_all_btn.clicked.connect(lambda: self.export_workbook(0))  # 导出所有习题
        self.exit_btn = QPushButton("退出程序")
        self.exit_btn.setFont(self.logic.base_font)
        self.exit_btn.clicked.connect(self.ExitApp)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.generate_error_btn)
        btn_layout.addWidget(self.generate_all_btn)
        btn_layout.addWidget(self.exit_btn)
        btn_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        if self.logic.os == "posix":
            self.apply_styles()
        self.answer_input.setFont(self.logic.base_font)
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
                self.logic.num_range[i] = int(self.logic.num_edit[i].text())
            except:
                pass

        # 更新运算符
        for i in range(5):
            if self.radio_operator[i].isChecked():
                self.logic.operator = i

        # 更新项数
        for i in range(4):
            if self.radio_terms[i].isChecked():
                self.logic.q.term_count = i + 2

        # 更新题目生成器
        self.logic.q.Set(
            range=self.logic.num_range,
            term_count=self.logic.q.term_count,
            user_operators=self.logic.ops[self.logic.operator]
        )

        # 保存设置到数据库
        self.logic.SaveSettingsToDB()

    def UpdateQuestion(self):
        if self.logic.authorization == False:
            QMessageBox.warning(None, "提醒", "软件超过使用期，请联系软件作者")
            self.ExitApp()
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

    def export_workbook(self, type):
        current_date = datetime.now().strftime("%Y%m%d")
        if type == 0:
            filename = f"习题本{current_date}.xlsx"
        else:
            filename = f"错题本{current_date}.xlsx"
        desktop_path = os.path.join(self.logic.home, 'Desktop')
        file_path = os.path.join(desktop_path, filename)

        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet()

        column_widths = [12, 30, 12, 12, 12, 22, 22, 15]
        format = workbook.add_format({
            "bg_color": "#FFFFFF",
            "align": "center",
            "valign": "vcenter",
            "font_size": "12",
        })
        worksheet.set_column(0, 100, None, format)
        cell_format = workbook.add_format({
            "bg_color": "#FFFFFF",
            "border": 1,
            "border_color": "black",
            "align": "center",
            "valign": "vcenter",
            "font_size": "12",
        })

        for col in range(8):
            worksheet.set_column(col, col, column_widths[col], format)
        worksheet.set_zoom(150)
        for row in range(0, 1000):
            worksheet.set_row(row, 25)

        headers = [
            '题号', '题目', '用户答案', '正确答案', '是否正确',
            '开始时间', '结束时间', '用时(秒)'
        ]
        worksheet.write_row(0, 0, headers, cell_format)

        if type == 0:
            self.logic.cursor.execute("SELECT * FROM Exam01")
        else:
            self.logic.cursor.execute("SELECT * FROM Exam01 WHERE IsCorrect = '错误'")
        data = self.logic.cursor.fetchall()

        for row_idx, row in enumerate(data, start=1):
            question_number = row[1]
            question = row[2]
            user_answer = row[3]
            correct_answer = row[4]
            is_correct = row[5]
            start_time = row[6]
            end_time = row[7]
            time_used = row[8]

            worksheet.write_row(row_idx, 0, [question_number, question, user_answer, correct_answer, is_correct, start_time, end_time, time_used], cell_format)

        worksheet.freeze_panes(1, 1)
        workbook.close()

        QMessageBox.information(self, "导出成功", f"文件已生成，路径：{file_path}")

    def ExitApp(self):
        self.logic.SaveSettingsToDB()
        self.logic.SaveWorkbook()
        self.logic.CloseDatabase()
        if self.logic.current_row == 1:
            try:
                os.remove(self.logic.file_path)
            except Exception as e:
                print(f"删除文件时出错: {e}")
        QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    logic = MathQuizLogic()
    window = MathQuizUI(logic)
    app.aboutToQuit.connect(window.ExitApp)
    window.showMaximized()
    sys.exit(app.exec())