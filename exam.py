import datetime

from question import *
import sqlite3
import os
from datetime import *
"""
类名称: Exam
变量: 
type: 题目类型
   0: 24点游戏
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
      2: 二项式
      3: 三项式 
      4: 四项式
      5: 五项式
    参数二:
      0: 加法
      1: 减法
      2: 乘法
      3: 除法
      4: 混合运算
range: 取值范围
q: Question对象

函数: 
CreateQuestion(): 生成与type相对应的题目类别的对象
Update(): 更新成员变量的函数
SubmitAnswer(): 提交答案
Test(): 测试函数

"""
class Exam:
    def __init__(self, type=0, subtype=[0], range=[1, 10]):
        self.type = type
        self.subtype = subtype
        self.range = range
        self.db = Database()
        self.user = User()
        self.q = self.CreateQuestion()
        self.user.Read(self.db)
        self.user.Write(self.db)

    def Dump(self, obj = None):
        if obj == None:
            obj = self
        print()
        print(f'Dumping Object: {obj.__class__.__name__}')
        for name, value in obj.__dict__.items():
            print(f"{name}: {value}")
        print()


    def Update(self, type = None, subtype = None, range = None):
        if type is not None: self.type = type
        if subtype is not None: self.subtype = subtype
        if range is not None: self.range = range
        self.q = self.CreateQuestion()

    def CreateQuestion(self):
        if self.type == 0: # 0: 24点游戏
            return Question24Point(range=self.range)
        elif self.type == 1: # 1: 乘法速算
            return QuestionQC(subtype=self.subtype, range=self.range)
        elif self.type == 2: # 2: 四则运算
            return Question4AO(subtype=self.subtype, range=self.range)
        else:
            print(f'{self.type}: 无效的类型')
            return None

    def SubmitAnswer(self, user_input):
        q = self.q
        if not q.ProcessUserInput():
            print('无效输入，继续做题')
            return
        if q.JudgeAnswer() == False: # 回答错误
            print('回答错误: 再来一次')
            q.Tips()
            if q.check_tips is not None:
                print(f'检查提示：{q.check_tips}')
            if q.answer_tips is not None:
                print(f'答题提示：{q.answer_tips}')
            print(f'答题结束时间：{q.end_time}, 答题用时：{q.used_time}秒')
        else: # 回答正确
            # 所有QuestionLR的题目：self.type == 1 or self.type == 2
            if 'QuestionLR' in q.SuperName():
                print('回答正确: {} = {}'.format(q.expression, q.user_answer))
            else: # 所有QuestionRL的题目：self.type == 0
                print('回答正确: {} = {}'.format(q.user_input, q.correct_answer))
            print(f'答题结束时间：{q.end_time}, 答题用时：{q.used_time}秒')
            q.Generate()  # 生成下一题

    def Run(self):
        print()
        type = 1
        parms = [{'type': 0, 'subtype': [], 'range': [1, 10]},
                 {'type': 1, 'subtype': [2], 'range': [10, 50]},
                 {'type': 2, 'subtype': [1, 4], 'range': [-50, 50, 2, 10]},
                 ]
        self.Update(parms[type]['type'], parms[type]['subtype'], parms[type]['range'])
        q = self.q
        print(q.name)
        # 初始化题目
        if q.Generate() == False:
            return
        # q.Dump()
        while True:
            print(q.comments)
            print("输入EXIT或QUIT退出程序")
            print(q.start_time)
            print(q.question)
            q.user_input = input()
            if q.user_input.upper() == 'EXIT' or q.user_input.upper() == 'QUIT':
                print('用户退出程序')
                break
            self.SubmitAnswer(q.user_input)
            print()


"""
类名称：User
说明：管理用户相关信息的类
Read(): 从数据库的Users数据表读取到User类的成员变量
Write(): 将User类的成员变量写入到数据库的Users数据表
"""
class User:
    def __init__(self):
        self.userid = None
        self.username = None
        self.email = None
        self.mentor_email = None
        self.mobile = None
        self.grade = None
        self.register_date = None
        self.is_verified = None
        self.expired_date = None

    def CreateTable(self, db):
        cursor = db.cursor
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT UNIQUE,
            Email TEXT UNIQUE,
            Mobile TEXT UNIQUE,
            Grade INTEGER,
            RegisterDate TEXT,
            IsVerified BOOLEAN DEFAULT 0,
            MentorEmail TEXT,
            ExpiredDate TEXT
        )
        ''')
        db.AddColumn('Users', 'MentorEmail', 'TEXT')
        db.AddColumn('Users', 'ExpiredDate', 'TEXT')
        db.connect.commit()

    def Read(self, db):
        cursor = db.cursor
        cursor.execute('''SELECT ID, Username, Email, Mobile, Grade, 
                                RegisterDate, IsVerified, MentorEmail,  ExpiredDate
                                FROM Users WHERE IsVerified = 1''')
        result = cursor.fetchone()
        if result is not None:
            self.userid = result[0]
            self.username = result[1]
            self.email = result[2]
            self.mobile = result[3]
            self.grade = result[4]
            self.register_date = result[5]
            self.register_date = result[6]
            self.is_verified = result[7]
            self.expired_date = result[8]
        return result

    def Write(self, db):
        cursor = db.cursor
        try:
            sql = "DELETE FROM Users Where Username = ?"
            cursor.execute(sql, (self.username,))
            db.conn.commit()
            cursor.execute("""INSERT INTO Users (Username, Email, Mobile, Grade, RegisterDate, IsVerified, MentorEmail, ExpiredDate) 
                                VALUES (?, ?, ?, ?, ?, 1, ?, ?)""",
                                (self.username, self.email, self.mobile, self.grade,
                                 datetime.now().strftime('%Y-%m-%d'), 'gnunoi@163.com',
                                 (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')))
            db.conn.commit()
        except sqlite3.IntegrityError:
            print("用户名或邮箱已存在！")

class Setting:
    def __int__(self):
        self.type = 0 # 题目类型
        self.subtype = [2, 0] # 题目子类型
        self.min_addend = 1 # 加数最小值
        self.max_addend = 50 # 加数最大值
        self.min_divisor = 1 # 除数最小值
        self.max_divisor = 10 # 除数最大值

    def Read(self):
        pass

    def Write(self):
        pass

class Database:
    def __init__(self):
        # 初始化 SQLite 数据库
        self.home = os.path.expanduser("~")
        # print(f'home direcotry: {self.home}')
        self.path = None
        self.connect = None
        self.cursor = None
        self.InitDB()

    def InitDB(self):
        desktop_path = os.path.join(self.home, "Desktop")
        db_folder = os.path.join(desktop_path, ".mathdoc")
        if not os.path.exists(db_folder):
            os.mkdir(db_folder)
        self.Hide(db_folder)
        self.path = os.path.join(db_folder, "mathdoc.db")
        # print(f'Database file: {self.path}')
        self.connect = sqlite3.connect(self.path)
        self.cursor = self.connect.cursor()
        self.CreateUsersTable()
        self.CreateSettingsTable()
        self.CreateExamTable()
        self.CreateMailTable()
        # self.ShowTables()

    def Hide(self, path):
        # 设置文件或目录为隐藏
        if os.name == 'nt':
            try:
                os.system(f'attrib +h "{path}"')
                print(f"{path} 已被隐藏")
            except Exception as e:
                print(f"隐藏文件或目录时出错：{e}")

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
            Tips TEXT,
            AnswerTips, TEXT,
            Solution, TEXT
        )
        ''')
        self.AddColumn('Exam01', 'AnswerTips', 'TEXT')
        self.AddColumn('Exam01', 'Solution', 'TEXT')
        self.connect.commit()

    def CreateSettingsTable(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Settings (
            Key TEXT PRIMARY KEY,
            Value TEXT
        )
        ''')
        self.connect.commit()

    def CreateMailTable(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Mail (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT,
            Submit BOOLEAN
        )
        ''')
        self.connect.commit()

"""
测试代码
"""
if __name__ == "__main__":
    exam = Exam()
    exam.Run()