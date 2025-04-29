from question import *
import sqlite3
import os
from datetime import *
import xlsxwriter
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from threading import Thread
import pandas as pd
"""
类名称: Exam
变量: 
os: 操作系统名称
  'nt': Windows
  'posix': 类UNIX操作系统
type: 题目类型
   0: 计算24点
   1: 乘法速算
   2: 四则运算
subtype: 子类型
  乘法速算:
    参数一:
      0: 平方数
      1: 平方差法
      2: 和十速算法
      3: 大数凑十法
      4: 逢五凑十法
      5: 双向凑十法
  四则运算:
    参数一：
      0: 二项式
      1: 三项式 
      2: 四项式
      3: 五项式
    参数二:
      0: 加法
      1: 减法
      2: 乘法
      3: 除法
      4: 混合运算
range: 取值范围
user: 用户对象
setting: 设置对象
record: 答题记录对象
wb: 工作簿对象
mail: 邮件对象
q: Question对象

函数: 
CreateQuestion(): 生成与type相对应的题目类别的对象
Dump(): 输出成员变量及其值
Exit(): 程序退出之前的处理
ExportRecords(): 导出习题记录，包括：习题本、错题本、难题本
Register(): 命令行注册函数
Run(): 命令行模式运行函数
SendDB(): 发送mathdoc.db文件
SendRecords(): 发送答题记录工作部文件
SubmitAnswer(): 提交答案
UpdateSetting(): 更新成员变量的函数
"""
class Exam:
    def __init__(self, type=0, subtype=[0, 0], range=[1, 10]):
        self.type = type
        self.subtype = subtype
        self.range = range
        self.db = Database()
        self.user = User(self.db)
        self.setting = Setting(self.db)
        self.record = Record(self.db)
        self.review = Review(self.db)
        self.wb = Workbook(self.user.username)
        self.mail = Mail()
        self.ReadSetting()
        # self.Dump(self.setting)
        # self.Dump(self)
        self.q = self.CreateQuestion()

    def Dump(self, obj = None):
        if obj == None:
            obj = self
        print()
        print(f'Dumping Object: {obj.__class__.__name__}')
        for name, value in obj.__dict__.items():
            print(f"{type(getattr(obj, name))}: {name}: {value}")
        print()

    def Exit(self):
        self.record.SaveRecords()
        self.SendDB()
        if len(self.record.data):
            self.wb.Save(self.record.data)
            self.SendRecords()

    def ReadSetting(self):
        self.setting.Read()
        self.type = self.setting.type
        if self.type == 0:
            self.range = [1, 10]
        elif self.type == 1:
            self.range = [self.setting.min_divisor, self.setting.max_divisor]
        elif self.type == 2:
            self.range = [self.setting.min_addend, self.setting.max_addend,
                self.setting.min_divisor, self.setting.max_divisor]
        elif self.type == 3:
            self.range = [self.setting.min_composite, self.setting.max_composite]

    def ExportRecords(self, type):
        db = self.db
        path = None
        name = ['习题本', '错题本', '难题本']
        if type < 0 or type > 2:
            return
        else:
            current_date = datetime.now().strftime("%Y%m%d")
            filename = str(name[type])+f'{current_date}.xlsx'
            # print(filename)
            table_name = 'Exam01'
            db.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = db.cursor.fetchall()
            column_names = [column[1] for column in columns]
            selected_columns = column_names[1:]
            query = f"SELECT {', '.join(selected_columns)} FROM {table_name}"
            # print(query)

        if type == 0:
            db.cursor.execute(f"{query}")
        elif type == 1:
            db.cursor.execute(f"{query} WHERE IsCorrect = '错误'")
        elif type == 2:
            db.cursor.execute(f"SELECT TimeUsed FROM {table_name} ORDER BY TimeUsed DESC")
            time_used_list = db.cursor.fetchall()
            total_count = len(time_used_list)
            threshold_index = min(int(total_count * 0.1), 50)
            threshold = time_used_list[threshold_index - 1][0] if time_used_list else 0
            db.cursor.execute(f"{query} WHERE TimeUsed >= {threshold} ORDER BY TimeUsed DESC")
        data = db.cursor.fetchall()
        wb = Workbook(filename = filename)
        wb.Save(data)


    def SendRecords(self):
        print('答题记录发送邮件...')
        local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.mail.subject = f'{self.user.email}在{local_time}发来的作业'
        self.mail.Send(attach=self.wb.fullpath) # 给服务器邮箱发送邮件
        self.mail.Send(receiver=self.user.email, attach=self.wb.fullpath) # 给本人邮箱发送邮件
        if not self.user.mentor_email is None and self.user.mentor_email.find('@'):
            self.mail.Send(receiver=self.user.mentor_email, attach=self.wb.fullpath)  # 给本人邮箱发送邮件
        print('答题记录邮件发送完毕')

    def SendDB(self):
        if not self.db.IsDBSent():
            print('发送DB邮件...')
            current_date = datetime.now().strftime("%Y-%m-%d")
            self.mail.subject = f'{self.user.email}在{current_date}发来的DB'
            self.mail.Send(receiver=self.mail.receiver, attach=self.db.path)
            self.db.AfterSendDB()
            print('DB邮件发送完毕')

    def UpdateSetting(self, type = None, subtype = None, range = None):
        if type is not None: self.type = type
        if subtype is not None: self.subtype = subtype
        if range is not None: self.range = range
        self.q = self.CreateQuestion()

    def CreateQuestion(self):
        # print(self.type, self.subtype, self.range)
        if self.type == 0: # 0: 计算24点
            return Question24Point(subtype=self.subtype, range=self.range)
        elif self.type == 1: # 1: 乘法速算
            return QuestionQC(subtype=self.subtype, range=self.range)
        elif self.type == 2: # 2: 四则运算
            return Question4AO(subtype=self.subtype, range=self.range)
        elif self.type == 3: # 3: 质因数分解
            return QuestionFactor(subtype=self.subtype, range=self.range)
        elif self.type == 4:  # 3: 解方程
            return QuestionEquation(subtype=self.subtype, range=self.range)
        else:
            print(f'{self.type}: 无效的类型')
            return None

    def SubmitAnswer(self):
        q = self.q
        if not q.ProcessUserInput():
            print('无效输入，继续做题')
            return
        if q.JudgeAnswer() == False: # 回答错误
            print('回答错误: 再来一次')
            q.Tips()
            if q.check_tips:
                print(f'检查提示：{q.check_tips}')
            if q.answer_tips:
                print(f'答题提示：{q.answer_tips}')
            print(f'答题结束时间：{q.end_time}, 答题用时：{q.time_used}秒')
            self.record.Append(q)
            if q.error_number >= 3:
                self.Generate()
        else: # 回答正确
            # 所有QuestionLR的题目：self.type == 1 or self.type == 2
            if 'QuestionLR' in q.SuperName():
                print('回答正确: {} = {}'.format(q.expression, q.user_answer))
            else: # 所有QuestionRL的题目：self.type == 0
                if q.__class__.__name__ == 'QuestionFactor':
                    subtype = self.q.subtype[0]
                    if subtype == 0:
                        expr = ' * '.join(map(str, self.q.user_answer))
                        print(f'回答正确: {expr} = {self.q.numbers[0]}')
                    else:
                        print(f'回答正确')
                elif q.__class__.__name__ == 'Question24Point':
                    print('回答正确: {} = {}'.format(q.user_input, q.correct_answer))
            print(f'答题结束时间：{q.end_time}, 答题用时：{q.time_used}秒')
            self.record.Append(q)
            self.record.correct_number += 1
            self.record.question_number += 1

    def Generate(self):
        """
        在已做题目中查重，保证题目不重复
        :return:
        """
        q = self.q
        ql = self.record.question_list
        q.Generate()

        count = 0
        for count in range(1000):
            count += 1
            # print(count)
            if q.question in ql:
                # print(f'{[q.question]} 存在于 {ql} 中')
                q.Generate()
            else:
                # print(f'{[q.question]} 不存在于 {ql} 中')
                return True
        return False

    def Register(self):
        while not self.user.IsCompleted():
            print('请先注册')
            print('输入用户名：')
            username = input()
            print('输入邮箱名：')
            email = input()
            print('输入手机号：')
            mobile = input()
            print('输入年级（1至12）：')
            grade = input()
            self.user.Register(username = username, email = email, mobile = mobile, grade = grade)

    def Run(self):
        self.Register()
        print()
        type = 3
        parms = [{'type': 0, 'subtype': [0], 'range': [1, 10]},
                 {'type': 1, 'subtype': [2, 0], 'range': [10, 50]},
                 {'type': 2, 'subtype': [1, 4], 'range': [-50, 50, 2, 10]},
                 {'type': 3, 'subtype': [0], 'range': [6, 200]},
                 ]
        self.UpdateSetting(parms[type]['type'], parms[type]['subtype'], parms[type]['range'])
        q = self.q
        print(q.name)
        while True:
            print(q.comments)
            print("输入EXIT或QUIT退出程序")
            print(q.start_time)
            print(q.question)
            q.user_input = input()
            upper_input = q.user_input.upper()
            if upper_input == 'EXIT' or upper_input == 'QUIT':
                print('用户退出程序')
                break
            # print(upper_input)
            if upper_input == 'EXPORT0':
                self.ExportRecords(0)
                continue
            elif upper_input == 'EXPORT1':
                self.ExportRecords(1)
                continue
            elif upper_input == 'EXPORT2':
                self.ExportRecords(2)
                continue
            self.SubmitAnswer()
            if self.q.is_correct:
                self.Generate()  # 生成下一题
            print()
        self.Exit() # 处理程序退出的收尾工作，如保存数据，发送邮件。


"""
类名称：User
说明：管理用户相关信息的类
Read(): 从数据库的Users数据表读取到User类的成员变量
Write(): 将User类的成员变量写入到数据库的Users数据表
"""
class User:
    def __init__(self, db):
        self.db = db
        self.userid = None
        self.username = None
        self.email = None
        self.mobile = None
        self.grade = None
        self.register_date = None
        self.is_verified = None
        self.mentor_email = None
        self.expired_date = None

        self.CreateTable()
        self.Read()

    def CreateTable(self):
        db = self.db
        if not db.ExistTable('Users'):
            db.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT UNIQUE,
                Email TEXT UNIQUE,
                Mobile TEXT UNIQUE,
                Grade INTEGER,
                RegisterDate TEXT,
                IsVerified BOOLEAN DEFAULT FALSE,
                MentorEmail TEXT,
                ExpiredDate TEXT
            )
            ''')
            db.connect.commit()
        else:
            db.AddColumn('Users', 'MentorEmail', 'TEXT')
            db.AddColumn('Users', 'ExpiredDate', 'TEXT')


    def Read(self):
        db = self.db
        db.cursor.execute('''SELECT ID, Username, Email, Mobile, Grade, 
                                RegisterDate, IsVerified, MentorEmail,  ExpiredDate
                                FROM Users WHERE IsVerified = 1''')
        result = db.cursor.fetchone()
        if result is not None:
            self.userid = result[0]
            self.username = result[1]
            self.email = result[2]
            self.mobile = result[3]
            self.grade = result[4]
            self.register_date = result[5]
            self.is_verified = result[6]
            self.mentor_email = result[7]
            self.expired_date = result[8]
        return result

    def ReadAll(self):
        db = self.db
        db.cursor.execute('''SELECT ID, Username, Email, Mobile, Grade, 
                                RegisterDate, IsVerified, MentorEmail,  ExpiredDate
                                FROM Users WHERE IsVerified = 1''')
        results = db.cursor.fetchone()
        for result in  results:
            self.userid = result[0]
            self.username = result[1]
            self.email = result[2]
            self.mobile = result[3]
            self.grade = result[4]
            self.register_date = result[5]
            self.is_verified = result[6]
            self.mentor_email = result[7]
            self.expired_date = result[8]
        return results

    def Write(self):
        db = self.db
        try:
            sql = "DELETE FROM Users Where Username = ?"
            db.cursor.execute(sql, (self.username,))
            db.connect.commit()
            db.cursor.execute("""INSERT INTO Users (Username, Email, Mobile, Grade, RegisterDate, 
                                IsVerified, MentorEmail, ExpiredDate) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                (self.username, self.email, self.mobile, self.grade,
                                 self.register_date, self.is_verified, self.mentor_email, self.expired_date))
            db.connect.commit()
        except sqlite3.IntegrityError:
            print("用户名或邮箱已存在！")

    def Register(self, username = None, email = None, mobile = None,
                 grade = None, mentor_email = None):
        if username is not None: self.username = username
        if email is not None: self.email = email
        if mobile is not None: self.mobile = mobile
        if grade is not None: self.grade = grade
        if mentor_email is not None: self.mentor_email = mentor_email
        self.is_verified = True
        self.register_date = datetime.now().strftime('%Y-%m-%d')
        self.expired_date = (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')
        if self.IsCompleted():
            self.Write()

    def IsCompleted(self):
        if self.username is None or self.username == '': return False
        if self.grade is None or self.grade == '': return False
        if self.email is None or self.email == '': return False
        if self.mobile is None or self.mobile == '': return False
        if self.register_date is None or self.register_date == '': return False
        return True

import ast
class Setting:
    def __init__(self, db):
        self.db = db
        self.default = {
            'type': 0,
            'min_24point': 1,
            'max_24point': 10,
            'min_qc': 10,
            'max_qc': 50,
            'type_qc': 0,
            'min_addend': 1,
            'max_addend': 50,
            'min_divisor': 1,
            'max_divisor': 10,
            'sn_term': 0,
            'sn_operator': 0,
            'min_composite': 8,
            'max_composite': 100,
            'factor_type': 0,
            'min_coefficient': -5,
            'max_coefficient': 5,
            'min_constant': -20,
            'max_constant': 20,
            'type_equation': 0,
        }
        self.CreateTable()
        self.Read()

    def CreateTable(self):
        for key, value in self.default.items():
            setattr(self, key, value)
        db = self.db
        if not db.ExistTable('Setting'):
            db.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Setting (
                Key TEXT PRIMARY KEY,
                Value TEXT
            )
            ''')
            db.connect.commit()
            self.Write()

    def Read(self):
        db = self.db
        for key, value in self.default.items():
            db.cursor.execute("SELECT Value FROM Setting WHERE Key = ?", (key,))
            result = db.cursor.fetchone()
            if result == None:
                break
            value = result[0]
            setattr(self, key, int(value))

            if not result:
                self.Write()

    def Write(self):
        db = self.db
        for key in self.default.keys():
            value = str(getattr(self, key))
            db.cursor.execute("INSERT OR REPLACE INTO Setting (Key, Value) VALUES (?, ?)", (key, value))
        db.connect.commit()

"""
类名称：Record
说明：答题记录

变量：
db: 数据库对象，从Exam初始化函数传入db参数
correct_number: 回答正确的题目数量
data: 答题记录列表，元素是每次答题记录构成的元组
question_list: 已做题目的列表，用于后续判断题目是否重复
question_number: 总的题目数量

函数：
CreateTable(): 创建答题记录数据表
Append(): 向记录列表追加记录
SaveRecord(): 将一条答题记录保存到数据表
SaveRecords(): 将所有答题记录保存到答题记录数据表
Reorganize(): 重新整理答题记录数据表，保证题号按照数字顺序写入
"""
class Record:
    def __init__(self, db):
        self.db = db
        self.correct_number = 0
        self.question_number = 1
        self.data = []
        self.question_list = []
        self.table_name = 'Exam01'
        self.CreateTable()

    def CreateTable(self):
        db = self.db
        db.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            QuestionNumber INTEGER,
            Question TEXT,
            UserAnswer TEXT,
            CorrectAnswer TEXT,
            IsCorrect TEXT,
            StartTime TEXT,
            EndTime TEXT,
            TimeUsed REAL,
            Tips TEXT,
            AnswerTips TEXT,
            Solution TEXT,
            Type INTEGER,
            Subtype TEXT,
            Input TEXT
        )
        ''')
        db.AddColumn(self.table_name, 'AnswerTips', 'TEXT')
        db.AddColumn(self.table_name, 'Solution', 'TEXT')
        db.AddColumn(self.table_name, 'Type', 'INTEGER')
        db.AddColumn(self.table_name, 'Subtype', 'TEXT')
        db.AddColumn(self.table_name, 'Input', 'TEXT')
        db.connect.commit()

    def Append(self, q):
        record = (self.question_number, q.question, str(q.user_answer), str(q.correct_answer),
                  "正确" if q.is_correct else "错误",
                  q.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                  q.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                  q.time_used, q.check_tips, q.answer_tips, q.solution,
                  q.type, str(q.subtype),
                  q.user_input)
        self.data.append(record)
        self.question_list.append(q.question)

    def SaveRecords(self):
        db = self.db
        db.cursor.executemany(f'''
            INSERT INTO {self.table_name} (QuestionNumber, Question, UserAnswer, CorrectAnswer, IsCorrect, 
            StartTime, EndTime, TimeUsed, Tips, AnswerTips, Solution, Type, Subtype, Input)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            self.data)
        db.connect.commit()
        self.Reorganize()

    def Reorganize(self):
        db = self.db
        try:
            db.cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY ID")
            data = db.cursor.fetchall()

            if not data:
                print(f"{self.table_name}表中没有数据需要整理")
                return

            new_question_number = 1
            previous_question = data[0][2]

            for row in data:
                current_id = row[0]
                current_question = row[2]
                if current_question != previous_question:
                    new_question_number += 1
                db.cursor.execute(f"UPDATE {self.table_name} SET QuestionNumber = ? WHERE ID = ?", (new_question_number, current_id))
                previous_question = current_question
            db.connect.commit()
        except Exception as e:
            print(f"整理{self.table_name}表数据时出错: {e}")

    def SaveRecord(self, q):
        db = self.db
        db.cursor.execute(f'''
            INSERT INTO {self.table_name} (QuestionNumber, Question, UserAnswer, CorrectAnswer, IsCorrect, 
            StartTime, EndTime, TimeUsed, Tips, AnswerTips, Solution, Type, Subtype, Input)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (self.question_number, q.question, str(q.user_answer), str(q.correct_answer), "正确" if q.is_correct else "错误",
             q.start_time.strftime("%Y-%m-%d %H:%M:%S"), q.end_time.strftime("%Y-%m-%d %H:%M:%S"),
             q.time_used, q.check_tips, q.answer_tips, q.solution,
             q.type, str(q.subtype),
             q.user_input)
        )
        db.connect.commit()

class Database:
    def __init__(self):
        # 初始化 SQLite 数据库
        self.path = None
        self.connect = None
        self.cursor = None
        self.InitDB()

    def InitDB(self):
        home = os.path.expanduser("~")
        desktop = os.path.join(home, "Desktop")
        db_folder = os.path.join(desktop, ".mathdoc")
        if not os.path.exists(db_folder):
            os.mkdir(db_folder)
        self.Hide(db_folder)
        self.path = os.path.join(db_folder, "mathdoc.db")
        self.connect = sqlite3.connect(self.path)
        self.cursor = self.connect.cursor()
        self.CreateMailTable()

    def Hide(self, path):
        # 设置文件或目录为隐藏
        if os.name == 'nt':
            try:
                os.system(f'attrib +h "{path}"')
                print(f"{path} 已被隐藏")
            except Exception as e:
                print(f"隐藏文件或目录时出错：{e}")

    def ExistTable(self, table_name):
        # 查询 sqlite_master 表，检查是否存在指定的表格
        self.cursor.execute(f"""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))

        result = self.cursor.fetchone()
        return result is not None

    def ShowTables(self):
        cursor = self.cursor
        # 查询 sqlite_master 表，获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        # 获取查询结果
        tables = cursor.fetchall()
        # 打印所有表名
        print("数据库中的表：")
        for table in tables:
            print(f'  {table[0]}')

    def AddColumn(self, table_name, column_name, column_type):
        if table_name is None or column_name is None or column_type is None:
            print(f'table_name = {table_name}, column_name = {column_name}, column_type = {column_type}')
            return

        try:
            self.cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};')
            self.connect.commit()
            print(f"字段 '{column_name}' 添加成功！")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                # print(f"字段 '{column_name}' 已经存在，无需添加。")
                pass
            else:
                print(f"添加字段时出错: {e}")

    def CreateMailTable(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Mail (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT,
            Submit BOOLEAN
        )
        ''')
        self.connect.commit()

    def AfterSendDB(self):
        if not self.IsDBSent():
            today = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("INSERT INTO Mail (Date, Submit) VALUES (?, ?)", (today, True))
            self.connect.commit()

    def IsDBSent(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("SELECT * FROM Mail WHERE Date = ? AND Submit = ?", (today, True))
        result = self.cursor.fetchone()
        return result is not None

"""
类名称: Workbook
说明: 处理工作簿相关事项

变量：
path: 保存工作部文件的文件夹的完整路径

函数：
Open(): 打开工作簿
Close(): 关闭工作簿
Save(): 保存工作簿
SaveRecords(): 保存所有答题记录
"""
class Workbook:
    def __init__(self, username = None, filename = None):
        self.username = username
        self.home = os.path.expanduser("~")
        self.desktop = os.path.join(self.home, "Desktop")
        self.path = os.path.join(self.desktop, "答题记录")
        self.filename = filename
        self.fullpath = None
        self.workbook = None
        self.worksheet = None
        self.max_rows = 65536 # xlsx工作表共有2^20 = 1048576行
        self.max_cols = 1024 # xlsx工作表共有2^14 = 16384列
        self.row_height = 25
        self.column_widths = [10, 40, 15, 15, 15, 25, 25, 15, 40, 40]
        self.zoom = 120 # 放大系数：120%
        self.title = ('题号', '题目', '用户答案', '正确答案', '是否正确',
            '开始时间', '结束时间', '用时(秒)', '检查提示', '答题提示')
        self.cell_format = {
            "bg_color": "#FFFFFF",
            "border": 1,
            "border_color": "black",
            "align": "center",
            "valign": "vcenter",
            "font_size": "12",
        }
        self.full_format = {
            "bg_color": "#FFFFFF",
            "align": "center",
            "valign": "vcenter",
            "font_size": "12",
        }
        self.Open()

    def Open(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        else:
            # print(f'"{self.path}"目录已存在')
            pass
        if self.filename is None:
            current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filename = f"{self.username}_{current_datetime}.xlsx"
        self.fullpath = os.path.join(self.path, self.filename)

        self.workbook = xlsxwriter.Workbook(self.fullpath)
        self.worksheet = self.workbook.add_worksheet("答题记录")

        full_format = self.workbook.add_format(self.full_format)
        self.worksheet.set_column(0, self.max_cols, None, full_format)
        for col in range(len(self.title)):
            self.worksheet.set_column(col, col, self.column_widths[col], full_format)
        self.worksheet.set_zoom(self.zoom) # 工作表放大
        for row in range(0, self.max_rows):
            self.worksheet.set_row(row, self.row_height) # 设置行高
        self.Append(0, self.title)
        self.worksheet.freeze_panes(1, 1)

    def Append(self, row, row_data):
        cell_format = self.workbook.add_format(self.cell_format)
        self.worksheet.write_row(row, 0, row_data, cell_format)

    def SaveRecords(self, data):
        row = 1
        for row_data in data:
            self.Append(row, row_data[:-4])
            row += 1

    def Save(self, data):
        rows = len(data)
        if self.workbook and rows:
            self.SaveRecords(data)
            self.worksheet.autofilter(0, 0, rows, len(self.title)-1)
            self.workbook.close()

class Mail():
    def __init__(self):
        self.receiver = "mathdb@163.com"
        self.sender = "mathdoc@163.com"
        self.authority = "466066c2a4aac05abcc0c4aacc845e68"
        self.subject = "数字博士作业"            # 邮件主题
        self.body = "数字博士作业，包含一个附件。"  # 邮件正文
        # 设置163邮箱的SMTP服务器和端口
        self.server = 'smtp.163.com'
        self.port = 465  # 163邮箱使用SSL加密
        self.home = os.path.expanduser("~")
        self.desktop = os.path.join(self.home, "Desktop")
        self.database = os.path.join(self.desktop, ".mathdoc", "mathdoc.db")  # 附件文件路径

    def Send(self, receiver=None, attach=None):
        self.ThreadSend(receiver=receiver, attach=attach)

    def ThreadSend(self, receiver=None, attach=None):
        # 创建MIMEMultipart对象
        msg = MIMEMultipart()
        msg['From'] = self.sender
        if receiver is None:
            receiver = self.receiver
        msg['To'] = receiver
        msg['Subject'] = self.subject

        # 添加邮件正文
        if self.body is not None:
            msg.attach(MIMEText(self.body, 'plain'))

        # 添加附件
        if os.name == 'posix':
            sep = '/'
        if os.name == 'nt':
            sep = '\\'
        if attach is not None:
            try:
                with open(attach, "rb") as attachment:
                    part = MIMEApplication(attachment.read(), Name=attach.split(sep)[-1])
                    part['Content-Disposition'] = f'attachment; filename="{attach.split(sep)[-1]}"'
                    msg.attach(part)
            except Exception as e:
                print(f"附件读取错误: {e}")
                return False
        try:
            # 创建SMTP会话
            server = smtplib.SMTP_SSL(self.server, self.port)  # 使用SSL加密
            server.login(self.sender, self.Decode(self.authority))  # 登录SMTP服务器
            server.sendmail(self.sender, receiver, msg.as_string())  # 发送邮件
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
        finally:
            server.quit()

    def SendDB(self):
        try:
            self.Send(attach=self.database)
        except Exception as e:
            print(e)

    def SendVCode(self):
        self.subject = '验证码'
        self.body = '验证码：' + str(random.randint(100000, 999999))
        self.receiver = 'sunsdbh@126.com'
        self.Send()

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
        m.Send()

class Review:
    def __init__(self, db):
        self.db = db
        self.df = None
        self.data = []
        self.table_name = 'Exam01'
        self.CompleteTable()

    def Read(self):
        pass

    def CompleteTable(self):
        self.df = pd.read_sql_query(f"SELECT * FROM {self.table_name} LIMIT 1;", self.db.connect)
        if self.df.empty: # 空表格
            print(f'Exam01表格不存在或为空表')
            return
        # if not pd.isna(self.df.loc[0]['Type']) or not pd.isna(self.df.loc[0]['Subtype']):
        #     print('Exam01数据表的记录类型、子类型完整')
        #     return
        self.df = pd.read_sql_query(f"SELECT * FROM {self.table_name};", self.db.connect)
        self.df['Question'] = self.df['Question'].str.replace('24点', '计算24点')
        self.df['Question'] = self.df['Question'].str.replace('计算计算24点', '计算24点')
        for index, row in self.df.iterrows():
            question = row['Question']
            type, subtype = self.JudgeType(question)
            self.df.at[index, 'Type'] = type
            self.df.at[index, 'Subtype'] = str(subtype)
        # print(self.df.to_string())
        # self.data = [tuple(row) for row in self.df.itertuples(index=False)] # 是否带索引列
        self.data = [tuple(row.values) for _, row in self.df.iterrows()] # 另一种方法导出所有行的数据，忽略索引列
        # for row in self.data:
        #     print(row)
        # 将结果写回数据库
        try:
            self.db.connect.commit()  # 提交之前的事务
            for index, row in self.df.iterrows():
                update_sql = f"""
                UPDATE {self.table_name}
                SET Type = ?, Subtype = ?
                WHERE ID = ?;
                """
                self.db.cursor.execute(update_sql, (row['Type'], row['Subtype'], row['ID']))
            self.db.connect.commit()
            print("数据更新成功")
        except sqlite3.Error as e:
            print(f"数据库错误：{e}")
            self.db.connect.rollback()  # 回滚事务
        finally:
            # pass
            # 重新从数据库读取数据以验证更新是否成功
            self.df = pd.read_sql_query(f"SELECT * FROM {self.table_name};", self.db.connect)
            # print(self.df.to_string())

    def JudgeType(self, question):
        type = 0
        subtype = []
        opr = 0
        sum = []
        pattern_qc = re.compile(r'^\d+ × \d+ = $')  # 匹配'数字 × 数字 = '格式的正则表达式
        q = question.replace(' ', '').replace('=', '').replace('(-', '').replace(')', '')
        q = q.replace('×', ' ').replace('÷', ' ').replace('/', ' ').replace('+', ' ').replace('-', ' ')
        q = q.replace('  ', ' ')
        numbers = q.split(' ')
        # print(numbers)
        if question.replace('(-', '').find('+') >= 0:
            opr = 0
            sum.append(opr)
        if question.replace('(-', '').find('-') >= 0:
            opr = 1
            sum.append(opr)
        if question.replace('(-', '').find('×') >= 0:
            opr = 2
            sum.append(opr)
        if question.replace('(-', '').find('÷') >= 0:
            opr = 3
            sum.append(opr)
        if question.replace('(-', '').find('/') >= 0:
            opr = 3
            sum.append(opr)
        # print(f'{question}: sum = {sum}, len(sum) = {len(sum)}')
        if question.startswith('计算24点'):
            type = 0
            subtype = [0]
        elif question.startswith('质因数分解'):
            type = 3
            subtype = [0]
        elif question.startswith('求最大公约数'):
            type = 3
            subtype = [1]
        elif question.startswith('求最小公倍数'):
            type = 3
            subtype = [2]
        elif pattern_qc.match(question):
            type = 1
            a = int(numbers[0])
            b = int(numbers[1])
            if a == b:
                subtype = [0]
            elif a // 10 == b // 10:
                subtype=[2]
            elif abs(a // 10 - b // 10) == 1 and ((a+b)/2 % 5 == 0 or (a+b)/2 % 10 == 0):
                subtype=[1]
            elif a % 2 == 0 and b % 5 == 0 or a % 5 == 0 and b % 2 == 0:
                subtype = [4]
            elif a % 10 in [7, 8, 9] and b % 10 in [1, 2, 3] or b % 10 in [7, 8, 9] and a % 10 in [1, 2, 3]:
                subtype = [5]
            elif a % 10 in [7, 8, 9] or b % 10 in [7, 8, 9]:
                subtype = [3]
        else:
            type = 2
            subtype = [len(numbers) - 2, opr if len(sum) == 1 else 4] # 项数
        return type, subtype
"""
测试代码
"""
if __name__ == "__main__":
    exam = Exam()
    exam.Run()
