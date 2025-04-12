import os
import shutil
import ntplib
from threading import Thread
from datetime import datetime
import xlsxwriter
import sqlite3

from question import Question
from mail import Mail
from PyQt5.QtWidgets import (QMessageBox)
from itertools import combinations
import re
from collections import Counter

class Exam:
    def __init__(self):
        self.appname = "数字博士"
        self.author = "致慧星空工作室出品"
        self.version_number = "2025.04.11(V0.5.5)"
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
        self.workbook_file = None
        self.workbook = None
        self.worksheet = None
        self.current_row = 0
        self.column_widths = [12, 40, 12, 12, 12, 12, 12, 15, 40]
        self.operator = 0
        self.bracket_prob = 30
        self.start_time = None
        self.end_time = None
        self.last_operator = None
        self.correct_answer = None
        self.user_answer = None
        self.tips = None
        self.answer_tips = None
        self.username = None
        self.email = None
        self.mobile = None
        self.grade = None
        self.update = None
        self.mail = Mail()
        self.InitDatabase()
        self.LoadSettingsFromDB()
        self.GetUser()
        self.OpenWorkbook()
        self.GetNetTimeInThread(self.HandleAuthorization)

    def GetOS(self):
        return os.name

    def Hide(self, path):
        # 设置文件或目录为隐藏
        if self.os == 'nt':
            try:
                os.system(f'attrib +h "{path}"')
                print(f"{path} 已被隐藏")
            except Exception as e:
                print(f"隐藏文件或目录时出错：{e}")

    def Unhide(self, path):
        if self.os == 'nt':
            try:
                # 取消隐藏文件或目录
                os.system(f'attrib -h "{path}"')
                print(f"{path} 已被显示")
            except Exception as e:
                print(f"显示文件或目录时出错：{e}")

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
        self.authorization = True

    def GetHome(self):
        return os.path.expanduser("~")

    def InitDatabase(self):
        # 初始化 SQLite 数据库
        desktop_path = os.path.join(self.home, "Desktop")
        db_folder = os.path.join(desktop_path, ".mathdoc")
        if not os.path.exists(db_folder):
            os.mkdir(db_folder)
        self.Hide(db_folder)
        old_db = os.path.join(desktop_path, "mathdoc.db")
        try:
            if os.path.exists(old_db):
                shutil.move(old_db, db_folder)
        except OSError as e:
            print(e)
        self.db_path = os.path.join(db_folder, "mathdoc.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.CreateExamTable()
        self.CreateSettingsTable()
        self.CreateMailTable()
        self.CreateUsersTable()

    def CreateUsersTable(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT UNIQUE,
            Email TEXT UNIQUE,
            Mobile TEXT UNIQUE,
            Grade INTEGER,
            RegisterDate TEXT,
            IsVerified BOOLEAN DEFAULT 0
        )
        ''')
        self.AddColumn('Users', 'Mobile', 'TEXT')
        self.AddColumn('Users', 'RegisterDate', 'TEXT')
        self.AddColumn('Users', 'Grade', 'INTEGER')
        self.conn.commit()

    def AddColumn(self, table_name, column_name, column_type):
        if table_name is None or column_name is None or column_type is None:
            print(f'table_name = {table_name}, column_name = {column_name}, column_type = {column_type}')
            return

        try:
            self.cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};')
            print(f"字段 '{column_name}' 添加成功！")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                # print(f"字段 '{column_name}' 已经存在，无需添加。")
                pass
            else:
                print(f"添加字段时出错: {e}")

    def CreateExamTable(self):
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
            TimeUsed REAL,
            Tips TEXT
        )
        ''')
        self.AddColumn('Exam01', 'Tips', 'TEXT')
        self.conn.commit()

    def CreateSettingsTable(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Settings (
            Key TEXT PRIMARY KEY,
            Value TEXT
        )
        ''')
        self.conn.commit()

    def CreateMailTable(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Mail (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT,
            Submit BOOLEAN
        )
        ''')
        self.conn.commit()

    def CheckMail(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("SELECT * FROM Mail WHERE Date = ? AND Submit = ?", (today, True))
        result = self.cursor.fetchone()
        return result is not None

    def SubmitHomework(self):
        if not self.CheckMail():
            email_thread = Thread(target=self.mail.SendDB)
            email_thread.start()
            today = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("INSERT INTO Mail (Date, Submit) VALUES (?, ?)", (today, True))
            self.conn.commit()

    def GetUser(self):
        self.cursor.execute("SELECT ID, Username, Email, Mobile, Grade, RegisterDate, IsVerified FROM Users WHERE IsVerified = 1")
        result = self.cursor.fetchone()
        if result is not None:
            self.userid = result[0]
            self.username = result[1]
            self.email = result[2]
            self.mobile = result[3]
            self.grade = result[4]
            self.register_date = result[5]
            return result
        else:
            return None, None, None

    def SaveUserToDB(self, username, email, mobile, grade):
        try:
            if self.update:
                sql = "DELETE FROM Users Where Username = ?"
                self.cursor.execute(sql, (username,))
                self.conn.commit()
            self.cursor.execute("INSERT INTO Users (Username, Email, Mobile, Grade, RegisterDate, IsVerified) VALUES (?, ?, ?, ?, ?, 1)",
                                (username, email, mobile, grade, datetime.now().strftime('%Y-%m-%d')))
            self.conn.commit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(None, "警告", "用户名或邮箱已存在！")

    def LoadSettingsFromDB(self):
        default_settings = {
            '加减数最小值': '10',
            '加减数最大值': '30',
            '乘除数最小值': '2',
            '乘除数最大值': '10',
            '运算符': '0',
            '项数': '2',
            '括号概率': '30',
            '题型': '0',
            '速算类型': '0'
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
            elif key == '题型':
                # print(f'value: {value}')
                if value is None:
                    self.q.type = 0
                else:
                    self.q.type = int(value)
                # print('self.q.type = {}'.format(self.q.type))
            elif key == '速算类型':
                # print(f'value: {value}')
                if value is None:
                    self.q.quick_calc_type = 0
                else:
                    self.q.quick_calc_type = int(value)
                # print('self.q.quick_calc_type = {}'.format(self.q.quick_calc_type))

            if not result:
                self.cursor.execute("INSERT INTO Settings (Key, Value) VALUES (?, ?)", (key, default_value))
                self.conn.commit()

        self.q.Set(range=self.num_range, user_operators=self.ops[self.operator])

    def SaveSettingsToDB(self):
        settings = {
            '加减数最小值': str(self.q.range[0]),
            '加减数最大值': str(self.q.range[1]),
            '乘除数最小值': str(self.q.range[2]),
            '乘除数最大值': str(self.q.range[3]),
            '运算符': str(self.operator),
            '项数': str(self.q.term_count),
            '括号概率': str(self.bracket_prob),
            '题型': str(self.q.type),
            '速算类型': str(self.q.quick_calc_type)
        }

        for key, value in settings.items():
            self.cursor.execute("INSERT OR REPLACE INTO Settings (Key, Value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def OpenWorkbook(self):
        username = self.username
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        desktop_path = os.path.join(self.home, 'Desktop')
        filename = f"{username}_{current_datetime}.xlsx"
        self.workbook_file = os.path.join(desktop_path, filename)

        self.workbook = xlsxwriter.Workbook(self.workbook_file)
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.worksheet = self.workbook.add_worksheet("答题记录{}".format(current_date))

        format = self.workbook.add_format({
            "bg_color": "#FFFFFF",
            "align": "center",
            "valign": "vcenter",
            "font_size": "12",
        })
        self.worksheet.set_column(0, 100, None, format)
        for col in range(9):
            self.worksheet.set_column(col, col, self.column_widths[col], format)
        self.worksheet.set_zoom(120)
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
            '开始时间', '结束时间', '用时(秒)', '检查提示'
        ])
        self.worksheet.freeze_panes(1, 1)

    def Append(self, data):
        self.worksheet.write_row(self.current_row, 0, data, self.cell_format)
        self.current_row += 1

    def SaveWorkbook(self):
        if self.workbook:
            self.worksheet.autofilter(0, 0, self.current_row - 1, 8)
            self.workbook.close()

    def GenerateQuestion(self):
        self.answer_tips = []
        self.tips = []
        self.q.Generate()
        return (self.q.question, self.q.correct_answer)

    def NextQuestion(self):
        self.current_question, self.correct_answer = self.GenerateQuestion()
        self.start_time = datetime.now()
        return self.current_question

    def check_expression(self):
        """
        判断用户输入的表达式是否包含给定数组中的数字，并且数字的出现次数与数组中的完全一致。

        参数:
            expression (str): 用户输入的表达式
            numbers (list): 给定的数字数组

        返回:
            bool: 如果表达式中的数字与给定数组完全一致（包括出现次数），返回 True，否则返回 False
        """
        # 提取表达式中的所有数字
        # 使用正则表达式匹配数字，包括整数和小数
        digits_in_expression = re.findall(r'\d+\.?\d*', self.user_answer)

        # 将提取的数字转换为浮点数
        digits_in_expression = [float(digit) for digit in digits_in_expression]

        # 将给定的数字数组转换为浮点数列表
        numbers = [float(num) for num in self.q.numbers]

        # 比较两个列表中的数字及其出现次数
        if Counter(digits_in_expression) == Counter(numbers):
            # print('输入了全部数字')
            return True
        else:
            print(Counter(digits_in_expression), Counter(numbers))
            # print('未输入全部数字')
            return False

    def SubmitAnswer(self, user_input):
        self.end_time = datetime.now()
        if self.q.type == 0 or self.q.type == 1:
            try:
                user_answer = float(user_input)
                if user_answer == int(user_answer):
                    user_answer = int(user_answer)
                    self.user_answer = user_answer
            except:
                return (False, "请输入有效数字")
        elif self.q.type == 2:
            self.user_answer = user_input
            try:
                user_answer = eval(user_input)
            except:
                return (False, "请输入有效的表达式")

        self.tips = None
        if self.q.type == 2 and not self.check_expression():
            is_correct = False
            self.tips = '未包含全部数字'
        elif user_answer == self.correct_answer:
            is_correct = True
        else:
            is_correct = False
            self.GenerateTips()

        self.time_used = round((self.end_time - self.start_time).total_seconds(), 1)
        self.Append([
            self.question_number,
            self.current_question.strip(),
            self.user_answer,
            self.correct_answer,
            "正确" if is_correct else "错误",
            self.start_time.strftime("%H:%M:%S"),
            self.end_time.strftime("%H:%M:%S"),
            self.time_used,
            self.tips
        ])
        self.SaveToDatabase(
            self.question_number,
            self.current_question.strip(),
            self.user_answer,
            self.correct_answer,
            is_correct,
            self.start_time,
            self.end_time,
            self.time_used,
            self.tips)

        if is_correct:
            self.correct_number += 1
            self.question_number += 1
            return (True, "正确")
        else:
            self.error_count += 1
            if self.error_count >= 3:
                self.question_number += 1
                self.error_count = 0
                return (False, f"正确答案是：{self.correct_answer}。请使用以下检查方法：{self.tips}")
            else:
                return (False, f"请再试一次，请使用以下检查方法：{self.tips}")

    def GenerateOppositeLists(self, lst):
        result = []
        n = len(lst)
        for k in range(1, n + 1):
            for indices in combinations(range(n), k):
                new_list = lst.copy()
                for idx in indices:
                    new_list[idx] = -new_list[idx]
                result.append(new_list)
        return result

    def IsSignError(self):
        numbers_list = self.GenerateOppositeLists(self.q.numbers)
        user_answer = abs(self.user_answer)
        correct_answer = abs(self.correct_answer)
        if user_answer / self.user_answer != correct_answer / self.correct_answer:
            return True
        for numbers in numbers_list:
            q = Question(numbers=numbers, operators=self.q.operators)
            if q.correct_answer == self.user_answer:
                # print(f'{q.expression} = {q.correct_answer}')
                return True

    def GenerateCheckTips(self):
        tips = []
        if self.q.type == 0 or self.q.type == 1:
            user_answer = abs(self.user_answer)
            correct_answer = abs(self.correct_answer)
            if self.IsSignError():
                tips.append('1. 正负号')
                print('1. 正负号')
            elif user_answer % 10 != correct_answer % 10:
                tips.append('2. 个位数')
                print('2. 个位数')
            elif len(str(user_answer)) != len(str(correct_answer)):
                tips.append('3. 总位数')
                print('3. 总位数')
            else:
                if user_answer // 10 != correct_answer // 10:
                    tips.append('4. 进借位')
                    print('4. 进借位')
        elif self.q.type == 2:
            if self.user_answer == str(eval(self.user_answer)):
                tips = f'{self.user_answer} != 24'
            else:
                tips = f'{self.user_answer} = {eval(self.user_answer)} != 24'

        return tips

    def GenerateAnswerTips(self):
        tips = []
        if self.q.type == 1:
            if self.q.quick_calc_type == 0: # 平方数
                m = self.q.numbers[0]
                n = self.q.numbers[1]
                r = m % 10
                if r >= 5:
                    c = 10 - r
                else:
                    c = r
                a = m + c
                b = m - c
                tips.append(f'{m} × {n} = ({m} + {c}) × ({m} - {c}) + {c} × {c} = {a} × {b} + {c} × {c} = {a*b} + {c*c} = {a*b+c*c}')
            if self.q.quick_calc_type == 1: # 平方差法
                m = self.q.numbers[0]
                n = self.q.numbers[1]
                a = int((m + n)/2)
                b = abs(a - self.q.numbers[0])
                tips.append(f'{m} × {n} = ({a} + {b})({a} - {b}) = {a} × {a} - {b} × {b} = {a*a} - {b*b} = {a*a-b*b}')
            if self.q.quick_calc_type == 2: # 和十速算法
                m = self.q.numbers[0]
                n = self.q.numbers[1]
                a = int(m/10)
                b = m % 10
                c = 10 -b
                tips.append(f'{a} × ({a} + 1) = {a} × {a+1} = {a*(a+1)}；{b} × {c} = {b*c}；{m} × {n} = {m*n}')
            if self.q.quick_calc_type == 3: # 大数凑十法
                m = self.q.numbers[0]
                n = self.q.numbers[1]
                r = m % 10
                c = 10 - r
                tips.append(f'{m} × {n} = ({m+c} - {c}) × {n} = {m+c} × {n} - {c} × {n} = {(m+c)*n} - {c*n} = {m*n}')
            if self.q.quick_calc_type == 4: # 逢五凑十法
                m = self.q.numbers[0]
                n = self.q.numbers[1]
                if m % 25 == 0 and n % 4 == 0:
                    a = int(m / 25)
                    b = 25
                    c = 4
                    d = int(n /4)
                else:
                    a = int(m /5)
                    b = 5
                    c = 2
                    d = int(n / 2)
                tips.append(f'{m} × {n} = {a} × {b} × {c} × {d} = {a} × {d} × {b*c} = {a * d} × {b*c} = {m * n}')
            if self.q.quick_calc_type == 5: # 双向凑十法
                m = self.q.numbers[0]
                n = self.q.numbers[1]
                b = 10 - m % 10
                a = m + b
                d = 10 - n % 10
                c = n + d
                tips.append(f'{m} × {n} = ({a} - {b}) × ({c} - {d}) = {a} × {c} - {a} × {d} - {b} × {c} + {b} × {d} = {a*c} - {a*d} - {b*c} + {b*d} = {m*n}')
        elif self.q.type == 2: # 24点游戏
            tips = self.q.calculate24(self.q.numbers)

        return tips

    def GenerateTips(self):
        if self.user_answer == self.correct_answer:
            return
        # print(self.q.expression, self.user_answer, self.correct_answer)
        if self.q.type ==0 or self.q.type == 1:
            self.tips = '；'.join(self.GenerateCheckTips())
        elif self.q.type == 2:
            self.tips = self.GenerateCheckTips()

        if self.q.type == 1:
            self.answer_tips = '；'.join(self.GenerateAnswerTips())
        elif self.q.type == 2:
            self.answer_tips = self.GenerateAnswerTips()

    def SaveToDatabase(self, question_number, question, user_answer, correct_answer, is_correct, start_time, end_time,
                       time_used, tips):
        self.cursor.execute('''
            INSERT INTO Exam01 (QuestionNumber, Question, UserAnswer, CorrectAnswer, IsCorrect, StartTime, EndTime, TimeUsed, Tips)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (question_number, question, str(user_answer), str(correct_answer), "正确" if is_correct else "错误",
            start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S"), time_used, tips)
        )
        self.conn.commit()

    def CloseDatabase(self):
        self.ReorganizeExamData()
        if self.conn:
            self.conn.close()

    def ReorganizeExamData(self):
        try:
            self.cursor.execute("SELECT * FROM Exam01 ORDER BY ID")
            data = self.cursor.fetchall()

            if not data:
                print("Exam01表中没有数据需要整理")
                return

            new_question_number = 1
            previous_question = data[0][2]

            for row in data:
                current_id = row[0]
                current_question = row[2]

                if current_question != previous_question:
                    new_question_number += 1
                self.cursor.execute("UPDATE Exam01 SET QuestionNumber = ? WHERE ID = ?", (new_question_number, current_id))
                previous_question = current_question
            self.conn.commit()
            # print("Exam01表数据整理完成")

        except Exception as e:
            print(f"整理Exam01表数据时出错: {e}")

    def export_workbook(self, type):
        current_date = datetime.now().strftime("%Y%m%d")
        if type == 0:
            filename = f"习题本{current_date}.xlsx"
        elif type == 1:
            filename = f"错题本{current_date}.xlsx"
        elif type == 2:
            filename = f"难题本{current_date}.xlsx"
        desktop_path = os.path.join(self.home, 'Desktop')
        wbfile = os.path.join(desktop_path, filename)

        workbook = xlsxwriter.Workbook(wbfile)
        worksheet = workbook.add_worksheet(filename.replace('.xlsx', ''))

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
        column_widths = [12, 40, 12, 12, 12, 25, 25, 15]
        for col in range(8):
            worksheet.set_column(col, col, column_widths[col], format)
        worksheet.set_zoom(120)
        for row in range(0, 1000):
            worksheet.set_row(row, 25)

        headers = [
            '题号', '题目', '用户答案', '正确答案', '是否正确',
            '开始时间', '结束时间', '用时(秒)'
        ]
        worksheet.write_row(0, 0, headers, cell_format)

        if type == 0:
            self.cursor.execute("SELECT * FROM Exam01")
        elif type == 1:
            self.cursor.execute("SELECT * FROM Exam01 WHERE IsCorrect = '错误'")
        elif type == 2:
            self.cursor.execute("SELECT * FROM Exam01 ORDER BY TimeUsed DESC")
            time_used_list = self.cursor.fetchall()
            total_count = len(time_used_list)
            threshold_index = min(int(total_count * 0.1), 50)
            if threshold_index == 0:
                threshold = float('inf')
            else:
                threshold = time_used_list[threshold_index - 1][8] if time_used_list else float('inf')
            self.cursor.execute(f"SELECT * FROM Exam01 WHERE TimeUsed >= {threshold} ORDER BY TimeUsed DESC")

        data = self.cursor.fetchall()
        rows = len(data)
        cols = len(data[0]) if data else 0

        for row_idx, row in enumerate(data, start=1):
            question_number = row[1]
            question = row[2]
            user_answer = row[3]
            correct_answer = row[4]
            is_correct = row[5]
            start_time = row[6]
            end_time = row[7]
            time_used = row[8]

            worksheet.write_row(
                row_idx, 0, [question_number, question,
                             user_answer, correct_answer, is_correct,
                             start_time, end_time, time_used],
                cell_format)

        worksheet.freeze_panes(1, 1)
        if rows > 0:
            worksheet.autofilter(0, 0, rows, cols - 2)
        workbook.close()