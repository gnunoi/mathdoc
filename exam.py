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

class Exam:
    def __init__(self):
        self.appname = "数字博士"
        self.author = "致慧星空工作室出品"
        self.version_number = "2025.03.19(V0.4.5)"
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
        self.mail = Mail()
        self.InitDatabase()
        self.LoadSettingsFromDB()
        self.userid = None
        self.username = None
        self.email = None
        self.mobile = None
        self.grade = None
        self.register_date = None
        self.update = False
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

    def GetHome(self):
        return os.path.expanduser("~")

    def InitDatabase(self):
        # 初始化 SQLite 数据库
        # print(f"{self.home}")
        desktop_path = os.path.join(self.home, "Desktop")
        # print(desktop_path)
        ini_file = os.path.join(desktop_path, "mathdoc.ini")
        if os.path.exists(ini_file):
            os.remove(ini_file)
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
        # print(f"{self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.CreateExamTable()
        self.CreateSettingsTable()
        self.CreateMailTable()
        self.CreateUsersTable()


    def CreateUsersTable(self):
        # print('Create Users Table...')
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
                print(f"字段 '{column_name}' 已经存在，无需添加。")
            else:
                print(f"添加字段时出错: {e}")

    def CreateExamTable(self):
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
            TimeUsed REAL,
            Tips TEXT
        )
        ''')
        self.AddColumn('Exam01', 'Tips', 'TEXT')
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

    def CreateMailTable(self):
        # 创建表格 Mail，如果不存在则创建
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Mail (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT,
            Submit BOOLEAN
        )
        ''')
        self.conn.commit()

    def CheckMail(self):
        # 检查今天是否已经发送过邮件
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("SELECT * FROM Mail WHERE Date = ? AND Submit = ?", (today, True))
        result = self.cursor.fetchone()
        return result is not None

    def SubmitHomework(self):
        # 如果今天未发送邮件，则发送邮件并记录
        if not self.CheckMail():
            # 创建并启动线程
            email_thread = Thread(target=self.mail.SendDB)
            email_thread.start()
            # 等待线程完成（可选）
            # self.mail.SendDB()  # 假设Mail类中有send_mail方法
            today = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("INSERT INTO Mail (Date, Submit) VALUES (?, ?)", (today, True))
            self.conn.commit()

    def GetUser(self):
        # 检查是否有已注册的用户
        self.cursor.execute("SELECT ID, Username, Email, Mobile, Grade, RegisterDate, IsVerified FROM Users WHERE IsVerified = 1")
        result = self.cursor.fetchone()
        if result is not None:
            # print(result)
            self.userid = result[0]
            self.username = result[1]
            self.email = result[2]
            self.mobile = result[3]
            self.grade = result[4]
            self.register_date = result[5]
            print(result)
            return result
        else:
            return None, None, None

    def SaveUserToDB(self, username, email, mobile, grade):
        if username is None or email is None or mobile is None or grade is None:
            print(f'username = {username}')
            print(f'email = {email}')
            print(f'mobile = {mobile}')
            print(f'grade = {grade}')
        try:
            if self.update:
                print(username)
                sql = "DELETE FROM Users Where Username = ?"
                self.cursor.execute(sql, (username,))
                self.conn.commit()
            self.cursor.execute("INSERT INTO Users (Username, Email, Mobile, Grade, RegisterDate, IsVerified) VALUES (?, ?, ?, ?, ?, 1)",
                                (username, email, mobile, grade, datetime.now().strftime('%Y-%m-%d')))
            self.conn.commit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(None, "警告", "用户名或邮箱已存在！")

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
        username = self.username
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        desktop_path = os.path.join(self.home, 'Desktop')
        filename = f"{username}_{current_datetime}.xlsx"
        self.workbook_file = os.path.join(desktop_path, filename)

        self.workbook = xlsxwriter.Workbook(self.workbook_file)
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.worksheet = self.workbook.add_worksheet("答题记录{}".format(current_date))
        # print(self.worksheet)

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
        # print(self.worksheet)
        self.worksheet.write_row(self.current_row, 0, data, self.cell_format)
        self.current_row += 1

    def SaveWorkbook(self):
        if self.workbook:
            self.worksheet.autofilter(0, 0, self.current_row - 1, 8)
            self.workbook.close()

    def GenerateQuestion(self):
        self.q.Generate()
        return (self.q.question, self.q.correct_answer)

    def NextQuestion(self):
        self.current_question, self.correct_answer = self.GenerateQuestion()
        self.start_time = datetime.now()
        return self.current_question

    def SubmitAnswer(self, user_input):
        self.end_time = datetime.now()
        try:
            user_answer = float(user_input)
            if user_answer == int(user_answer):
                user_answer = int(user_answer)
                self.user_answer = user_answer
        except:
            return (False, "请输入有效数字")

        if user_answer == self.correct_answer:
            is_correct = True
        else:
            is_correct = False
        self.time_used = round((self.end_time - self.start_time).total_seconds(), 1)

        self.GenerateTips()
        # print(self.tips)
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
        for k in range(1, n + 1):  # k表示要改变的元素个数，从1到n
            for indices in combinations(range(n), k):  # 生成所有可能的k个元素的索引组合
                new_list = lst.copy()
                for idx in indices:
                    new_list[idx] = -new_list[idx]
                result.append(new_list)
        return result

    def IsSignError(self):

        numbers_list = self.GenerateOppositeLists(self.q.numbers)
        # print(numbers_list)
        user_answer = abs(self.user_answer)
        correct_answer = abs(self.correct_answer)
        # 检查符号
        if user_answer / self.user_answer != correct_answer / self.correct_answer:
            return True
        for numbers in numbers_list:
            q = Question(numbers = numbers, operators = self.q.operators)
            # print(numbers, self.q.operators)
            # print(q.expression, q.correct_answer)
            if q.correct_answer == self.user_answer:
                print(f'{q.expression} = {q.correct_answer}')
                print('1. 检查正负号')
                return True

    def GenerateTips(self):
        if self.user_answer == self.correct_answer:
            return

        print(self.q.expression, self.user_answer, self.correct_answer)
        tips = []
        user_answer = abs(self.user_answer)
        correct_answer = abs(self.correct_answer)
        # 检查符号
        if self.IsSignError():
            tips.append('1. 正负号')
            print('1. 正负号')
        # 检查个位数
        if user_answer % 10 != correct_answer % 10:
            tips.append('2. 个位数')
            print('2. 个位数')
        # 检查总位数
        if len(str(user_answer)) != len(str(correct_answer)):
            tips.append('3. 总位数')
            print('3. 总位数')
        # 检查进借位
        if user_answer // 10 != correct_answer // 10:
            tips.append('4. 进借位')
            print('4. 进借位')

        self.tips = '；'.join(tips)


    def SaveToDatabase(self, question_number, question, user_answer, correct_answer, is_correct, start_time, end_time,
                       time_used, tips):
        # print(tips)
        # 将记录保存到数据库
        self.cursor.execute('''
            INSERT INTO Exam01 (QuestionNumber, Question, UserAnswer, CorrectAnswer, IsCorrect, StartTime, EndTime, TimeUsed, Tips)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (question_number, question, str(user_answer), str(correct_answer), "正确" if is_correct else "错误",
            start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S"), time_used, tips)
        )
        self.conn.commit()

    def CloseDatabase(self):
        # 整理数据表
        self.ReorganizeExamData()
        # 关闭数据库连接
        if self.conn:
            self.conn.close()

    def ReorganizeExamData(self):
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

                # print(current_question, previous_question)
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
            # 获取所有TimeUsed值并排序
            self.cursor.execute("SELECT TimeUsed FROM Exam01 ORDER BY TimeUsed DESC")
            time_used_list = self.cursor.fetchall()
            total_count = len(time_used_list)
            threshold_index = min(int(total_count * 0.1), 50)  # 取前10%的索引
            if threshold_index == 0:
                threshold = float('inf')
            else:
                threshold = time_used_list[threshold_index - 1][0] if time_used_list else float('inf')
            # 筛选TimeUsed大于等于threshold的记录
            self.cursor.execute(f"SELECT * FROM Exam01 WHERE TimeUsed >= {threshold} ORDER BY TimeUsed DESC ")

        data = self.cursor.fetchall()
        rows = len(data)
        cols = len(data[0])
        # print("rows = {}, cols = {}".format(rows, cols))

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
        # cols：增加了一列ID，导出到Excel表没有这列，从0开始计数。
        # rows: 因为增加了一行标题行。
        worksheet.autofilter(0, 0, rows, cols-2)
        workbook.close()