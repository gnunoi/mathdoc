import decimal
import random
import secrets
import itertools
import re
from fractions import Fraction
from datetime import datetime
from itertools import combinations
import sympy as sp
import math
import time
import os
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication)

dpi = 0
base_font_size = 0
def GetFontSize():
    global dpi
    global base_font_size
    if dpi > 0 and base_font_size > 0:
        return int(dpi), base_font_size
    primary_screen = QApplication.primaryScreen()
    physical_size = primary_screen.physicalSize()
    scale_factor = primary_screen.devicePixelRatio()
    screen_geometry = primary_screen.geometry()
    ppi = screen_geometry.width() / physical_size.width() * 25.4
    dpi = ppi * scale_factor
    # print(physical_size.width(), physical_size.height(), scale_factor, screen_geometry.width(), screen_geometry.height())
    if screen_geometry.width() <= 1024:
        base_font_size = 12
        big_font_size = 18
        huge_font_size = 20
    elif screen_geometry.width() <= 1600:
        base_font_size = 18
        big_font_size = 28
        huge_font_size = 32
    elif screen_geometry.width() <= 2048:
        base_font_size = 24
        big_font_size = 36
        huge_font_size = 40
    elif screen_geometry.width() <= 3072:
        base_font_size = 36
        big_font_size = 54
        huge_font_size = 60
    else:
        base_font_size = 54
        big_font_size = 80
        huge_font_size = 90
    # DJF
    if False:
        base_font_size = 54
    return int(dpi), base_font_size

"""
类名称: Question
说明：各种题目的基础类

变量: 
answer_tips: 答题提示
check_tips: 检查提示
comments: 答题说明
correct_answer: 正确答案
end_time: 答题结束时间
error_number: 答错次数
expression: 题目的表达式
is_correct: 答题是否正确
name: 题目类型名称
numbers: 操作数的数组
operators: 运算符的数组
question: 题目的题干
range: 取值范围
solution: 各种解法
start_time: 答题开始时间
subtype: 数组，分别是题目子类型及更详细的分类
time_used: 解题所用时间
type: 题目类型编号
user_input: 用户输入的原始答案
user_answer: 最后一个等于号之后的用户答案
user_results: 列表，包括两个元素，计算user_answer和转化为分数之后的user_answer的结果

函数: 
Dump(): 输出所有成员
RandInt(a, b): 随机生成整数a到b之间的整数
Generate(): 生成完整的新题目，包括实例、题干、大难
BeforeGenerate(): 生成前处理
AfterGenerate(): 生成后处理
Question(): 根据现有的题目，生成完整的题干
Answer(): 根据现有的题目，生成正确答案
JudgeAnswer(): 判断用户答案是否正确
BeforeJudgeAnswer(): 判题前处理
Tips(): 生成检查提示与答题提示
CheckTips(): 生成检查提示
AnswerTips(): 生成检查提示
ClassName(): 返回类的名称
SuperName(): 返回父类的名称


Fraction(): 将表达式中的数字替换为分数，确保计算严格准确
ProcessUserInput(): 处理用户输入，将中文符号替换为英文符号，删除空白符
CheckUserInput(): 检查用户输入的表达式是否包含了全部数字
ProcessCalculation(): 显示完整的计算步骤

ClassName(): 获取类名称
SuperName(): 获取父类名称
"""
class Question():
    def __init__(self, type=0, subtype=[0], range=[1, 10]):
        self.answer_tips = ''
        self.check_tips = ''
        self.correct_answer = ''
        self.comments = ''
        self.end_time = ''
        self.error_number = 0
        self.expression = ''
        self.is_correct = False
        self.name = ''
        self.numbers = []
        self.operators = []
        self.question = ''
        self.range = range
        self.start_time = ''
        self.solution = ''
        self.subtype = subtype
        self.subtype2 = subtype
        self.time_used = ''
        self.type = type
        self.user_input = ''
        self.user_answer = ''
        self.user_results = []
        self.try_numbers = 1000
        self.path = self.GetPath()
        self.png_file = os.path.join(self.path, 'question.png')
        self.primes = [
            2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
            53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107,
            109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167,
            173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229
        ]

    def GetPath(self):
        home = os.path.expanduser("~")
        desktop = os.path.join(home, "Desktop")
        folder = os.path.join(desktop, ".mathdoc")
        return folder

    def ClassName(self):
        return self.__class__.__name__

    def SuperName(self):
        parent_names = [base.__name__ for base in self.__class__.__bases__]
        return parent_names

    def Dump(self):
        print()
        print(f'Dumping Object: {self}')
        for name, value in self.__dict__.items():
            print(f"{name}: {value}")
        print()

    def RandInt(self, a, b):
        seed = int(time.time() * 1000000)
        if a > b:
            secrets_rand = secrets.randbelow(a - b + 1) + b
        else:
            secrets_rand = secrets.randbelow(b - a + 1) + a
        random_number = (seed + secrets_rand) % (b - a + 1) + a
        return random_number

    def GCD(self, a, b):
        while b:
            a, b = b, a % b
        return a

    def LCM(self, a, b):
        return a * b // self.GCD(a, b)

    def Latex2PNG(self, latex_formula, output_file, margin=0.5):
        dpi, font_size = GetFontSize()
        dpi *= 1.2
        # print(dpi, font_size)
        plt.rcParams['font.sans-serif'] = ['Arial']  # 用来正常显示中文标签
        fig = plt.figure(figsize=(1, 1))  # 初始尺寸，后续会自动调整
        # 在图形上添加文本（LaTeX 公式）
        text = fig.text(0, 0, latex_formula, fontdict={'size': font_size})
        # text = fig.text(0, 0, latex_formula, fontdict={'size': 60})
        # 自动调整布局，增加边距
        fig.tight_layout(pad=margin)
        # 保存图形为 PNG 文件，自动调整图片大小，背景透明
        fig.savefig(output_file, dpi=dpi, format='png', transparent=True, bbox_inches='tight')
        # 关闭图形，释放资源
        plt.close(fig)

    def BeforeGenerate(self):
        """
        以下变量不能重新初始化
        comments
        name
        type
        subtype
        range
        """
        self.answer_tips = ''
        self.check_tips = ''
        self.correct_answer = ''
        # self.comments = ''
        self.end_time = ''
        self.error_number = 0
        self.expression = ''
        self.is_correct = False
        self.name = ''
        self.numbers = []
        self.operators = []
        self.question = ''
        self.start_time = ''
        self.solution = ''
        self.time_used = ''
        self.user_input = ''
        self.user_answer = ''
        self.user_results = []

    def Generate(self):
        pass

    def AfterGenerate(self):
        self.start_time = datetime.now()
        self.error_number = 0

    def Question(self):
        pass

    def Answer(self):
        pass

    def CheckTips(self):
        pass

    def AnswerTips(self):
        pass

    def Tips(self):
        self.CheckTips()
        self.AnswerTips()

    def BeforeJudgeAnswer(self):
        self.check_tips = ''
        self.answer_tips = ''
        self.solution = ''
        self.is_correct = False
        self.end_time = datetime.now()
        self.time_used = round((self.end_time - self.start_time).total_seconds(), 1)

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        self.end_time = datetime.now()
        self.time_used = round((self.end_time - self.start_time).total_seconds(), 1)
        if self.correct_answer in [self.user_answer] + self.user_results:
            self.is_correct = True
            return True
        else:
            self.is_correct = False
            self.error_number += 1
            return False

    def Fraction(self, expression):
        # 使用正则表达式匹配表达式中的数字（包括整数、浮点数和科学计数法）
        pattern = r'(?<!\w)(-?\d+\.?\d*|\.\d+)([eE][-+]?\d+)?(?!\w)'

        # 替换每个数字为 Fraction(数字)
        def replace_with_fraction(match):
            number = match.group(0)
            return f"Fraction('{number}')"

        new_expression = re.sub(pattern, replace_with_fraction, expression)
        return new_expression

    def ProcessUserInput(self):
        replace_map = {
            "（": "(", "）": ")", "[": "(", "]": ")", "{": "(", "}": "(", "【": "(", "】": ")",
            "＋": "+", "➕": "+", "➖": "-", "×": "*", "✖": "*", "÷": "/",
        }
        user_input = self.user_input.strip()
        # print(user_input)
        if user_input == '':
            return False
        for old, new in replace_map.items():
            user_input = user_input.replace(old, new)
        user_input = user_input.split('=')[-1]
        self.user_answer = user_input
        self.user_results = []
        try:
            result = eval(self.user_answer)
            self.user_results.append(result)
            result = eval(self.Fraction(self.user_answer))
            self.user_results.append(result)
        except:
            pass
        # print(self.user_results)
        return True

    def ProcessCalculation(self):
        print(self.expression)
        return

    def Fraction2Latex(self, frac):
        # 判断输入是否为Fraction
        if not isinstance(frac, Fraction):
            return frac
        numerator = frac.numerator
        denominator = frac.denominator

        # 处理分母为1的特殊情况
        if denominator == 1:
            return str(numerator)

        # 将负号放在分数线前面
        if numerator < 0:
            return r"-" + r"\dfrac{" + str(-numerator) + "}{" + str(denominator) + "}"
        else:
            return r"\dfrac{" + str(numerator) + "}{" + str(denominator) + "}"

    def HasDuplicates(self, numbers):
        has_duplicates = False
        for num in numbers:
            # print(num, numbers.count(num))
            if numbers.count(num) > 1:
                has_duplicates = True
                break
        return has_duplicates

    def PrimeFactors(self, num):
        """返回n的质因数分解结果"""
        factors = []
        # 处理2的因子
        while num % 2 == 0:
            factors.append(2)
            num = num // 2

        # 处理奇数因子
        i = 3
        while i * i <= num:
            while num % i == 0:
                factors.append(i)
                num = num // i
            i += 2

        # 如果剩余的n是质数
        if num > 1:
            factors.append(num)
        return factors

    def GetFactors(self, num):
        factors = []
        for i in range(1, int(num ** 0.5) + 1):
            if num % i == 0:
                factors.append(i)
                if i != num // i:  # 避免添加重复的因数（当数是平方数时）
                    factors.append(num // i)
        factors.sort()  # 对因数列表进行排序
        return factors

    def StrNumber(self, num):
        if num >= 0:
            return f'{num}'
        else:
            return f'({num})'

"""
类名称：QuestionRL
题目类型：从右向左求值，即答案是表达式，题目是数值
"""
class QuestionRL(Question):
    def __init__(self, type = 0, subtype = [], range = []):
        super().__init__(type = type, subtype = subtype, range = range)
        self.type = type
        self.subtype = subtype
        self.range = range

"""
类名称: QuestionFactor
题目类型: 质因数分解

成员函数：
IsPrime(): 判断是否为质数
PrimeFactors(): 返回质因数组成的列表
"""
class QuestionFactor(QuestionRL):
    def __init__(self, subtype = [0], range = [8, 50]):
        super().__init__(type=3, subtype = subtype, range = range)
        self.name = "质因数分解"
        self.comments = ""

    def IsPrime(self, num):
        """判断一个数是否为质数"""
        if num <= 1:
            return False
        if num <= 3:
            return True
        if num % 2 == 0:
            return False
        i = 3
        while i * i <= num:
            if num % i == 0:
                return False
            i += 2
        return True

    def Generate(self):
        """生成一个10到1000之间的随机数，保证有至少3个质因数"""
        # print(f'self.subtype = {self.subtype}')
        subtype = self.subtype[0]
        self.error_number = 0
        # print(f'subtype = {subtype}')
        if subtype == 0: # 质因数分解
            self.comments = "分解质因数（用空格或*分隔质因数），如：72，输入：2 2 2 3 3 或：72 = 2 * 2 * 2 * 3 * 3"
            self.GenerateQFactor()
        elif subtype == 1: # 最大公约数
            self.comments = "求最大公约数，如：24, 32，输入：8，或：24 = 8 * 3, 32 = 8 * 4, = 8"
            self.GenerateGCD()
        elif subtype == 2: # 最小公倍数
            self.comments = "求最小公倍数，如：24, 40，输入：120，或：24 = 8 * 3, 40 = 8 * 5, = 8 * 3 * 5 = 40 * 3 = 120"
            self.GenerateLCM()
        self.start_time = datetime.now()
        print(self.question)

    def GenerateComposite(self):
        min = self.range[0]
        max = self.range[1]
        while True:
            num = random.randint(min, max)
            factors = sorted(self.PrimeFactors(num))
            if len(factors) >= 2:
                return num

    def GenerateLCM(self): # 最小公倍数
        self.numbers = []
        gcd = random.randint(5, 20)
        divisor1 = random.randint(2, 10)
        divisor2 = random.randint(2, 10)
        while self.GCD(divisor1, divisor2) > 1:
            divisor2 = random.randint(2, 10)
        # print(prime1, prime2)
        num1 = gcd * divisor1
        num2 = gcd * divisor2
        self.numbers.append(num1)
        self.numbers.append(num2)
        self.correct_answer = gcd * divisor1 * divisor2
        self.question = f'求最小公倍数：{self.numbers[0]}, {self.numbers[1]}'

    def GenerateGCD(self): # 最大公约数
        self.numbers = []
        while True:
            a = self.GenerateComposite()
            b = self.GenerateComposite()
            gcd = self.GCD(a, b)
            if a != b and gcd > 1:
                break
        self.numbers.append(a)
        self.numbers.append(b)
        self.question = f'求最大公约数：{self.numbers[0]}, {self.numbers[1]}'
        self.correct_answer = gcd


    def GenerateQFactor(self):
        self.numbers = []
        self.numbers.append(self.GenerateComposite())
        self.correct_answer = sorted(self.PrimeFactors(self.numbers[0]))
        self.question = f'质因数分解：{self.numbers[0]}'

    def BeforeJudgeAnswer(self):
        subtype = self.subtype[0]
        try:
            if subtype == 0:
                self.user_answer = self.user_answer.strip().replace('*', ' ')
                self.user_answer = self.user_answer.replace(',', '')
                self.user_answer = self.user_answer.replace('，', '')
                self.user_answer = self.user_answer.split()
                print(self.user_answer)
                for i in range(len(self.user_answer)):
                    self.user_answer[i] = int(self.user_answer[i])
            else:
                self.user_answer = self.user_input.strip().replace('*', ' ')
                self.user_answer = self.user_answer.replace(',', ' ')
                self.user_answer = self.user_answer.replace('，', ' ')
                self.user_answer = self.user_answer.replace(' ', '=')
                self.user_answer = self.user_answer.split('=')[-1]
                self.user_answer = int(self.user_answer)
        except:
            print(f'{self.user_answer}含有无效信息')

    def JudgeAnswer(self):
        super().BeforeJudgeAnswer()
        self.BeforeJudgeAnswer()
        self.end_time = datetime.now()
        self.time_used = round((self.end_time - self.start_time).total_seconds(), 1)

        subtype = self.subtype[0]
        if subtype == 0:
            return self.JudgeAnswerQFactor()
        else:
            self.is_correct = self.user_answer == self.correct_answer
            return self.is_correct

    def JudgeAnswerQFactor(self):
        if sorted(self.user_answer) == self.correct_answer:
            self.is_correct = True
        else:
            self.is_correct = False
            self.error_number += 1
        return self.is_correct

    def CheckTips(self):
        subtype = self.subtype[0]
        if subtype == 0:
            self.CheckTipsQFactor()
        elif subtype == 1:
            a = self.numbers[0]
            b = self.numbers[1]
            gcd = self.correct_answer
            err = f'{a} = {gcd} * {a // gcd}；'
            err += f'{b} = {gcd} * {b // gcd}'
            # print(err)
            self.check_tips = f'{err}'
        elif subtype == 2:
            a = self.numbers[0]
            b = self.numbers[1]
            gcd = self.GCD(a, b)
            err = f'{a} = {gcd} * {a // gcd}；'
            err += f'{b} = {gcd} * {b // gcd}；'
            err += f'最小公倍数 = {gcd} * {a // gcd} * {b // gcd} = {self.correct_answer}'
            print(err)
            self.check_tips = f'{err}'

    def CheckTipsQFactor(self):
        expr = ' * '.join(map(str, self.user_answer))
        l = []
        err = ''
        try:
            for answer in self.user_answer:
                if not self.IsPrime(answer):
                    l.append(answer)
            if len(l) > 0:
                err = ', '.join(map(str, l))
                err += '不是质数'

            ret = eval(expr)
            if not ret == self.numbers[0]:
                if err:
                    err += f'，{expr} ≠ {self.numbers[0]}'
                else:
                    err = f'{expr} ≠ {self.numbers[0]}'
            self.check_tips = err
        except:
            self.check_tips = f'{self.user_answer}含有无效信息'


    def AnswerTips(self):
        des = ['质因数',
               '最大公约数',
               '最小公倍数']
        subtype = self.subtype[0]
        self.answer_tips = f"{des[subtype]}为：{self.correct_answer}"

"""
类名称：Question24Point
题目类型：计算24点
"""
class Question24Point(QuestionRL):
    def __init__(self, subtype = [0], range=[1, 10]):
        super().__init__(type = 0, subtype = subtype, range = range)
        self.name = "计算24点"
        self.comments = "输入表达式，使得表达式的值为24。如: (5+3)*(8-5)。"

    def Generate(self):
        self.BeforeGenerate()
        self.Question()
        self.Answer()
        self.AfterGenerate()
        print(self.question)

    def BeforeGenerate(self):
        super().BeforeGenerate()
        min_val = self.range[0]
        max_val = self.range[1]
        while True:
            self.numbers = sorted([random.randint(min_val, max_val) for _ in range(4)])
            if self.Validate24Point() is not None:
                break

    def Validate24Point(self):
        for perm in itertools.permutations(self.numbers):
            for ops in itertools.product(['+', '-', '*', '/'], repeat=3):
                expressions = [
                    f"({perm[0]} {ops[0]} {perm[1]}) {ops[1]} ({perm[2]} {ops[2]} {perm[3]})",
                    f"(({perm[0]} {ops[0]} {perm[1]}) {ops[1]} {perm[2]}) {ops[2]} {perm[3]}",
                    f"{perm[0]} {ops[0]} (({perm[1]} {ops[1]} {perm[2]}) {ops[2]} {perm[3]})",
                    f"{perm[0]} {ops[0]} ({perm[1]} {ops[1]} ({perm[2]} {ops[2]} {perm[3]}))",
                    f"({perm[0]} {ops[0]} {perm[1]}) {ops[1]} {perm[2]} {ops[2]} {perm[3]}"
                ]
                for expr in expressions:
                    try:
                        converted_expr = self.Fraction(expr)
                        if eval(expr) == 24 or eval(converted_expr) == 24:
                            return expr
                    except:
                        continue
        return None

    def Question(self):
        self.question = f'计算24点: {self.numbers}'
        return self.question

    def Answer(self):
        self.correct_answer = 24
        return self.correct_answer

    def CheckTips(self):
        if not self.UsedAllNumbers():
            self.check_tips = f'{self.user_input} ，未包括全部数字'
        else:
            try:
                if self.is_correct:
                    self.check_tips = '正确！'
                else:
                    self.check_tips = f'{self.user_input} = {self.user_results[0]} != {self.correct_answer}'
            except:
                self.check_tips = f'{self.user_answer}表达式不正确'
        return self.check_tips

    def AnswerTips(self):
        self.answer_tips = f'{self.Validate24Point()}'
        return self.answer_tips

    def UsedAllNumbers(self):
        # 使用正则表达式提取表达式中的所有数字
        numbers_in_expression = re.findall(r'\d+', self.user_answer)
        # 将提取的数字字符串转换为整数
        numbers_in_expression = [int(num_str) for num_str in numbers_in_expression]
        # 检查两个数组是否完全相同（数量和内容都相同，顺序可以不同）
        # print(sorted(numbers_in_expression))
        # print(sorted(self.numbers))
        return sorted(numbers_in_expression) == sorted(self.numbers)

    def JudgeAnswer(self):
        self.is_correct = super().JudgeAnswer()
        if not self.UsedAllNumbers():
            self.is_correct = False
        return self.is_correct

class QuestionReciprocal(QuestionRL): # 倒数之和题型
    def __init__(self, subtype, range):
        super().__init__(type=11, subtype = subtype, range = range)
        self.name = "倒数之和"
        self.comments = "在(  )内填入不同的自然数。"

    def Generate(self):
        self.BeforeGenerate()
        subtype = self.subtype[0]
        n = self.RandInt(2, 15)
        nomimator = 0
        num = 0
        self.numbers = [Fraction(1, n)]
        if subtype == 0: # 两个倒数之和
            self.question = f'1/(  ) + 1/(  ) = 1/{n}'
            self.correct_answer = [n*(n+1), n+1]
            lhs = '\\dfrac{1}{(\\quad)} + \\dfrac{1}{(\\quad)}'
        elif subtype == 1: # 三个倒数之和
            self.question = f'1/(  ) + 1/(  ) + 1/(  ) = 1/{n}'
            self.correct_answer = [n*(n+1), (n+1)*(n+2), n+2]
            lhs = '\\dfrac{1}{(\\quad)} + \\dfrac{1}{(\\quad)} + \\dfrac{1}{(\\quad)}'
        elif subtype == 2: # 四个倒数之和
            self.question = f'1/(  ) + 1/(  ) + 1/(  ) + 1/(  ) = 1/{n}'
            self.correct_answer = [n*(n+1), (n+1)*(n+2), (n+2)*(n+3), n+3]
            lhs = '\\dfrac{1}{(\\quad)} + \\dfrac{1}{(\\quad)} + \\dfrac{1}{(\\quad)} + \\dfrac{1}{(\\quad)}'
        elif subtype == 3: # 两个倒数之和等于真分数
            min = 32
            max = 200
            while True:
                num = self.RandInt(min, max)
                factors = self.GetFactors(num)[:-1]
                if len(factors) > 4:
                    break
            a = random.choice(factors)
            factors.remove(a)
            b = random.choice(factors)
            nomimator = a + b
            gcd = self.GCD(nomimator, num)
            # print(a, b, nomimator, num, gcd)
            if gcd != 1:
                nomimator //= gcd
                num //= gcd
            self.numbers = [Fraction(nomimator, num)]
            self.correct_answer = [num // a, num // b]
            self.question = f'1 / (  ) + 1 / (  ) = {nomimator} / {num}'
            lhs = '\\dfrac{1}{(\\quad)} + \\dfrac{1}{(\\quad)}'
        elif subtype == 4:  # 三个倒数之和等于真分数
            print('三个倒数之和等于真分数')
            min = 32
            max = 200
            while True:
                num = self.RandInt(min, max)
                factors = self.GetFactors(num)[:-1]
                if len(factors) > 4:
                    break
            a = random.choice(factors)
            factors.remove(a)
            b = random.choice(factors)
            factors.remove(b)
            c = random.choice(factors)
            nomimator = a + b + c
            gcd = self.GCD(nomimator, num)
            print(a, b, c, nomimator, num, gcd)
            if gcd != 1:
                nomimator //= gcd
                num //= gcd
            self.numbers = [Fraction(nomimator, num)]
            a, b, c = sorted([a, b, c])
            self.correct_answer = [num // a, num // b, num // c]
            self.question = f'1 / (  ) + 1 / (  ) + 1 / (  ) = {nomimator} / {num}'
            lhs = '\\dfrac{1}{(\\quad)} + \\dfrac{1}{(\\quad)} + \\dfrac{1}{(\\quad)}'
        try:
            print(self.question)
            if subtype == 0 or subtype == 1 or subtype == 2:
                rhs = f'\\dfrac{{1}}{{{n}}}'
            else:
                rhs = f'\\dfrac{{{nomimator}}}{{{num}}}'
            latex = r'${} = {}$'.format(lhs, rhs)
            self.Latex2PNG(latex, self.png_file)
        except:
            pass
        self.AfterGenerate()

    def BeforeJudgeAnswer(self):
        self.user_answer = self.user_answer.strip().replace(',', ' ').replace('，', ' ')
        self.user_answer = list(map(int, self.user_answer.split()))

    def JudgeAnswer(self):
        super().BeforeJudgeAnswer()
        self.BeforeJudgeAnswer()
        self.end_time = datetime.now()
        self.time_used = round((self.end_time - self.start_time).total_seconds(), 1)

        subtype = self.subtype[0]
        try:
            if self.HasDuplicates(self.user_answer): # 输入有相同的数字
                self.is_correct = False
                return False

            if subtype in [0, 1, 2] and len(self.user_answer) != subtype + 2: # 输入的数字个数不符合要求
                    self.is_correct = False
                    return False
            if subtype in [3] and len(self.user_answer) != subtype - 1:
                self.is_correct = False
                return False
            answer = 0
            for r in self.user_answer:
                answer += Fraction(1, r)
            # print(answer, self.numbers[0])
            if answer == self.numbers[0]:
                self.is_correct = True
            else:
                self.is_correct = False
        except:
            pass
        return self.is_correct

    def CheckTips(self):
        subtype = self.subtype[0]

        if subtype in [0, 1, 2] and len(self.user_answer) != subtype + 2: # 输入的数字个数不正确
            self.check_tips = f'要求输入{subtype + 2}个不同的自然数，实际输入了{len(self.user_answer)}个。'
            return
        if subtype > 3 and len(self.user_answer) != subtype - 1: # 输入的数字个数不正确
            self.check_tips = f'要求输入{subtype - 1}个不同的自然数，实际输入了{len(self.user_answer)}个。'
            return
        for num in self.user_answer:
            if self.user_answer.count(num) > 1:
                self.check_tips = f'{num}出现{self.user_answer.count(num)}次。'
                return
        answer = 0
        for i, r in enumerate(self.user_answer):
            answer += Fraction(1, r)
            if i == 0:
                str_answer = f'1 / {r}'
            else:
                str_answer += f' + 1 / {r}'
        if answer != self.numbers[0]:
            self.check_tips = f'左式 = {str_answer} = {answer} ≠ {self.numbers[0]}'

    def AnswerTips(self):
        subtype = self.subtype[0]
        n = Fraction(1, self.numbers[0])

        if subtype == 0:
            self.answer_tips = f'1/{n} = 1/{n} - 1/{n+1} + 1/{n+1} = 1/{n*(n+1)} + 1/{n+1}，正确答案：{n*(n+1)}, {n+1}'
        elif subtype == 1:
            self.answer_tips = f' 1/{n} = 1/{n} - 1/{n+1} + 1/{n+1} - 1/{n+2} + 1/{n+2} = 1/{n*(n+1)} + 1/{(n+1)*(n+2)} + 1/{n+2}'
            self.answer_tips += f'，正确答案：{n*(n+1)}, {(n+1)*(n+2)}, {n+2}'
            self.answer_tips += f'\n∵ 1/2 + 1/3 + 1/6 = 1，∴ 1/{n} = 1/{2*n} + 1/{3*n} + 1/{6*n}，正确答案：{2*n}, {3*n}, {6*n}'
        elif subtype == 2:
            self.answer_tips = f' 1/{n} = 1/{n} - 1/{n+1} + 1/{n+1} - 1/{n+2} + 1/{n+2} - 1/{n+3} + 1/{n+3} = 1/{n*(n+1)} + 1/{(n+1)*(n+2)} + 1/{(n+2)*(n+3)} + 1/{n+3}'
            self.answer_tips += f'\n正确答案：{n*(n+1)}, {(n+1)*(n+2)}, {(n+2)*(n+3)}, {n+3}'
        elif subtype >= 3:
            print(n)
            f = self.numbers[0]
            solution, num, den = self.GetSolution(f, subtype - 1)
            print(solution, num, den)
            for i, s in enumerate(solution):
                if i == 0:
                    self.answer_tips = f'{s}/{den}'
                else:
                    self.answer_tips += f' + {s}/{den}'
            for i, s in enumerate(solution):
                if i == 0:
                    self.answer_tips += f' = 1/{den//s}'
                else:
                    self.answer_tips += f' + 1/{den//s}'
            if f.denominator != den: # 进行过约分
                self.answer_tips += f' = {num}/{den}'
            self.answer_tips += f' = {f}'
            self.answer_tips += f'\n正确答案：'
            for i, s in enumerate(solution):
                if i == 0:
                    self.answer_tips += f'{den // s}'
                else:
                    self.answer_tips += f', {den // s}'

    def GetSolution(self, f, n):
        numerator = f.numerator
        denominator = f.denominator
        # print(numerator, denominator)
        i = 1
        while True:
            num = numerator * i
            den = denominator * i
            factors = self.GetFactors(den)
            # print(num, den, factors)
            for pair in itertools.combinations(factors, n):
                # print(pair, sum(pair), num)
                if sum(pair) == num:
                    return list(pair), num, den
            i += 1


"""
类名称：QuestionLR
题目类型：从左向右求值，即题目是表达式，答案是数值
"""
class QuestionLR(Question):
    def __init__(self, type=1, subtype=[0, 0], range=[1, 50, 10, 50]):
        super().__init__(type=1, subtype=subtype, range=range)
        self.type = type
        self.subtype = subtype
        self.range = range

    def Generate(self):
        self.BeforeGenerate()
        self.Question()
        self.Answer()
        self.AfterGenerate()
        print(self.question)

    def Question(self):
        try:
            expr = ''
            for i in range(len(self.numbers)):
                num = self.numbers[i]
                num = str(num) if num >= 0 else f'({num})'
                expr += num
                operator = f' {self.operators[i]} ' if i < len(self.operators) else ''
                expr += operator
            self.expression = expr
            self.question = expr.replace('*', '×').replace('/', '÷') + " = "
            return self.expression
        except:
            print('无法生成题目')
            return None

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        self.end_time = datetime.now()
        self.time_used = round((self.end_time - self.start_time).total_seconds(), 1)
        for opr in ['+', '-', '*', '/', '=',]:
            self.user_answer == self.user_answer.replace(opr, ' ')
        self.user_answer = self.user_answer.split(' ')[-1]
        try:
            if self.correct_answer == int(self.user_answer):
                self.is_correct = True
                return True
            else:
                self.is_correct = False
                self.error_number += 1
                return False
        except:
            self.is_correct = False
            self.error_number += 1
            return False

    def Answer(self):
        self.correct_answer = int(eval(self.Fraction(self.expression)))
        return self.correct_answer

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
        numbers_list = self.GenerateOppositeLists(self.numbers)
        try:
            user_answer = abs(self.user_answer)
        except:
            print(f'求值出错: {abs(self.user_answer)}')
        try:
            correct_answer = abs(self.correct_answer)
        except:
            print(f'求值出错: {abs(self.correct_answer)}')

        if user_answer / self.user_answer != correct_answer / self.correct_answer:
            return True
        try:
            for numbers in numbers_list:
                expr = ''
                for i in range(len(self.numbers)):
                    expr += f'{self.numbers[i]} {self.operators[i]} ' if i < len(self.operators) else f'{self.numbers[i]}'
                if eval(self.Fraction(expr)) == self.user_answer:
                    return True
        except:
            print('判断正负号的计算过程出错')

    def CheckTips(self):
        tips = ''
        try:
            if type(self.user_answer) == str:
                self.user_answer = eval(self.Fraction(self.user_answer))
            user_answer = abs(self.user_answer)
            correct_answer = abs(self.correct_answer)
            if self.IsSignError():
                tips += '检查正负号'
            elif user_answer % 10 != correct_answer % 10:
                tips += '检查个位数'
            elif len(str(user_answer)) != len(str(correct_answer)):
                tips += '检查总位数'
            elif user_answer // 10 != correct_answer // 10:
                tips += '检查进借位'
            self.check_tips = f'{tips}'
        except:
            self.check_tips = f'{self.user_answer}含有无效信息'
        return self.check_tips

    def AnswerTips(self):
        pass


"""
类名称：QuestionQC
题目类型：两位数乘法速算
"""
class QuestionQC(QuestionLR):
    def __init__(self, subtype=[0, 0], range=[10, 50, 1, 10]):
        super().__init__(type=1, subtype=subtype, range=range)
        self.name = "两位数乘法速算"
        self.comments = "输入答案，可以含中间过程。如: 36 * 36 = 32 * 40 + 4 * 4 = 1280 + 16 = 1296"

    def BeforeGenerate(self):
        super().BeforeGenerate()
        self.numbers = []
        self.operators = []
        subtype = self.subtype[0]
        min_val = self.range[0]
        max_val = self.range[1]
        if subtype < 0 or subtype >= 7:
            subtype = self.RandInt(0, 6)
            self.subtype2 = [subtype]
        if subtype == 0:  # 和十速算法
            n1 = self.RandInt(int(min_val / 10), int(max_val / 10)) * 10
            n2 = self.RandInt(1, 9)
            a = n1 + n2
            b = n1 + 10 - n2
            if a > max_val:
                a = a - 10
                b = b - 10
            self.numbers.append(a)
            self.operators.append('*')
            self.numbers.append(b)
        elif subtype == 1:  # 逢五凑十法
            n1 = self.RandInt(int(min_val / 5), int(max_val / 5)) * 5
            if n1 % 10 == 0:
                n1 += 5
            if n1 >= max_val:
                n1 -= 10
            n2 = self.RandInt(int(min_val / 2), int(max_val / 2)) * 2
            self.numbers.append(n1)
            self.operators.append('*')
            self.numbers.append(n2)
        elif subtype == 2:  # 平方差法
            n1 = self.RandInt(int(min_val / 5), int(max_val / 5)) * 5
            n2 = self.RandInt(1, 5)
            self.numbers.append(n1 + n2)
            self.operators.append('*')
            self.numbers.append(n1 - n2)
        elif subtype == 3:  # 平方数
            n = self.RandInt(min_val, max_val)
            self.numbers.append(n)
            self.operators.append('*')
            self.numbers.append(n)
        elif subtype == 4:  # 小数凑十法
            n1 = self.RandInt(int(min_val / 10), int(max_val / 10)) * 10
            n2 = self.RandInt(1, 3)
            if n1 + n2 < min_val:
                n1 + n2 + 10
            elif n1 + n2 > max_val:
                num1 = n1 + n2 - 10
            else:
                num1 = n1 + n2
            n3 = self.RandInt(int(min_val / 10), int(max_val / 10)) * 10
            n4 = self.RandInt(1, 9)
            num2 = n3 + n4 if n3 + n4 <= max_val else n3 + n4 - 10
            self.numbers.append(num1)
            self.operators.append('*')
            self.numbers.append(num2)
        elif subtype == 5:  # 大数凑十法
            n1 = self.RandInt(int(min_val / 10), int(max_val / 10)) * 10
            n2 = self.RandInt(7, 9)
            if n1 + n2 < min_val:
                num1 = n1 + n2 + 10
            elif n1 + n2 > max_val:
                num1 = n1 + n2 - 10
            else:
                num1 = n1 + n2
            n3 = self.RandInt(int(min_val / 10), int(max_val / 10)) * 10
            n4 = self.RandInt(1, 9)
            if n3 + n4 < min_val:
                num2 = n3 + n4 + 10
            elif n3 + n4 > max_val:
                num2 = n3 + n4 - 10
            else:
                num2 = n3 + n4
            self.numbers.append(num1)
            self.operators.append('*')
            self.numbers.append(num2)
        elif subtype == 6:  # 双向凑十法
            n1 = self.RandInt(int(min_val / 10), int(max_val / 10)) * 10
            num1 = n1 + self.RandInt(8, 9)
            n2 = self.RandInt(int(min_val / 10), int(max_val / 10)) * 10
            num2 = n2 + 10 - self.RandInt(1, 2)
            self.numbers.append(num1)
            self.operators.append('*')
            self.numbers.append(num2)
        self.numbers = sorted(self.numbers)
        return True

    def AnswerTips(self):
        tips = ''
        if self.subtype[0] == 0 or self.subtype2[0] == 0: # 和十速算法
            m = self.numbers[0]
            n = self.numbers[1]
            a = int(m/10)
            b = m % 10
            c = 10 -b
            tips += f'{a} × ({a} + 1) = {a} × {a+1} = {a*(a+1)}；{b} × {c} = {b*c}；{m} × {n} = {m*n}'
        if self.subtype[0] == 1 or self.subtype2[0] == 1:  # 逢五凑十法
            m = self.numbers[0]
            n = self.numbers[1]
            if n % 10 == 5:
                m, n = n, m
            if m % 25 == 0 and n % 4 == 0:
                a = int(m / 25)
                b = 25
                c = 4
                d = int(n / 4)
            else:
                a = int(m / 5)
                b = 5
                c = 2
                d = int(n / 2)
            tips += f'{m} × {n} = {m} × {c} × {d} = {m * c} × {d} = {m * n}'
        if self.subtype[0] == 2 or self.subtype2[0] == 2:  # 平方差法
            m = self.numbers[0]
            n = self.numbers[1]
            a = int((m + n) / 2)
            b = abs(a - self.numbers[0])
            if m % 10 == 0 and n % 10 == 0:
                tips += f'{m // 10} × {n // 10} = {m*n//100}，{m} × {n} = {m*n//100} × 100 = {m*n}'
            else:
                tips += f'{m} × {n} = ({a} - {b})({a} + {b}) = {a} × {a} - {b} × {b} = {a * a} - {b * b} = {a * a - b * b}'
        if self.subtype[0] == 3 or self.subtype2[0] == 3: # 平方数
            m = self.numbers[0]
            n = self.numbers[1]
            r = m % 10
            if r >= 5:
                c = 10 - r
            else:
                c = r
            a = m + c
            b = m - c
            tips += f'{m} × {n} = ({m} + {c}) × ({m} - {c}) + {c} × {c} = {a} × {b} + {c} × {c} = {a*b} + {c*c} = {a*b+c*c}'
        if self.subtype[0] == 4 or self.subtype2[0] == 4:  # 小数凑十法
            m = self.numbers[0]
            n = self.numbers[1]
            if m % 10 > n % 10:
                m, n = n, m
            r = m % 10
            tips += f'{m} × {n} = ({m-r} + {r}) × {n} = {m-r} × {n} + {r} × {n} = {(m-r) * n} + {r * n} = {m * n}'
        if self.subtype[0] == 5 or self.subtype2[0] == 5: # 大数凑十法
            m = self.numbers[0]
            n = self.numbers[1]
            if m % 10 < n % 10:
                m, n = n, m
            r = m % 10
            c = 10 - r
            tips += f'{m} × {n} = ({m+c} - {c}) × {n} = {m+c} × {n} - {c} × {n} = {(m+c)*n} - {c*n} = {m*n}'
        if self.subtype[0] == 6 or self.subtype2[0] == 6: # 双向凑十法
            m = self.numbers[0]
            n = self.numbers[1]
            b = 10 - m % 10
            a = m + b
            d = 10 - n % 10
            c = n + d
            tips += f'{m} × {n} = ({a} - {b}) × ({c} - {d}) = {a} × {c} - {a} × {d} - {b} × {c} + {b} × {d} = {a*c} - {a*d} - {b*c} + {b*d} = {m*n}'
        self.answer_tips = tips
        return self.answer_tips

"""
类名称：Question4AO
题目类型：四则运算
"""
class Question4AO(QuestionLR):
    def __init__(self, subtype=[0, 0], range=[1, 50, 10, 50]):
        super().__init__(type = 2, subtype = subtype, range = range)
        # print(self.subtype)
        self.name = "四则速算"
        self.comments = "输入答案，可以含中间过程。如: 36 * 36 = 32 * 40 + 4 * 4 = 1280 + 16 = 1296"

    def BeforeGenerate(self):
        super().BeforeGenerate()
        ops = [['+'], ['-'], ['*'], ['/'], ['+', '-', '*', '/']]
        term_count = self.subtype[0] + 2
        try:
            user_operators = ops[self.subtype[1]]
        except:
            print('运算符选择错误')

        for i in range(term_count):
            num = self.RandInt(self.range[0], self.range[1])
            self.numbers.append(num)
            if i < term_count - 1:
                self.operators.append(random.choice(user_operators))
        self.Validate()
        self.Question()
        return True

    def Divisor(self):
        num = self.RandInt(self.range[2], self.range[3])
        while num == 0:
            num = self.RandInt(self.range[2], self.range[3])
        return num

    def Validate(self):
        count = self.subtype[0]
        for i in range(count, -1, -1):
            if self.operators[i] in ['*', '/']:
                self.numbers[i + 1] = self.Divisor()
                self.numbers[i] = self.Divisor()

        flag = 0
        for i in range(count, -1, -1):
            if self.operators[i] == '/':
                if flag == 0:
                    flag = 1
                    num = self.numbers[i + 1] * self.numbers[i]
                else:
                    num *= self.numbers[i]
                if i == 0:
                    self.numbers[i] = num
            else:
                if flag == 1:
                    self.numbers[i + 1] = num
                    flag = 0

    def AnswerTips(self):
        self.answer_tips = f'正确答案：{self.question} {self.correct_answer}'
        return self.answer_tips

class QuestionConversion(QuestionLR):
    def __init__(self, subtype=[0]):
        self.name = "单位换算"
        # 定义长度单位之间的换算关系（基数为米）
        self.length_rates = {
            "千米": 1000000,
            "米": 1000,
            "分米": 100,
            "厘米": 10,
            "毫米": 1,
        }
        self.area_rates = {
            "平方千米": 1e6,
            "公顷": 1e4,
            "亩": Fraction(2000,3),
            "平方米": 1,
            "平方分米": 1e-2,
            "平方厘米": 1e-4,
            "平方毫米": 1e-6,
        }
        self.volume_rates = {
            "立方米": 1e9,
            "立方分米": 1e6,
            "升": 1e6,
            "立方厘米": 1e3,
            "毫升": 1e3,
            "立方毫米": 1,
        }
        self.mass_rates = {
            "吨": 1e6,
            "千克": 1e3,
            "克": 1,
            "毫克": 1e-3,
        }
        self.time_rates = {
            "时": 3600,
            "分": 60,
            "秒": 1,
            "毫秒": 1e-3,
        }
        self.rates = [
            self.length_rates,
            self.area_rates,
            self.volume_rates,
            self.mass_rates,
            self.time_rates,
        ]
        self.length_units = list(self.length_rates.keys())
        self.area_units = list(self.area_rates.keys())
        self.volume_units = list(self.volume_rates.keys())
        self.mass_units = list(self.mass_rates.keys())
        self.time_units = list(self.time_rates.keys())
        self.units = [
            self.length_units,
            self.area_units,
            self.volume_units,
            self.mass_units,
            self.time_units,
        ]
        super().__init__(type=4, subtype=subtype)

        if self.subtype[0] == 0:
            self.comments = "长度换算：1米 = (    )毫米，输入答案：1000，或1 000，或 = 1 000"
        elif self.subtype[0] == 1:
            self.comments = "面积换算：1平方米 = (    )平方厘米，输入答案：10000，或10 000，或 = 10 000"
        elif self.subtype[0] == 2:
            self.comments = "体积换算：1升 = (    )毫升，输入答案：1000，或1 000，或 = 1 000"
        elif self.subtype[0] == 3:
            self.comments = "质量换算：1吨 = (    )千克，输入答案：1000，或1 000，或 = 1 000"
        elif self.subtype[0] == 4:
            self.comments = "时间换算：1时 = (    )秒，输入答案：3600，或3 600，或 = 3 600"

    def Generate(self):
        sub_type = self.subtype[0]
        self.BeforeGenerate()
        while True:
            big_num = self.RandInt(1, 100) / 10
            if big_num == int(big_num):
                big_num = int(big_num)
            big_unit = random.choice(self.units[sub_type])
            small_unit = random.choice(self.units[sub_type])
            big_rate = self.rates[sub_type][big_unit]
            small_rate = self.rates[sub_type][small_unit]
            if small_unit == big_unit:
                continue
            elif big_rate < small_rate or big_rate > small_rate * 1e6:
                continue
            else:
                break
        rate = big_rate / small_rate
        if self.subtype[0] == 4 and rate > 1000:  # 时间换算题型
            big_num = random.choice([1,2,3,5,10])
        small_num = big_num *  big_rate / small_rate
        if small_num  == int(small_num):
            small_num = int(small_num)
        if self.RandInt(0, 1) == 0: # 大单位换算为小单位
            self.direction = 1
            if int(big_num) == big_num:
                self.question = f'{int(big_num)}{big_unit} = (        ){small_unit}'
            else:
                self.question = f'{float(big_num):.1f}{big_unit} = (        ){small_unit}'
            if abs(small_num - int(small_num)) < 1e-3:
                self.correct_answer = int(small_num)
            else:
                self.correct_answer = small_num
        else: # 小单位换算为大单位
            self.direction = -1
            if abs(small_num - int(small_num)) < 1e-3:
                str_small_num = f'{small_num: ,.0f}'.replace(',', ' ')
                self.question = f'{str_small_num}{small_unit} = (        ){big_unit}'
            else:
                str_small_num = f'{small_num: ,.1f}'.replace(',', ' ')
                self.question = f'{str_small_num}{small_unit} = (        ){big_unit}'
            self.correct_answer = big_num
        self.big_unit = big_unit
        self.small_unit = small_unit
        self.big_rate = big_rate
        self.small_rate = small_rate
        self.big_num = big_num
        if small_num == int(small_num):
            self.small_num = f'{small_num: ,.0f}'.replace(',', ' ')
        else:
            self.small_num = f'{small_num: ,.1f}'.replace(',', ' ')
        self.rate = str(f'{big_rate / small_rate : ,.0f}').replace(',', ' ')
        self.AfterGenerate()
        print(self.question)

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        try:
            user_answer = float(self.user_answer.strip().replace(' ', ''))
            if abs(user_answer - self.correct_answer) < 1e-3 :
                self.is_correct = True
            else:
                self.is_correct = False
        except:
            self.is_correct = False
        return self.is_correct

    def CheckTips(self):
        self.check_tips = f'1{self.big_unit} = {self.rate}{self.small_unit}'

    def AnswerTips(self):
        if self.direction > 0:
            self.answer_tips = f'{self.big_num} × {self.rate} = {self.small_num}'
        else:
            self.answer_tips = f'{self.small_num} ÷ {self.rate} = {self.big_num}'

class QuestionFraction(QuestionLR):
    def __init__(self, subtype=[0]):
        super().__init__(type=5, subtype=subtype)
        self.name = "分数运算"
        if subtype[0] == 0:
            self.comments = "分数加法：1/2 + 1/3 = ，答案输入：5/6，或：1/2 + 1/3 = 5/6"
        elif subtype[0] == 1:
            comments = "分数减法：1/2 - 1/3 = ，答案输入：1/6，或：1/2 - 1/3 = 1/6"
        elif subtype[0] == 2:
            self.comments = "分数乘法：1/2 × 1/3 = ，答案输入：1/6，或：1/2 × 1/3 = 1/6"
        elif subtype[0] == 3:
            self.comments = "分数除法：1/2 ÷ 1/3 = ，答案输入：3/2，或：1/2 ÷ 1/3 = 3/2"

    def Generate(self):
        sub_type = self.subtype[0]
        self.BeforeGenerate()
        if sub_type == 0 or sub_type == 1:
            scale = 1
        else:
            scale = 3
        while True:
            a = self.RandInt(2, 10)
            b = self.RandInt(1, scale * a - 1)
            gcd = self.GCD(a, b)
            if gcd != 1:
                a //= gcd
                b //= gcd
            if a > 1:
                break
        while True:
            c = self.RandInt(2, 10)
            d = self.RandInt(1, scale * c - 1)
            gcd = self.GCD(c, d)
            if gcd != 1:
                c //= gcd
                d //= gcd
            if c > 1:
                break
        self.numbers = [a, b, c, d]
        if sub_type == 0:
            self.expression = f'{b}/{a} + {d}/{c}'
            sign = '+'
            self.formula = '\\dfrac{' + f'{b}' + '}{' + f'{a}' + '}' + f'{sign}' + '\\dfrac{' + f'{d}' + '}{' + f'{c}' + '} = '
            self.correct_answer = Fraction(b, a) + Fraction(d, c)
        elif sub_type == 1:
            self.expression = f'{b}/{a} - {d}/{c}'
            sign = '-'
            self.formula = '\\dfrac{' + f'{b}' + '}{' + f'{a}' + '}' + f'{sign}' + '\\dfrac{' + f'{d}' + '}{' + f'{c}' + '} = '
            self.correct_answer = Fraction(b, a) - Fraction(d, c)
        elif sub_type == 2:
            self.expression = f'{b}/{a} × {d}/{c}'
            sign = '\\times'
            self.formula = '\\dfrac{' + f'{b}' + '}{' + f'{a}' + '}' + f'{sign}' + '\\dfrac{' + f'{d}' + '}{' + f'{c}' + '} = '
            self.correct_answer = Fraction(b, a) * Fraction(d, c)
        elif sub_type == 3:
            self.expression = f'{b}/{a} ÷ {d}/{c}'
            sign = '\\div'
            self.formula = '\\dfrac{' + f'{b}' + '}{' + f'{a}' + '}' + f'{sign}' + '\\dfrac{' + f'{d}' + '}{' + f'{c}' + '} = '
            self.correct_answer = Fraction(b, a) / Fraction(d, c)
        self.question = self.expression + ' = '
        print(f'{self.question}{self.correct_answer}')
        latex = r'${}$'.format(self.formula)
        self.Latex2PNG(latex, self.png_file)
        self.AfterGenerate()

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        try:
            user_answer = Fraction(self.user_answer)
            if user_answer == self.correct_answer:
                self.is_correct = True
            else:
                self.is_correct = False
        except:
            self.is_correct = False
        return self.is_correct

    def CheckTips(self):
        try:
            [a, b, c, d] = self.numbers
            denominator = self.LCM(a, c)
            if self.subtype[0] == 0:
                self.check_tips = f'{self.expression} = {int(denominator*b/a)}/{denominator} + {int(denominator*d/c)}/{denominator}'
                self.check_tips += f' = {int(denominator*b/a + denominator*d/c)}/{denominator} = {self.correct_answer}'
            elif self.subtype[0] == 1:
                self.check_tips = f'{self.expression} = {int(denominator*b/a)}/{denominator} - {int(denominator*d/c)}/{denominator}'
                self.check_tips += f' = {int(denominator*b/a - denominator*d/c)}/{denominator} = {self.correct_answer}'
            elif self.subtype[0] == 2:
                self.check_tips = f'{self.expression} = {b * d}/{a * c} = {self.correct_answer}'
            elif self.subtype[0] == 3:
                self.check_tips = f'{self.expression} = {b}/{a} × {c}/{d} = {b*c}/{a*d} = {self.correct_answer}'
        except:
            pass

    def AnswerTips(self):
        try:
            [a, b, c, d] = self.numbers
            denominator = self.LCM(a, c)
            if self.subtype[0] == 0:
                self.answer_tips = f'{self.expression} = {int(denominator*b/a)}/{denominator} + {int(denominator*d/c)}/{denominator}'
                self.answer_tips += f' = {int(denominator*b/a + denominator*d/c)}/{denominator} = {self.correct_answer}'
            elif self.subtype[0] == 1:
                self.answer_tips = f'{self.expression} = {int(denominator*b/a)}/{denominator} - {int(denominator*d/c)}/{denominator}'
                self.answer_tips += f' = {int(denominator*b/a - denominator*d/c)}/{denominator} = {self.correct_answer}'
            elif self.subtype[0] == 2:
                self.answer_tips = f'{self.expression} = {b * d}/{a * c} = {self.correct_answer}'
            elif self.subtype[0] == 3:
                self.answer_tips = f'{self.expression} = {b}/{a} × {c}/{d} = {b*c}/{a*d} = {self.correct_answer}'
        except:
            pass

class QuestionDecimal(QuestionLR):
    def __init__(self, subtype=[0]):
        super().__init__(type=6, subtype=subtype)
        self.name = "分数运算"
        if subtype[0] == 0:
            self.comments = "小数加法：0.1 + 0.2 = ，答案输入：0.3，或：0.1 + 0.2 = 0.3"
        elif subtype[0] == 1:
            comments = "小数减法：1.5 - 0.3 = ，答案输入：1.2，或：1.5 - 0.3 = 1.2"
        elif subtype[0] == 2:
            self.comments = "小数乘法：1.5 × 0.3 = ，答案输入：0.45，或：1.5 * 0.3 = 0.45"
        elif subtype[0] == 3:
            self.comments = "小数除法：1.5 ÷ 0.3 = ，答案输入：5，或：1.5 / 0.3 = 5"

    def Generate(self):
        sub_type = self.subtype[0]
        self.BeforeGenerate()
        if sub_type == 0:
            a = decimal.Decimal(self.RandInt(1, 50)) / decimal.Decimal(random.choice([2, 4, 5, 10, 20, 50]))
            b = decimal.Decimal(self.RandInt(1, 50)) / decimal.Decimal(random.choice([2, 4, 5, 10, 20, 50]))
            self.numbers = [a, b]
            self.expression = f'{a} + {b}'
            self.correct_answer = decimal.Decimal(a) + decimal.Decimal(b)
        elif sub_type == 1:
            a = decimal.Decimal(self.RandInt(1, 50)) / decimal.Decimal(random.choice([2, 4, 5, 10, 20, 50]))
            b = decimal.Decimal(self.RandInt(1, 50)) / decimal.Decimal(random.choice([2, 4, 5, 10, 20, 50]))
            self.numbers = [a, b]
            self.expression = f'{a} - {b}'
            self.correct_answer = decimal.Decimal(a) - decimal.Decimal(b)
        elif sub_type == 2:
            a = decimal.Decimal(self.RandInt(1, 50)) / decimal.Decimal(random.choice([1, 10]))
            b = decimal.Decimal(self.RandInt(1, 50)) / decimal.Decimal(random.choice([10]))
            self.numbers = [a, b]
            self.expression = f'{a} * {b}'
            self.correct_answer = a * b
        elif sub_type == 3:
            a = decimal.Decimal(self.RandInt(1, 50)) / decimal.Decimal(random.choice([1, 10]))
            b = 1
            while b == 1:
                b = decimal.Decimal(random.choice([1, 2, 4, 5, 8, 10, 20, 25, 40, 50])) / decimal.Decimal(random.choice([10]))
            self.numbers = [a, b]
            self.expression = f'{a} / {b}'
            self.correct_answer = a / b
        self.question = self.expression.replace('*', '×').replace('/', '÷') + ' = '
        print(f'{self.question}{self.correct_answer}')
        self.AfterGenerate()

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        try:
            user_answer = decimal.Decimal(self.user_answer)
            if user_answer == self.correct_answer:
                self.is_correct = True
            else:
                self.is_correct = False
        except:
            self.is_correct = False
        return self.is_correct

    def CheckTips(self):
        try:
            [a, b] = self.numbers
            if self.subtype[0] == 0:
                self.check_tips = f'{self.expression} = {decimal.Decimal(a) + decimal.Decimal(b)}'
            if self.subtype[0] == 1:
                self.check_tips = f'{self.expression} = {decimal.Decimal(a) - decimal.Decimal(b)}'
            if self.subtype[0] == 2:
                self.check_tips = f'{self.expression} = {decimal.Decimal(a) * decimal.Decimal(b)}'
            if self.subtype[0] == 3:
                self.check_tips = f'{self.expression} = {decimal.Decimal(a) / decimal.Decimal(b)}'
        except:
            pass

    def AnswerTips(self):
        try:
            [a, b] = self.numbers
            if self.subtype[0] == 0:
                self.answer_tips = f'{self.expression} = {decimal.Decimal(a) + decimal.Decimal(b)}'
            if self.subtype[0] == 1:
                self.answer_tips = f'{self.expression} = {decimal.Decimal(a) - decimal.Decimal(b)}'
            if self.subtype[0] == 2:
                self.answer_tips = f'{self.expression} = {decimal.Decimal(a) * decimal.Decimal(b)}'
            if self.subtype[0] == 3:
                self.answer_tips = f'{self.expression} = {decimal.Decimal(a) / decimal.Decimal(b)}'
        except:
            pass

class QuestionRatio(QuestionLR):
    def __init__(self, subtype=[0]):
        super().__init__(type=7, subtype=subtype)
        self.name = "分数运算"
        if subtype[0] == 0:
            self.comments = "内项计算：2 : 1 = (    ) : 3 ，答案输入：6"
        if subtype[0] == 1:
            self.comments = "外项计算：2 : 1 = 1 : (    ) ，答案输入：0.5，或：1/2"
        if subtype[0] == 2:
            self.comments = ("比值计算：2 : 4 = (    )，答案输入：0.5，或：1/2")

    def Generate(self):
        sub_type = self.subtype[0]
        self.BeforeGenerate()
        if sub_type == 0:
            while True:
                a = self.RandInt(1, 20)
                b = self.RandInt(2, 10)
                if self.GCD(a, b) == 1:
                    break
            c = b * self.RandInt(2, 10)
            self.correct_answer = decimal.Decimal(c) * decimal.Decimal(a) // decimal.Decimal(b)
            self.numbers = [a, b, c]
            self.expression = f'{a} : {b} = (    ) : {c}'
        elif sub_type == 1:
            while True:
                a = self.RandInt(1, 20)
                b = self.RandInt(2, 10)
                if self.GCD(a, b) == 1:
                    break
            c = a * self.RandInt(2, 10)
            self.correct_answer = decimal.Decimal(b) * decimal.Decimal(c) // decimal.Decimal(a)
            self.numbers = [a, b, c]
            self.expression = f'{a} : {b} = {c} : (    )'
        elif sub_type == 2:
            b = self.RandInt(1, 20)
            a = b * self.RandInt(2, 10) / 10
            self.correct_answer = decimal.Decimal(a) / decimal.Decimal(b)
            self.numbers = [a, b]
            self.expression = f'{a} : {b} = (    )'
        self.question = self.expression
        print(f'{self.question}，正确答案：{self.correct_answer}')
        self.AfterGenerate()

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        try:
            user_answer = decimal.Decimal(self.user_answer)
            print(type(user_answer), type(self.correct_answer))
            print(user_answer, self.correct_answer)
            if user_answer == self.correct_answer:
                self.is_correct = True
            else:
                self.is_correct = False
        except:
            self.is_correct = False
        return self.is_correct

    def CheckTips(self):
        try:
            if self.subtype[0] == 0 or self.subtype[0] == 1:
                [a, b, c] = self.numbers
            elif self.subtype[0] == 2:
                [a, b] = self.numbers
            if self.subtype[0] == 0:
                self.check_tips = f'(    ) = {a} × {c} ÷ {b} = {a * c // b}'
            elif self.subtype[0] == 1:
                self.check_tips = f'(    ) = {c} ÷ {a} × {b} = {b * c // a}'
            elif self.subtype[0] == 2:
                self.check_tips = f'(    ) = {a} ÷ {b} = {a / b}'
        except:
            pass

    def AnswerTips(self):
        try:
            if self.subtype[0] == 0 or self.subtype[0] == 1:
                [a, b, c] = self.numbers
            elif self.subtype[0] == 2:
                [a, b] = self.numbers
            if self.subtype[0] == 0:
                self.answer_tips = f'(    ) = {a} × {c} ÷ {b} = {a * c // b}'
            elif self.subtype[0] == 1:
                self.answer_tips = f'(    ) = {b} × {c} ÷ {a} = {b * c // a}'
            elif self.subtype[0] == 2:
                self.answer_tips = f'(    ) = {a} ÷ {b} = {a / b}'
        except:
            pass

class QuestionPerimeter(QuestionLR):
    def __init__(self, subtype=[0]):
        super().__init__(type=8, subtype=subtype)
        self.name = "周长计算"
        self.comments = "输入周长的数值。如：6，或 = 6"

    def Generate(self):
        sub_type = self.subtype[0]
        self.BeforeGenerate()
        if sub_type == 0:
            while True:
                a = self.RandInt(1, 20)
                b = self.RandInt(10, 20)
                c = self.RandInt(5, 15)
                if a + b > c and a + c > b and b + c > a:
                    break
            self.correct_answer = a + b + c
            self.numbers = [a, b, c]
            self.expression = f'三角形三边长分别为{a}cm、{b}cm、{c}cm，求三角形的周长（单位：cm）。'
        elif sub_type == 1:
            a = self.RandInt(1, 20)
            b = self.RandInt(2, 10)
            if a < b:
                a, b = b, a
            self.correct_answer = 2 * (a + b)
            self.numbers = [a, b]
            self.expression = f'长方形长为{a}cm，宽为{b}cm，求长方形的周长（单位：cm）。'
        elif sub_type == 2:
            a = self.RandInt(1, 20)
            self.correct_answer = 4 * a
            self.numbers = [a]
            self.expression = f'正方形边长为{a}cm，求正方形的周长（单位：cm）。'
        elif sub_type == 3:
            a = self.RandInt(1, 20)
            b = self.RandInt(1, 20)
            self.correct_answer = 2 * (a + b)
            self.numbers = [a, b]
            self.expression = f'平行四边形底边为{a}cm、斜边为{b}cm，求平行四边形的周长（单位：cm）。'
        elif sub_type == 4:
            a = self.RandInt(1, 10)
            b = self.RandInt(10, 20)
            c = self.RandInt(5, 10)
            d = self.RandInt(5, 10)
            self.correct_answer = a + b + c + d
            self.numbers = [a, b, c, d]
            self.expression = f'梯形的底边分别为{a}cm、{b}cm，斜边分别为{c}cm、{d}cm，求梯形的周长（单位：cm）。'
        elif sub_type == 5:
            r = self.RandInt(1, 10)
            self.correct_answer = decimal.Decimal(round(628 * r, 0)) / 100
            print(self.correct_answer)
            self.numbers = [r]
            if self.RandInt(1, 10) % 2 == 0:
                self.expression = f'半径为{r}cm，求圆的周长（单位：cm），π取值3.14。'
            else:
                self.expression = f'直径为{2*r}cm，求圆的周长（单位：cm），π取值3.14。'
        elif sub_type == 6:
            r = self.RandInt(1, 10)
            self.correct_answer = decimal.Decimal(round(314 * r, 0)) / 100 + 2 * r
            print(self.correct_answer)
            self.numbers = [r]
            if self.RandInt(1, 10) % 2 == 0:
                self.expression = f'半径为{r}cm，求半圆的周长（单位：cm），π取值3.14。'
            else:
                self.expression = f'直径为{2*r}cm，求半圆的周长（单位：cm），π取值3.14。'
        elif sub_type == 7:
            r = self.RandInt(1, 10)
            self.correct_answer = decimal.Decimal(round(314 * r, 0)) / 200 + 2 * r
            print(self.correct_answer)
            self.numbers = [r]
            if self.RandInt(1, 10) % 2 == 0:
                self.expression = f'半径为{r}cm，求四分之一圆的周长（单位：cm），π取值3.14。'
            else:
                self.expression = f'直径为{2*r}cm，求四分之一圆的周长（单位：cm），π取值3.14。'
        self.question = self.expression
        print(f'{self.question}，正确答案：{self.correct_answer}')
        self.AfterGenerate()

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        try:
            user_answer = decimal.Decimal(self.user_answer)
            if user_answer == self.correct_answer:
                self.is_correct = True
            else:
                self.is_correct = False
        except:
            self.is_correct = False
        return self.is_correct

    def CheckTips(self):
        try:
            if self.subtype[0] == 0:
                [a, b, c] = self.numbers
                self.check_tips = f'{a} + {b} + {c} = {self.correct_answer}'
            elif self.subtype[0] == 1:
                [a, b] = self.numbers
                self.check_tips = f'2 × ({a} + {b}) = 2 × {a + b} = {self.correct_answer}'
            elif self.subtype[0] == 2:
                [a] = self.numbers
                self.check_tips = f'4 × {a} = {self.correct_answer}'
            elif self.subtype[0] == 3:
                [a, b] = self.numbers
                self.check_tips = f'2 × ({a} + {b}) = 2 × {a + b} = {self.correct_answer}'
            elif self.subtype[0] == 4:
                [a, b, c, d] = self.numbers
                self.check_tips = f'{a} + {b} + {c} + {d} = {self.correct_answer}'
            elif self.subtype[0] == 5:
                [r] = self.numbers
                self.check_tips = f'3.14 × {2 * r} = {self.correct_answer}'
            elif self.subtype[0] == 6:
                [r] = self.numbers
                self.check_tips = f'3.14 × {r} + 2 × {r} = 5.14 × {r} = {self.correct_answer}'
            elif self.subtype[0] == 7:
                [r] = self.numbers
                self.check_tips = f'3.14 ÷ 2 × {r} + 2 × {r} = 3.57 × {r} = {self.correct_answer}'
        except:
            pass

    def AnswerTips(self):
        try:
            if self.subtype[0] == 0:
                [a, b, c] = self.numbers
                self.answer_tips = f'{a} + {b} + {c} = {self.correct_answer}'
            elif self.subtype[0] == 1:
                [a, b] = self.numbers
                self.answer_tips = f'2 × ({a} + {b}) = 2 × {a + b} = {self.correct_answer}'
            elif self.subtype[0] == 2:
                [a] = self.numbers
                self.answer_tips = f'4 × {a} = {self.correct_answer}'
            elif self.subtype[0] == 3:
                [a, b] = self.numbers
                self.answer_tips = f'2 × ({a} + {b}) = 2 × {a + b} = {self.correct_answer}'
            elif self.subtype[0] == 4:
                [a, b, c, d] = self.numbers
                self.answer_tips = f'{a} + {b} + {c} + {d} = {self.correct_answer}'
            elif self.subtype[0] == 5:
                [r] = self.numbers
                self.answer_tips = f'3.14 × {2 * r} = {self.correct_answer}'
            elif self.subtype[0] == 6:
                [r] = self.numbers
                self.answer_tips = f'3.14 × {r} + 2 × {r} = 5.14 × {r} = {self.correct_answer}'
            elif self.subtype[0] == 7:
                [r] = self.numbers
                self.answer_tips = f'3.14 ÷ 2 × {r} + 2 × {r} = 3.57 × {r} = {self.correct_answer}'
        except:
            pass

class QuestionArea(QuestionLR):
    def __init__(self, subtype=[0]):
        super().__init__(type=9, subtype=subtype)
        self.name = "面积计算"
        self.comments = "输入面积的数值。如：16，或 4 * 4 = 16"

    def Generate(self):
        sub_type = self.subtype[0]
        self.BeforeGenerate()
        if sub_type == 0:
            a = self.RandInt(1, 20)
            h = self.RandInt(1, 20)
            self.correct_answer = decimal.Decimal(1 / 2 * a * h)
            self.numbers = [a, h]
            self.expression = f'三角形底边长分别为{a}厘米，高为{h}厘米，求三角形的面积（单位：平方厘米）。'
        elif sub_type == 1:
            a = self.RandInt(1, 20)
            b = self.RandInt(2, 10)
            if a < b:
                a, b = b, a
            self.correct_answer = a * b
            self.numbers = [a, b]
            self.expression = f'长方形长为{a}厘米，宽为{b}厘米，求长方形的面积（单位：平方厘米）。'
        elif sub_type == 2:
            a = self.RandInt(1, 20)
            self.correct_answer = a * a
            self.numbers = [a]
            self.expression = f'正方形边长为{a}厘米，求正方形的面积（单位：平方厘米）。'
        elif sub_type == 3:
            a = self.RandInt(1, 20)
            h = self.RandInt(1, 20)
            self.correct_answer = a * h
            self.numbers = [a, h]
            self.expression = f'平行四边形底边为{a}厘米、高为{h}厘米，求平行四边形的周长（单位：平方厘米）。'
        elif sub_type == 4:
            a = self.RandInt(1, 10)
            b = self.RandInt(10, 20)
            h = self.RandInt(5, 10)
            self.correct_answer = decimal.Decimal(1/2*(a+b)*h)
            self.numbers = [a, b, h]
            self.expression = f'梯形的底边分别为{a}厘米、{b}厘米，高为{h}厘米，求梯形的面积（单位：平方厘米）。'
        elif sub_type == 5:
            r = self.RandInt(1, 10)
            self.correct_answer = decimal.Decimal(314 * r * r) / 100
            print(self.correct_answer)
            self.numbers = [r]
            if self.RandInt(1, 10) % 2 == 0:
                self.expression = f'半径为{r}厘米，求圆的面积（单位：平方厘米），π取值3.14。'
            else:
                self.expression = f'直径为{2*r}厘米，求圆的面积（单位：平方厘米），π取值3.14。'
        elif sub_type == 6:
            r = self.RandInt(1, 10)
            self.correct_answer = decimal.Decimal(314 * r * r) / 200
            print(self.correct_answer)
            self.numbers = [r]
            if self.RandInt(1, 10) % 2 == 0:
                self.expression = f'半径为{r}厘米，求半圆的面积（单位：平方厘米），π取值3.14。'
            else:
                self.expression = f'直径为{2*r}厘米，求半圆的面积（单位：平方厘米），π取值3.14。'
        elif sub_type == 7:
            r = self.RandInt(1, 10)
            self.correct_answer = decimal.Decimal(314 * r * r) / 400
            print(self.correct_answer)
            self.numbers = [r]
            if self.RandInt(1, 10) % 2 == 0:
                self.expression = f'半径为{r}厘米，求四分之一圆的面积（单位：平方厘米），π取值3.14。'
            else:
                self.expression = f'直径为{2*r}厘米，求四分之一圆的面积（单位：平方厘米），π取值3.14。'
        self.question = self.expression
        print(f'{self.question}正确答案：{self.correct_answer}')
        self.AfterGenerate()

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        try:
            user_answer = decimal.Decimal(self.user_answer)
            if user_answer == self.correct_answer:
                self.is_correct = True
            else:
                self.is_correct = False
        except:
            self.is_correct = False
        return self.is_correct

    def CheckTips(self):
        try:
            if self.subtype[0] == 0:
                [a, h] = self.numbers
                self.check_tips = f'1/2 × {a} × {h} = {self.correct_answer}'
            elif self.subtype[0] == 1:
                [a, b] = self.numbers
                self.check_tips = f'{a} × {b} = {self.correct_answer}'
            elif self.subtype[0] == 2:
                [a] = self.numbers
                self.check_tips = f'{a} × {a} = {self.correct_answer}'
            elif self.subtype[0] == 3:
                [a, h] = self.numbers
                self.check_tips = f'{a} × {h} = {self.correct_answer}'
            elif self.subtype[0] == 4:
                [a, b, h] = self.numbers
                self.check_tips = f'1/2 × ({a} + {b}) × {h} = {self.correct_answer}'
            elif self.subtype[0] == 5:
                [r] = self.numbers
                self.check_tips = f'3.14 × {r}  × {r} = {self.correct_answer}'
            elif self.subtype[0] == 6:
                [r] = self.numbers
                self.check_tips = f'3.14 × {r} × {r} ÷ 2 = {self.correct_answer}'
            elif self.subtype[0] == 7:
                [r] = self.numbers
                self.check_tips = f'3.14 × {r} × {r} ÷ 4 = {self.correct_answer}'
        except:
            pass

    def AnswerTips(self):
        try:
            if self.subtype[0] == 0:
                [a, h] = self.numbers
                self.answer_tips = f'1/2 × {a} × {h} = {self.correct_answer}'
            elif self.subtype[0] == 1:
                [a, b] = self.numbers
                self.answer_tips = f'{a} × {b} = {self.correct_answer}'
            elif self.subtype[0] == 2:
                [a] = self.numbers
                self.answer_tips = f'{a} × {a} = {self.correct_answer}'
            elif self.subtype[0] == 3:
                [a, h] = self.numbers
                self.answer_tips = f'{a} × {h} = {self.correct_answer}'
            elif self.subtype[0] == 4:
                [a, b, h] = self.numbers
                self.answer_tips = f'1/2 × ({a} + {b}) × {h} = {self.correct_answer}'
            elif self.subtype[0] == 5:
                [r] = self.numbers
                self.answer_tips = f'3.14 × {r}  × {r} = {self.correct_answer}'
            elif self.subtype[0] == 6:
                [r] = self.numbers
                self.answer_tips = f'3.14 × {r} × {r} ÷ 2 = {self.correct_answer}'
            elif self.subtype[0] == 7:
                [r] = self.numbers
                self.answer_tips = f'3.14 × {r} × {r} ÷ 4 = {self.correct_answer}'
        except:
            pass


class QuestionVolume(QuestionLR):
    def __init__(self, subtype=[0]):
        super().__init__(type=10, subtype=subtype)
        self.name = "体积计算"
        self.comments = "输入体积的数值。如：64，或 4 * 4 * 4 = 64"

    def Generate(self):
        sub_type = self.subtype[0]
        self.BeforeGenerate()
        if sub_type == 0: # 长方体
            a = self.RandInt(1, 10)
            b = self.RandInt(1, 10)
            c = self.RandInt(1, 10)
            self.correct_answer = a * b * c
            self.numbers = [a, b, c]
            self.expression = f'求边长分别为{a}厘米、{b}厘米、{c}厘米的长方体的体积（单位：立方厘米）。'
        elif sub_type == 1: # 正方体
            a = self.RandInt(1, 10)
            self.correct_answer = a * a * a
            self.numbers = [a]
            self.expression = f'求边长分别为{a}厘米的正方体的体积（单位：立方厘米）。'
        elif sub_type == 2: # 棱柱体
            a = self.RandInt(1, 10)
            h1 = self.RandInt(1, 10)
            h2 = self.RandInt(1, 10)
            self.correct_answer = a * h1 * h2 / 2
            self.numbers = [a, h1, h2]
            self.expression = f'求底边长为{a}厘米、底面高为{h1}厘米、高为{h2}厘米的三棱柱的体积（单位：立方厘米）。'
        elif sub_type == 3:
            r = self.RandInt(1, 10)
            h = self.RandInt(1, 10)
            self.correct_answer = decimal.Decimal(314 * r * r) * h / 100
            self.numbers = [r, h]
            self.expression = f'求半径为{r}厘米、高为{h}厘米的圆柱体体积（单位：立方厘米，π取3.14）。'
        elif sub_type == 4: # 圆锥体
            r = self.RandInt(1, 10)
            h = self.RandInt(1, 10)
            self.correct_answer = decimal.Decimal(round(314 * r * r * h / 3, 0)) / 100
            self.numbers = [r, h]
            self.expression = f'求半径为{r}厘米、高为{h}厘米的圆锥体体积（单位：立方厘米，π取3.14，保留2位小数）。'
        elif sub_type == 5: # 棱锥体
            s = self.RandInt(1, 100)
            h = self.RandInt(1, 10)
            self.correct_answer = decimal.Decimal(round(s * h / 3, 2) * 100) / 100
            print(self.correct_answer)
            self.numbers = [s, h]
            self.expression = f'求底面积为{s}平方厘米、高为{h}厘米的棱锥体的体积（单位：立方厘米），保留2位小数。'
        elif sub_type == 6: # 球体
            r = self.RandInt(1, 10)
            self.correct_answer = decimal.Decimal(round(314 * r * r * r * 4 / 3, 0)) / 100
            self.numbers = [r]
            self.expression = f'求半径为{r}厘米的球体体积（单位：立方厘米，π取3.14，保留2位小数）。'
        elif sub_type == 7: # 半球
            r = self.RandInt(1, 10)
            self.correct_answer = decimal.Decimal(round(314 * r * r * r * 2 / 3, 0)) / 100
            self.numbers = [r]
            self.expression = f'求半径为{r}厘米的半球体积（单位：立方厘米，π取3.14，保留2位小数）。'
        self.question = self.expression
        print(f'{self.question}正确答案：{self.correct_answer}')
        self.AfterGenerate()

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        try:
            user_answer = decimal.Decimal(self.user_answer)
            if user_answer == self.correct_answer:
                self.is_correct = True
            else:
                self.is_correct = False
        except:
            self.is_correct = False
        return self.is_correct

    def CheckTips(self):
        try:
            sub_type = self.subtype[0]
            if sub_type == 0:  # 长方体
                [a, b, c] = self.numbers
                self.check_tips = f'{a} × {b} × {c} = {self.correct_answer}'
            elif sub_type == 1:  # 正方体
                [a] = self.numbers
                self.check_tips = f'{a} × {a} × {a} = {self.correct_answer}'
            elif sub_type == 2:  # 棱柱体
                [a, h1, h2] = self.numbers
                self.check_tips = f'{a} × {h1} × {h2} ÷ 2 = {self.correct_answer}'
            elif sub_type == 3:
                [r, h] = self.numbers
                self.check_tips = f'π × {r} × {r} × {h} = {self.correct_answer}'
            elif sub_type == 4:  # 圆锥体
                [r, h] = self.numbers
                self.check_tips = f'1/3 × π × {r} × {r} × {h} = {self.correct_answer}'
            elif sub_type == 5: #
                print(self.correct_answer)
                [s, h] = self.numbers
                self.check_tips = f'1/3 × {s} × {h} = {self.correct_answer}'
            elif sub_type == 6:  # 球体
                [r] = self.numbers
                self.check_tips = f'4/3 × π × {r} × {r} × {r} = {self.correct_answer}'
            elif sub_type == 7:  # 半球
                [r] = self.numbers
                self.check_tips = f'2/3 × π × {r} × {r} × {r} = {self.correct_answer}'
        except:
            pass

    def AnswerTips(self):
        try:
            sub_type = self.subtype[0]
            if sub_type == 0:  # 长方体
                [a, b, c] = self.numbers
                self.answer_tips = f'{a} × {b} × {c} = {self.correct_answer}'
            elif sub_type == 1:  # 正方体
                [a] = self.numbers
                self.answer_tips = f'{a} × {a} × {a} = {self.correct_answer}'
            elif sub_type == 2:  # 棱柱体
                [a, h1, h2] = self.numbers
                self.answer_tips = f'{a} × {h1} × {h2} ÷ 2 = {self.correct_answer}'
            elif sub_type == 3:
                [r, h] = self.numbers
                self.answer_tips = f'π × {r} × {r} × {h} = {self.correct_answer}'
            elif sub_type == 4:  # 圆锥体
                [r, h] = self.numbers
                self.answer_tips = f'1/3 × π × {r} × {r} × {h} = {self.correct_answer}'
            elif sub_type == 5: #
                print(self.correct_answer)
                [s, h] = self.numbers
                self.answer_tips = f'1/3 × {s} × {h} = {self.correct_answer}'
            elif sub_type == 6:  # 球体
                [r] = self.numbers
                self.answer_tips = f'4/3 × π × {r} × {r} × {r} = {self.correct_answer}'
            elif sub_type == 7:  # 半球
                [r] = self.numbers
                self.answer_tips = f'2/3 × π × {r} × {r} × {r} = {self.correct_answer}'
        except:
            pass

class QuestionPower(QuestionLR):
    def __init__(self, subtype=[0]):
        self.power = [
            {'base': 2, 'exponent': range(17)},
            {'base': 3, 'exponent': range(9)},
            {'base': 4, 'exponent': range(9)},
            {'base': 5, 'exponent': range(7)},
            {'base': 6, 'exponent': range(4)},
            {'base': 7, 'exponent': range(4)},
            {'base': 8, 'exponent': range(6)},
            {'base': 9, 'exponent': range(4)},
            {'base': 10, 'exponent': range(9)},
            {'base': 11, 'exponent': range(4)},
            {'base': 13, 'exponent': range(3)},
            {'base': 14, 'exponent': range(3)},
            {'base': 15, 'exponent': range(3)},
            {'base': 16, 'exponent': range(5)},
        ]
        super().__init__(type=11, subtype=subtype)
        self.name = "乘幂运算"
        if subtype[0] == 0:
            self.comments = "乘幂求值：2**10 = 1024，答案输入：1024，或：=1024"
        elif subtype[0] == 1:
            comments = "乘幂加法：2**5 + 2**6 = 32 + 64 = 96，答案输入：96，或：= 96"
        elif subtype[0] == 2:
            self.comments = "乘幂减法：2**5 - 2**6 = 32 - 64 = -32，答案输入：-32，或：= -32"
        elif subtype[0] == 3:
            self.comments = "乘幂乘法：2**5 * 2**5 = 32 * 32 = 1024，答案输入：1024或：= 1024"
        elif subtype[0] == 4:
            self.comments = "乘幂乘法：2**10 * 2**5 = 2**5 = 32，答案输入：32或：= 32"
        elif subtype[0] == 5:
            self.comments = "乘幂的乘幂：(2**4)**4 = 2**(4*4) = 2**16 = 65536，答案输入：65536或：= 65536"

    def Generate(self):
        sub_type = self.subtype[0]
        self.BeforeGenerate()
        if sub_type == 0:
            self.GeneratePower()
        elif sub_type == 1 or sub_type == 2:
            self.GeneratePowerPS()
        elif sub_type == 3 or sub_type == 4:
            self.GeneratePowerMD()
        elif sub_type == 5:
            self.GeneratePowerPower()
        latex = r'${}$'.format(self.formula)
        print(latex)
        self.Latex2PNG(latex, self.png_file)
        self.AfterGenerate()
        print(self.question)

    def GeneratePower(self):
        power = self.power
        sub = random.choice(range(len(power)))
        a = power[sub]['base']
        n = random.choice(power[sub]['exponent'])
        # print(f'a = {a}, n = {n}')
        self.expression = f'{a} ** {n}'
        self.question = self.expression + ' = '
        self.formula = f'{a}' + '^' + '{' + f'{n}' + '} = '
        self.correct_answer = eval(self.expression)

    def GeneratePowerPS(self): # 加减法
        subtype = self.subtype[0]
        sign = '+'
        if subtype == 2:
            sign = '-'
        power = self.power
        sub = random.choice(range(len(power)))
        a = power[sub]['base']
        n1 = random.choice(power[sub]['exponent'])
        if n1 == 0:
            n2 = n1 + 1
        else:
            n2 = n1 - 1
        # print(f'a = {a}, n1 = {n1}, n2 = {n2}')
        self.expression = f'{a} ** {n1} {sign} {a} ** {n2}'
        self.question = self.expression + ' = '
        self.formula = f'{a}' + '^' + '{' + f'{n1}' + '}' + f'{sign}' + f'{a}' + '^' + '{' + f'{n2}' + '}' + ' = '
        self.correct_answer = eval(self.expression)
        self.numbers = [a, n1, n2]
        # self.a = a
        # self.n1 = n1
        # self.n2 = n2

    def GeneratePowerMD(self): # 乘除法
        subtype = self.subtype[0]
        sign = '*'
        latex_sign = '\\times'
        if subtype == 4:
            sign = '/'
            latex_sign = '\\div'
        power = self.power
        sub = random.choice(range(len(power)))
        a = power[sub]['base']
        n1 = random.choice(power[sub]['exponent'])
        n2 = random.choice(power[sub]['exponent'])
        if subtype == 3:
            n1 = int(n1 / 2)
            n2 = int(n2 / 2)
        elif subtype == 4:
            if n1 == 0:
                n1 = power[sub]['exponent'][-1]
                n2 = random.choice(power[sub]['exponent'])
            else:
                n2 = int(n1 / 2)
        self.expression = f'{a}**{n1} {sign} {a}**{n2}'
        self.question = self.expression + ' = '
        self.formula = f'{a}' + '^' + '{' + f'{n1}' + '}' + f'{latex_sign}' + f'{a}' + '^' + '{' + f'{n2}' + '}' + ' = '
        print(self.expression)
        self.correct_answer = eval(self.expression)
        self.numbers = [a, n1, n2]
        self.a = a
        self.n1 = n1
        self.n2 = n2

    def GeneratePowerPower(self):
        subtype = self.subtype[0]
        power = self.power
        sub = random.choice([0, 1, 8])
        a = power[sub]['base']
        n1 = max(1, int(random.choice(power[sub]['exponent']) / 4))
        n2 = self.RandInt(1, 4)
        self.expression = f'({a} ** {n1}) ** {n2}'
        self.question = self.expression + ' = '
        self.formula = f'\\left( {a}' + '^' + '{' + f'{n1}' + '}\\right)' + '^' + '{' + f'{n2}' + '}' + ' = '
        self.correct_answer = eval(self.expression)
        self.a = a
        self.n1 = n1
        self.n2 = n2

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        try:
            user_answer = Fraction(self.user_answer.strip().replace(' ', ''))
            if abs(user_answer - self.correct_answer) < 1e-3 :
                self.is_correct = True
            else:
                self.is_correct = False
        except:
            self.is_correct = False
        return self.is_correct

    def CheckTips(self):
        try:
            if self.subtype[0] == 0:
                self.check_tips = f'{self.expression} = {self.correct_answer}'
                return
            else:
                [a, n1, n2] = self.numbers
                r1 = a ** n1
                r2 = a ** n2

            if self.subtype[0] == 1:
                self.check_tips = f'{self.expression} = {r1} + {r2} = {self.correct_answer}'
            elif self.subtype[0] == 2:
                self.check_tips = f'{self.expression} = {r1} - {r2} = {self.correct_answer}'
            elif self.subtype[0] == 3:
                self.check_tips = f'{self.expression} = {r1} * {r2} = {self.correct_answer}'
            elif self.subtype[0] == 4:
                self.check_tips = f'{self.expression} = {r1} / {r2} = {self.correct_answer}'
            elif self.subtype[0] == 5:
                r1 = n1 * n2
                self.check_tips = f'{self.expression} = {a} ** {r1} = {self.correct_answer}'
        except:
            pass

    def AnswerTips(self):
        try:
            if self.subtype[0] == 0:
                self.answer_tips = f'{self.expression} = {self.correct_answer}'
            else:
                [a, n1, n2] = self.numbers
                r1 = a ** n1
                r2 = a ** n2

            if self.subtype[0] == 1:
                self.answer_tips = f'{self.expression} = {r1} + {r2} = {self.correct_answer}'
            elif self.subtype[0] == 2:
                self.answer_tips = f'{self.expression} = {r1} - {r2} = {self.correct_answer}'
            elif self.subtype[0] == 3:
                self.answer_tips = f'{self.expression} = {r1} * {r2} = {self.correct_answer}'
            elif self.subtype[0] == 4:
                self.answer_tips = f'{self.expression} = {r1} / {r2} = {self.correct_answer}'
            elif self.subtype[0] == 5:
                r1 = n1 * n2
                self.answer_tips = f'{self.expression} = {a} ** {r1} = {self.correct_answer}'
        except:
            pass

class QuestionEq1v1d(QuestionLR):
    def __init__(self, subtype=[0], range=[1, 5, 1, 20]):
        super().__init__(type=12, subtype=subtype, range=range)
        self.name = "求一元一次方程的解"
        self.comments = "输入未知数的解，可以包括中间过程。如：5，或：x = 5，或：x + 2 = 7, x = 5"

    def BeforeGenerate(self):
        super().BeforeGenerate()

    def AfterGenerate(self):
        super().AfterGenerate()

    def Generate(self):
        self.BeforeGenerate()
        subtype = self.subtype
        if subtype[0] == 0:
            if subtype[1] == 0:
                self.GenerateEq1v1d_00()
            elif subtype[1] == 1:
                self.GenerateEq1v1d_01()
            elif subtype[1] == 2:
                self.GenerateEq1v1d_02()
            elif subtype[1] == 3:
                self.GenerateEq1v1d_03()
        elif subtype[0] == 1:
            if subtype[1] == 0:
                self.GenerateEq1v1d_10()
            elif subtype[1] == 1:
                self.GenerateEq1v1d_11()
            elif subtype[1] == 2:
                self.GenerateEq1v1d_12()
            elif subtype[1] == 3:
                self.GenerateEq1v1d_13()
        elif subtype[0] == 2:
            pass

        try:
            self.question = f'{self.equation.lhs} = {self.equation.rhs}'.replace('*', '')
            print(self.question)
            latex = sp.latex(self.equation)
            latex = r'${}$'.format(latex).replace('frac', 'dfrac')
            print(latex)
            self.Latex2PNG(latex, self.png_file)
        except:
            pass
        self.AfterGenerate()

    def GenerateEq1v1d_00(self):
        min1 = self.range[0]
        max1 = self.range[1]
        min2 = self.range[2]
        max2 = self.range[3]
        while True:
            a = self.RandInt(min2, max2)
            if a != 0:
                break
        b = self.RandInt(min2, max2)
        self.numbers = [a, b]
        x = sp.symbols('x')
        equation = sp.Eq(x + a, b)
        self.correct_answer = sp.solve(equation, x)
        self.equation = equation

    def GenerateEq1v1d_01(self):
        min1 = self.range[0]
        max1 = self.range[1]
        min2 = self.range[2]
        max2 = self.range[3]
        while True:
            a = self.RandInt(min1, max1)
            if a != 0 and a != 1:
                break
        b = self.RandInt(min2, max2)
        self.numbers = [a, b]
        x = sp.symbols('x')
        equation = sp.Eq(a * x, b)
        self.correct_answer = sp.solve(equation, x)
        self.equation = equation

    def GenerateEq1v1d_02(self):
        min1 = self.range[0]
        max1 = self.range[1]
        min2 = self.range[2]
        max2 = self.range[3]
        while True:
            a = self.RandInt(min1, max1)
            if a != 0  and a != 1:
                break
        while True:
            b = self.RandInt(min2, max2)
            if b != 0:
                break
        c = self.RandInt(min2, max2)
        self.numbers = [a, b, c]
        x = sp.symbols('x')
        equation = sp.Eq(a * x + b, c)
        self.correct_answer = sp.solve(equation, x)
        self.equation = equation

    def GenerateEq1v1d_03(self):
        min1 = self.range[0]
        max1 = self.range[1]
        min2 = self.range[2]
        max2 = self.range[3]
        while True:
            a = self.RandInt(min1, max1)
            if a != 0:
                break
        while True:
            b = self.RandInt(min2, max2)
            if b != 0:
                break
        while True:
            c = self.RandInt(min1, max1)
            if c !=0 and c != a:
                break
        while True:
            d = self.RandInt(min2, max2)
            if d !=0:
                break
        self.numbers = [a, b, c, d]
        x = sp.symbols('x')
        equation = sp.Eq(a * x + b, c * x + d)
        self.correct_answer = sp.solve(equation, x)
        self.equation = equation

    def GenerateEq1v1d_10(self): # x + b/a = d/c
        min1 = self.range[0]
        max1 = self.range[1]
        min2 = self.range[2]
        max2 = self.range[3]
        while True:
            a = self.RandInt(min1, max1)
            b = self.RandInt(min2, max2)
            if a != 0 and b != 0 and self.GCD(a, b) == 1:
                break
        while True:
            c = self.RandInt(min1, max1)
            d = self.RandInt(min2, max2)
            if c != 0 and d != 0 and self.GCD(c, d) == 1:
                break
        x = sp.symbols('x')
        a1 = Fraction(b, a)
        b1 = Fraction(d, c)
        equation = sp.Eq(x + a1, b1)
        self.correct_answer = sp.solve(equation, x)
        self.numbers = [a1, b1]
        self.equation = equation

    def GenerateEq1v1d_11(self): # (b/a)x = d/c
        min1 = self.range[0]
        max1 = self.range[1]
        min2 = self.range[2]
        max2 = self.range[3]
        while True:
            a = self.RandInt(min1, max1)
            b = self.RandInt(min2, max2)
            if a != 0 and b != 0 and self.GCD(a, b) == 1:
                break
        while True:
            c = self.RandInt(min1, max1)
            d = self.RandInt(min2, max2)
            if c != 0 and d != 0 and self.GCD(c, d) == 1:
                break
        x = sp.symbols('x')
        a1 = Fraction(b, a)
        b1 = Fraction(d, c)
        equation = sp.Eq(a1 * x, b1)
        self.correct_answer = sp.solve(equation, x)
        self.numbers = [a1, b1]
        self.equation = equation

    def GenerateEq1v1d_12(self): # (b/a)x + d/c = e/a or e/c
        min1 = self.range[0]
        max1 = self.range[1]
        min2 = self.range[2]
        max2 = self.range[3]
        while True:
            a = self.RandInt(min1, max1)
            b = self.RandInt(min2, max2)
            if a != 0 and b != 0 and self.GCD(a, b) == 1:
                break
        while True:
            c = self.RandInt(min1, max1)
            d = self.RandInt(min2, max2)
            if c != 0 and d != 0 and self.GCD(c, d) == 1:
                break
        while True:
            e = self.RandInt(min2, max2)
            if e != 0:
                break
        x = sp.symbols('x')
        a1 = Fraction(b, a)
        b1 = Fraction(d, c)
        if self.RandInt(0, 1) == 0:
            c1 = Fraction(e, a)
        else:
            c1 = Fraction(e, c)
        equation = sp.Eq(a1 * x + b1, c1)
        self.correct_answer = sp.solve(equation, x)
        self.numbers = [a1, b1, c1]
        self.equation = equation

    def GenerateEq1v1d_13(self): # (b/a)x + d/c = (f/e)x + h/g
        min1 = self.range[0]
        max1 = self.range[1]
        min2 = self.range[2]
        max2 = self.range[3]
        while True:
            a = self.RandInt(min1, max1)
            b = self.RandInt(min2, max2)
            if a != 0 and b != 0 and self.GCD(a, b) == 1:
                break
        while True:
            c = self.RandInt(min1, max1)
            d = self.RandInt(min2, max2)
            if c != 0 and d != 0 and self.GCD(c, d) == 1:
                break
        while True:
            e = self.RandInt(min2, max2)
            if e != 0 and self.GCD(a, e) == 1:
                break
        while True:
            f = self.RandInt(min2, max2)
            if f != 0 and self.GCD(c, f) == 1:
                break
        x = sp.symbols('x')
        a1 = Fraction(b, a)
        b1 = Fraction(d, c)
        c1 = Fraction(e, a)
        d1 = Fraction(f, c)
        equation = sp.Eq(a1 * x + b1, c1 * x + d1)
        self.correct_answer = sp.solve(equation, x)
        self.numbers = [a1, b1, c1, d1]
        self.equation = equation

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        self.end_time = datetime.now()
        self.time_used = round((self.end_time - self.start_time).total_seconds(), 1)
        subtype = self.subtype[0]
        try:
            user_answer = Fraction(self.user_answer)
            print(user_answer, self.correct_answer)
            if user_answer in self.correct_answer:
                self.is_correct = True
            else:
                self.is_correct = False
            return self.is_correct
        except:
            self.is_correct = False
            return False

    def CheckTips(self):
        try:
            if self.subtype[0] in [0, 1]:
                self.CheckTips0()
        except:
            pass

    def CheckTips0(self):
        try:
            if self.subtype[1] == 0:
                [a, b] = self.numbers
                answer = sp.Rational(self.user_answer)
                self.check_tips = f'左式 = {answer} + {a} = {answer + a}；右式 = {b}；左式 ≠ 右式'
            elif self.subtype[1] == 1:
                [a, b] = self.numbers
                answer = sp.Rational(self.user_answer)
                self.check_tips = f'左式 = {a} × {answer}= {a * answer}；右式 = {b}；左式 ≠ 右式'
            elif self.subtype[1] == 2:
                [a, b, c] = self.numbers
                answer = sp.Rational(self.user_answer)
                if answer < 0:
                    str1 = f'× ({answer})'
                else:
                    str1 = f'× {answer}'
                if b < 0:
                    str2 = f'- {-b}'
                else:
                    str2 = f'+ {b}'
                self.check_tips = f'左式 = {a} {str1} {str2} = {a * answer + b}；右式 = {c}；左式 ≠ 右式'
            elif self.subtype[1] == 3:
                [a, b, c, d] = self.numbers
                answer = sp.Rational(self.user_answer)
                if answer < 0:
                    str1 = f'× ({answer})'
                else:
                    str1 = f'× {answer}'
                if b < 0:
                    str2 = f'- {-b}'
                else:
                    str2 = f'+ {b}'
                if d < 0:
                    str3 = f'- {-d}'
                else:
                    str3 = f'+ {d}'
                self.check_tips = f'左式 = {a} {str1} {str2} = {a * answer + b}；右式 = {c} {str1} {str3} = {c * answer + d}；左式 ≠ 右式'
        except:
            self.check_tips = '无效的答案'

    def AnswerTips(self):
        try:
            if self.subtype[0] in [0, 1]:
                self.AnswerTips0()
        except:
            pass

    def AnswerTips0(self):
        try:
            if self.subtype[1] == 0: # x + a = b
                [a, b] = self.numbers
                if a < 0:
                    str1 = f'+ {-a}'
                else:
                    str1 = f'- {a}'
                self.answer_tips = f'x = {b} {str1} = {self.correct_answer[0]}'
            elif self.subtype[1] == 1: # ax = b
                [a, b] = self.numbers
                if a == -1:
                    self.answer_tips = f'x = {self.correct_answer[0]}'
                elif a < 0:
                    str1 = f'÷ {-a}'
                    if type(a) == Fraction:
                        self.answer_tips = f'({-a})x = {-b} ⇒ x = {-b} {str1} = {self.correct_answer[0]}'
                    else:
                        self.answer_tips = f'{-a}x = {-b} ⇒ x = {-b} {str1} = {self.correct_answer[0]}'
                else:
                    str1 = f'÷ {a}'
                    self.answer_tips = f'x = {b} {str1} = {self.correct_answer[0]}'
            elif self.subtype[1] == 2: # ax + b = c
                [a, b, c] = self.numbers
                if a > 0:
                    if b < 0:
                        str2 = f'{c} + {-b}'
                    else:
                        str2 = f'{c} - {b}'
                    if a == 1:
                        str1 = 'x'
                    else:
                        if type(a) == Fraction:
                            str1 = f'({a})x'
                        else:
                            str1 = f'{a}x'
                    e = a
                    f = c - b
                else: # a < 0
                    if c < 0:
                        str2 = f'{b} + {-c}'
                    else:
                        str2 = f'{b} - {c}'
                    if a == -1:
                        str1 = 'x'
                    else:
                        if type(a) == Fraction:
                            str1 = f'({-a})x'
                        else:
                            str1 = f'{-a}x'
                    e = -a
                    f = b - c
                if e == 1:
                    self.answer_tips = f'{str1} = {str2} ⇒ x = {self.correct_answer[0]}'
                elif self.GCD(e, abs(f)) != 1:
                    self.answer_tips = f'{str1} = {str2} = {f} ⇒ x = {f} ÷ {e} = {self.correct_answer[0]}'
                else:
                    self.answer_tips = f'{str1} = {str2} = {f} ⇒ x = {self.correct_answer[0]}'
            elif self.subtype[1] == 3: # ax + b = cx + d
                [a, b, c, d] = self.numbers
                print(a, b, c, d)
                if a > c: # a - c > 0
                    str4 = f'{a - c}'
                    str3 = f'{d - b}'
                    e = a - c
                    f = d - b
                    if c < 0:
                        str1 = f'({a} + {-c})x'
                    else:
                        str1 = f'({a} - {c})x'
                    if b < 0:
                        str2 = f'{d} + {-b}'
                    else:
                        str2 = f'{d} - {b}'
                else: # a - c < 0
                    str4 = f'{c - a}'
                    str3 = f'{b - d}'
                    e = c - a
                    f = b - d
                    if a < 0:
                        str1 = f'({c} + {-a})x'
                    else:
                        str1 = f'({c} - {a})x'
                    if d < 0:
                        str2 = f'{b} + {-d}'
                    else:
                        str2 = f'{b} - {d}'

                if e == 1:
                    self.answer_tips = f'{str1} = {str2} ⇒ x = {self.correct_answer[0]}'
                else:
                    if type(e) == Fraction and e.denominator != 1:
                        str3 = f'({e})x'
                    else:
                        str3 = f'{e}x'
                    if self.GCD(e, abs(f)) != 1:
                        self.answer_tips = f'{str1} = {str2} = {f} ⇒ {str3} = {f} ⇒ x = {f} ÷ {e} = {self.correct_answer[0]}'
                    else:
                        self.answer_tips = f'{str1} = {str2} = {f} ⇒ {str3} = {f} ⇒ x = {self.correct_answer[0]}'
        except:
            pass

class QuestionEquation(QuestionLR):
    def __init__(self, subtype=[0], range=[1, 5, 1, 20]):
        super().__init__(type=12, subtype=subtype, range=range)
        self.name = "解方程"
        if self.subtype[0] == 0:
            self.comments = "输入未知数x的解，如：5，或者  x = 5"
        elif self.subtype[0] == 1:
            self.comments = "输入未知数x和y的解，可以包括推导过程。如：2x = 2, x = 1, 3y = -1, y = -1/3 或：1, -1/3"
        elif self.subtype[0] == 2:
            self.comments = "输入未知数x的解，可以包括推导过程。如：delta = 4 * 4 - 4 * 2 = 8, x1 = -2 - sqrt(2), x2 = -2 + sqrt(2)"

    def BeforeGenerate(self):
        super().BeforeGenerate()

    def AfterGenerate(self):
        super().AfterGenerate()

    def Generate(self):
        subtype = self.subtype[0]
        self.BeforeGenerate()
        if subtype == 0:
            self.Generate1v1d()
        if subtype == 1:
            self.Generate2v1d()
        if subtype == 2:
            self.Generate1v2d()
        self.AfterGenerate()

    def Generate1v1d(self):
        min1 = self.range[0]
        max1 = self.range[1]
        min2 = self.range[2]
        max2 = self.range[3]
        a = self.RandInt(min1, max1)
        b = self.RandInt(min2, max2)
        c = random.choice([0, self.RandInt(min1, max1)])
        d = random.choice([0, self.RandInt(min2, max2)])
        while a == 0:
            a = self.RandInt(min1, max1)
        while b == 0:
            b = self.RandInt(min2, max2)
        while c == a:
            c = self.RandInt(min1, max1)
        self.numbers = [a, b, c, d]
        x = sp.symbols('x')
        equation = sp.Eq(a * x + b, c * x + d)
        self.correct_answer = sp.solve(equation, x)
        if a == 1:
            term1 = 'x'
        elif a == -1:
            term1 = '-x'
        else:
            term1 = f'{a}x'
        if b > 0:
            term2 = f' + {b}'
        elif b < 0:
            term2 = f' - {-b}'
        if c == 1:
            term3 = 'x'
        elif c == -1:
            term3 = '-x'
        else:
            term3 = f'{c}x'
        if d > 0:
            term4 = f' + {d}'
        elif d < 0:
            term4 = f' - {-d}'
        if c == 0 and d == 0:
            term3 = '0'
            term4 = ''
        elif c == 0:
            term3 = ''
            term4 = f'{d}'
        elif d == 0:
            term4 = ''
        self.question = term1 + term2 + ' = ' + term3 + term4

    def Generate2v1d(self):
        min1 = self.range[0]
        max1 = self.range[1]
        min2 = self.range[2]
        max2 = self.range[3]
        try_numbers = 0
        while try_numbers < self.try_numbers:
            try_numbers += 1
            a1 = self.RandInt(min1, max1)
            b1 = self.RandInt(min1, max1)
            c1 = self.RandInt(min2, max2)
            a2 = self.RandInt(min1, max1)
            b2 = self.RandInt(min1, max1)
            c2 = self.RandInt(min2, max2)
            while a1 == 0:
                a1 = self.RandInt(min1, max1)
            while b1 == 0:
                b1 = self.RandInt(min1, max1)
            while c1 == 0:
                c1 = self.RandInt(min2, max2)
            while a2 == 0:
                a2 = self.RandInt(min1, max1)
            while b2 == 0:
                b2 = self.RandInt(min1, max1)
            while c2 == 0:
                c2 = self.RandInt(min2, max2)
            self.numbers = [a1, b1, c1, a2, b2, c2]
            x, y = sp.symbols('x y')
            eq1 = sp.Eq(a1 * x + b1 * y, c1)
            eq2 = sp.Eq(a2 * x + b2 * y, c2)
            try:
                solutions = sp.solve((eq1, eq2), (x, y), dict = True)
                if not solutions:
                    print('方程组无解')
                elif len(solutions) > 1:
                    print('方程组有无数多个解')
                else:
                    if a1 == 1:
                        term1 = 'x'
                    else:
                        term1 = f'{a1}x'
                    if a2 == 1:
                        term4 = 'x'
                    else:
                        term4 = f'{a2}x'
                    if b1 == 1:
                        term2 = '+ y'
                    else:
                        term2 = f'+ {b1}y'
                    if b2 == 1:
                        term5 = '+ y'
                    else:
                        term5 = f'+ {b2}y'
                    self.question = f'{term1} {term2} = {c1}\n{term4} {term5} = {c2}'
                    solution = solutions[0]
                    self.correct_answer = [solution[x], solution[y]]
                    print(self.question)
                    print(f"x = {solution[x]}")
                    print(f"y = {solution[y]}")
                    break
            except:
                self.range[0] -= 1
                self.range[1] += 1
                self.range[2] -= 1
                self.range[3] += 1

    def Generate1v2d(self):
        [min1, max1, min2, max2] = self.range
        try_numbers = 0
        while try_numbers < self.try_numbers:
            try_numbers += 1
            a = self.RandInt(min1, max1)
            while a == 0:
                a = self.RandInt(min1, max1)
            b = self.RandInt(min1, max1)
            c = self.RandInt(min2, max2)
            gcd = math.gcd(a, b, c)
            if gcd != 1:
                a = a // gcd
                b = b // gcd
                c = c // gcd
            if b * b - 4 * a * c < 0:
                continue
            self.numbers = [a, b, c]
            x = sp.symbols('x')
            eq = sp.Eq(a * x ** 2 + b * x + c, 0)

            solutions = sorted(sp.solve(eq, x))
            if not solutions:
                print('方程无解')
                continue
            if a == 1:
                stra = 'x²'
            elif a == -1:
                stra = '-x²'
            else:
                stra = f'{a}x²'
            if b == 0:
                strb = ''
            elif b == 1:
                strb = ' + x'
            elif b == -1:
                strb = ' - x'
            elif b < 0:
                strb = f' - {-b}x'
            else:
                strb = f' + {b}x'
            if c == 0:
                strc = ''
            elif c > 0:
                strc = f' + {c}'
            else:
                strc = f' - {-c}'
            self.question = f'{stra}{strb}{strc} = 0'
            self.correct_answer = solutions
            print(self.question)
            print(f"x = {solutions}")
            break
        else:
            self.range[0] -= 1
            self.range[1] += 1
            self.range[2] -= 1
            self.range[3] += 1

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        self.end_time = datetime.now()
        self.time_used = round((self.end_time - self.start_time).total_seconds(), 1)
        subtype = self.subtype[0]
        try:
            if subtype == 0:
                return self.JudgeAnswer1v1d()
            elif subtype == 1:
                return self.JudgeAnswer2v1d()
            elif subtype == 2:
                return self.JudgeAnswer1v2d()
        except:
            self.is_correct = False
            return False

    def JudgeAnswer1v1d(self):
        self.user_answer = re.sub(r"\s+", "", self.user_answer) # 删除空白符
        for opr in [',', '，', '＝']:
            self.user_answer == self.user_answer.replace(opr, '=')
        self.user_answer = self.user_answer.split('=')[-1]
        try:
            if sp.Rational(self.correct_answer[0]) == sp.Rational(self.user_answer):
                self.is_correct = True
                return True
            else:
                self.is_correct = False
                self.error_number += 1
                return False
        except:
            self.is_correct = False
            self.error_number += 1
            return False

    def Get2Numbers(self):
        user_input = self.user_input.replace(',', ' ').replace('  ', ' ')
        # 尝试将输入分割为两个部分
        parts = user_input.split()
        if len(parts) != 2:
            # 如果不是两个部分，检查是否可能包含逗号分隔
            if ',' in user_input:
                parts = user_input.split(',')
            else:
                print("输入格式错误，请输入两个数！")
        if len(parts) == 2:
            x_val = sp.Rational(parts[0])
            y_val = sp.Rational(parts[1])
            return x_val, y_val
        elif len(parts) == 1:
            x_val = sp.Rational(parts[0])
            return x_val, None
        elif len(parts) == 0:
            return None, None

    def JudgeAnswer2v1d(self):
        from sympy import sqrt
        # 提取用户输入中最后的x和y的值
        pattern = r'(x[^=]*=)([^,]+)|([^=]*y=)([^,]+)'
        matches = re.findall(pattern, self.user_input.replace(" ", ""))

        x_val = None
        y_val = None
        for match in matches:
            if match[0]:  # 匹配x=...的情况
                x_val = match[1].strip().split('=')[-1]
            elif match[2]:  # 匹配y=...的情况
                y_val = match[3].strip().split('=')[-1]
        try:
            x_val = sp.Rational(x_val)
            y_val = sp.Rational(y_val)
        except:
            print(f'x_val={x_val}, y_val={y_val}')
            self.is_correct = False
        # 检查是否成功提取了x和y的值
        if x_val is None or y_val is None:
            x_val, y_val = self.Get2Numbers()
        if self.correct_answer == [x_val, y_val]:
            self.is_correct = True
        else:
            self.is_correct = False
            self.user_answer = [x_val, y_val]
            self.user_input = f'x = {self.user_answer[0]}, y = {self.user_answer[1]}'
        return self.is_correct

    def JudgeAnswer1v2d(self):
        user_input = self.user_input.strip()
        numbers = []

        # 尝试匹配带x1=和x2=的格式（允许逗号后有空格）
        # 正则表达式模式
        pattern = r'(x1|x2)\s*=\s*(.*?)(?=,|$)'

        # 查找所有匹配项
        matches = re.findall(pattern, user_input)
        if matches:
            # 提取x1和x2后的内容
            result = {match[0]: match[1].strip() for match in matches}
            numbers = [result['x1'], result['x2']]
        else:
            # 处理直接输入两个数字的情况（逗号或空格分隔）
            parts = re.split(r'[,，]+', user_input)
            numbers = parts
        if len(self.correct_answer) != len(numbers):
            self.is_correct = False
            return self.is_correct
        self.user_answer = [sp.sympify(answer) for answer in numbers]
        self.is_correct = True
        for answer in self.user_answer:
            if not answer in self.correct_answer:
                self.is_correct = False

        i = 1
        self.user_input = ''
        for answer in self.user_answer:
            prefix = '' if i == 1 else ', '
            self.user_input += f'{prefix}x{i} = {answer}'
            i += 1
        return self.is_correct

    def CheckTips(self):
        try:
            if self.subtype[0] == 0:
                self.CheckTips1v1d()
            elif self.subtype[0] == 1:
                self.CheckTips2v1d()
            elif self.subtype[0] == 2:
                self.CheckTips1v2d()
            pass
        except:
            self.check_tips = '无效的答案'

    def CheckTips1v1d(self):
        x = sp.Rational(self.user_answer)
        a, b, c, d = tuple(self.numbers)
        self.check_tips = f''
        e = a * x + b
        f = c * x + d
        self.check_tips += f'左式 = {e}, 右式 = {f}, {e} ≠ {f}'

    def CheckTips2v1d(self):
        x = sp.Rational(self.user_answer[0])
        y = sp.Rational(self.user_answer[1])
        a1, b1, c1, a2, b2, c2 = tuple(self.numbers)
        self.check_tips = f''
        d1 = a1 * x + b1 * y
        d2 = a2 * x + b2 * y
        conj = '\n'
        if d1 != c1:
            self.check_tips += f'{conj}(1)左式 = {d1}, (1)右式 = {c1}, {d1} ≠ {c1}'
            conj = ', '
        if d2 != c2:
            self.check_tips += f'{conj}(2)左式 = {d2}, (2)右式 = {c2}, {d2} ≠ {c2}'

    def CheckTips1v2d(self):
        [a, b, c] = self.numbers
        if len(self.user_answer) == 2:
            [x1, x2] = self.user_answer
        elif len(self.user_answer) == 1:
            x1 = self.user_answer[0]
            x2 = x1
        else:
            return
        x1 = sp.sympify(x1)
        x2 = sp.sympify(x2)
        d1 = x1 + x2
        e1 = x1 * x2
        d2 = Fraction(-b, a)
        e2 = Fraction(c, a)
        self.check_tips = ''
        conj = ''
        if d1 != d2:
            self.check_tips += f'x1 + x2 ≠ {d2}'
            conj = ', '
        if e1 != e2:
            self.check_tips += f'{conj}x1⋅x2 ≠ {e2}'

    def AnswerTips(self):
        try:
            subtype = self.subtype[0]
            if subtype == 0:
                self.AnswerTips1v1d()
            elif subtype == 1:
                self.AnswerTips2v1d()
            elif subtype == 2:
                self.AnswerTips1v2d()
        except:
            pass

    def AnswerTips1v1d(self):
        a, b, c, d = tuple(self.numbers)
        if a > c:
            e = a - c
            f = d - b
        elif a < c:
            e = c - a
            f = b - d
        else:
            err = '方程系数不能为0'
            print(err)
        if e == 1:
            self.answer_tips = f'x = {f}'
        else:
            self.answer_tips = f'{e}x = {f} ⇒ x = {f} ÷ {e} = {self.correct_answer[0]}'

    def AnswerTips2v1d(self):
        x = sp.Rational(self.user_answer[0])
        y = sp.Rational(self.user_answer[1])
        a1, b1, c1, a2, b2, c2 = tuple(self.numbers)
        lcm = self.LCM(b1, b2)
        str1 = f'(1)式' if b1 == lcm else f'(1)式 × {lcm//b1}'
        str2 = f'(2)式' if b2 == lcm else f'(2)式 × {lcm//b2}'
        d1 = a1 * lcm // b1 - a2 * lcm // b2
        if d1 == 1:
            str3 = 'x'
        elif d1 == -1:
            str3 = '-x'
        else:
            str3 = f'{d1}x'
        self.answer_tips = f'{str1} - {str2}得到：{str3} = {c1 * lcm // b1 - c2 * lcm // b2}'
        self.answer_tips += f'⇒ x = {self.correct_answer[0]}, y = {self.correct_answer[1]}'

    def AnswerTips1v2d(self):
        [a, b, c] = self.numbers
        delta = b * b - 4 * a * c
        r1 = Fraction(-b, 2 * a)
        r2 = sp.sympify(sp.sqrt(delta) / (2 * a))
        if r2 == 0:
            self.answer_tips = f'delta = 0, x1 = x2 = {r1}'
        else:
            self.answer_tips = f'delta = {delta}, x1 = {r1 + r2}, x2 = {r1 - r2}'

class QuestionSequence(QuestionLR): # 数列题型
    def __init__(self, subtype):
        super().__init__(type=15, subtype = subtype)
        self.name = "数列问题"
        self.comments = "在(    )内填入数字。"

    def Generate(self):
        subtype = self.subtype[0]
        self.BeforeGenerate()

        if subtype == 0: # 等差数列
            self.GenerateAS()
        elif subtype == 1: # 等比数列
            self.GenerateGS()
        elif subtype == 2:  # 斐波那契
            self.GenerateFib()
        elif subtype == 3: # 质数数列
            self.GeneratePS()
        elif subtype == 4: # 平方差
            self.GenerateSD()
        elif subtype == 5: # 平方和
            self.GenerateSS()
        elif subtype == 6: # 二阶等差
            self.GenerateSOAS()
        elif subtype == 7: # 等差乘积
            self.GenerateASM()
        self.AfterGenerate()

    def GenerateAS(self): # 等差数列
        a0 = self.RandInt(-20, 20)
        while True:
            d = self.RandInt(-10, 10)
            if d != 0:
                break
        n = 3
        self.numbers = [a0, d, n]
        s = [a0 + i * d for i in range(n)]
        self.question = ''
        for i in range(n):
            self.question += f'{s[i]}, '
        self.question += ' (    )'
        self.correct_answer = a0 + n * d
        print(self.question, self.correct_answer)

    def GenerateGS(self): # 等比数列
        while True:
            a0 = self.RandInt(-5, 5)
            if a0 != 0:
                break
        while True:
            d = self.RandInt(-5, 5)
            if d != 0 and d != 1:
                break
        n = 3
        self.numbers = [a0, d, n]
        s = [a0 * d ** i for i in range(n)]
        self.question = ''
        for i in range(n):
            self.question += f'{s[i]}, '
        self.question += ' (    )'
        self.correct_answer = a0 * d**n
        print(self.question, self.correct_answer)

    def GenerateFib(self):  # 平方和
        a = self.RandInt(-5, 5)
        while True:
            b = self.RandInt(-3, 3)
            if b != a:
                break
        n = 4
        self.numbers = [a, b, n]
        s = [a, b]
        for i in range(2, n):
            s.append(s[i-2] + s[i-1])
        self.question = ''
        for i in range(n):
            self.question += f'{s[i]}, '
        self.question += ' (    )'
        self.correct_answer = s[n-2] + s[n-1]
        print(self.question, self.correct_answer)

    def GeneratePS(self): # 质数
        n0 = self.RandInt(1, 3)
        d = self.RandInt(1, 2)
        n = 4
        self.numbers = [n0, d, n]
        s = [self.primes[n0 + i * d] for i in range(n)]
        self.question = ''
        for i in range(n):
            self.question += f'{s[i]}, '
        self.question += ' (    )'
        self.correct_answer = self.primes[n0 + n * d]
        print(self.question, self.correct_answer)

    def GenerateSD(self): # 平方差
        a = self.RandInt(1, 6)
        while True:
            b = self.RandInt(1, 3)
            if b != a:
                break
        da = self.RandInt(1, 2)
        db = self.RandInt(1, 2)
        n = 4
        self.numbers = [a, b, da, db, n]
        s = [(a + i * da) ** 2 - (b + i * db) ** 2 for i in range(n)]
        self.question = ''
        for i in range(n):
            self.question += f'{s[i]}, '
        self.question += ' (    )'
        self.correct_answer = (a + n * da) ** 2 - (b + n * db) ** 2
        print(self.question, self.correct_answer)

    def GenerateSS(self): # 平方和
        a = self.RandInt(1, 6)
        while True:
            b = self.RandInt(1, 3)
            if b != a:
                break
        da = self.RandInt(1, 2)
        db = self.RandInt(1, 2)
        n = 5
        self.numbers = [a, b, da, db, n]
        sa = [a + i*da for i in range(n+1)]
        sb = [b + i*db for i in range(n+1)]
        sd = [sa[i] ** 2 + sb[i] ** 2 for i in range(n+1)]
        self.question = ''
        for i in range(n):
            self.question += f'{sd[i]}, '
        self.question += ' (    )'
        self.correct_answer = sd[n]

        print(self.question, self.correct_answer)

    def GenerateSOAS(self): # 二阶等差数列
        a0 = self.RandInt(1, 10)
        while True:
            d1 = self.RandInt(1, 5)
            if d1 != 0:
                break
        while True:
            d2 = self.RandInt(1, 5)
            if d2 != 0:
                break
        n = 5
        self.numbers = [a0, d1, d2, n]
        s = [a0 + i * d1 + i*(i-1)//2*d2 for i in range(n+1)]
        self.question = ''
        for i in range(n):
            self.question += f'{s[i]}, '
        self.question += ' (    )'
        self.correct_answer = s[-1]
        print(self.question, self.correct_answer)

    def GenerateASM(self): # 等差数列
        a0 = self.RandInt(1, 5)
        b0 = self.RandInt(1, 5)
        if a0 > b0:
            a0, b0 = b0, a0
        while True:
            da = self.RandInt(1, 3)
            if da != 0:
                break
        while True:
            db = self.RandInt(1, 3)
            if db != 0:
                break
        n = 4
        self.numbers = [a0, b0, da, db, n]
        s = [(a0+i*da)*(b0+i*db) for i in range(n+1)]
        self.question = ''
        for i in range(n):
            self.question += f'{s[i]}, '
        self.question += ' (    )'
        self.correct_answer = s[n]
        print(self.question, self.correct_answer)

    def CheckTips(self):
        try:
            subtype = self.subtype[0]
            if subtype == 0:
                self.CheckTipsAS()
            elif subtype == 1:
                self.CheckTipsGS()
            elif subtype == 2:
                self.CheckTipsFib()
            elif subtype == 3:
                self.CheckTipsPS()
            elif subtype == 4:
                self.CheckTipsSD()
            elif subtype == 5:
                self.CheckTipsSS()
            elif subtype == 6:
                self.CheckTipsSOAS()
            elif subtype == 7:
                self.CheckTipsASM()
        except:
            self.check_tips = '无效的答案'

    def CheckTipsAS(self):
        a0, d, n = self.numbers
        s = [a0 + i * d for i in range(n)]
        self.user_answer = int(self.user_answer)
        if d >= 0:
            if s[0] >= 0:
                self.check_tips = f'{s[1]} - {s[0]} = {d}'
            else:
                self.check_tips = f'{s[1]} - ({s[0]}) = {d}'
            self.check_tips += f'，{s[n-1]} + {d} ≠ {self.user_answer}'
        else:
            if s[1] >= 0:
                self.check_tips = f'{s[0]} - {s[1]} = {-d}'
            else:
                self.check_tips = f'{s[0]} - ({s[1]}) = {-d}'
            self.check_tips += f'，{s[n-1]} - {-d} ≠ {self.user_answer}'

    def CheckTipsGS(self):
        [a0, d, n] = self.numbers
        s = [a0 * d ** i for i in range(n)]
        self.user_answer = int(self.user_answer)
        if s[0] >= 0:
            self.check_tips = f'{s[1]} ÷ {s[0]} = {d}，'
        else:
            self.check_tips = f'{s[1]} ÷ ({s[0]}) = {d}，'
        if d > 0:
            self.check_tips += f'{s[n-1]} × {d} ≠ {self.user_answer}'
        else:
            self.check_tips += f'{s[n-1]} × ({d}) ≠ {self.user_answer}'

    def CheckTipsFib(self):
        a, b, n = self.numbers
        s = [a, b]
        self.user_answer = int(self.user_answer)
        for i in range(2, n):
            s.append(s[i-2] + s[i-1])
        if s[1] >= 0:
            self.check_tips = f'{s[2]} = {s[0]} + {s[1]}'
        else:
            self.check_tips = f'{s[2]} = {s[0]} + ({s[1]})'
        if s[n-1] >= 0:
            self.check_tips += f'{s[n-2]} + {s[n-1]} ≠ {self.user_answer}'
        else:
            self.check_tips += f'{s[n - 2]} + ({s[n - 1]}) ≠ {self.user_answer}'

    def CheckTipsPS(self):
        n0, d, n = self.numbers
        si = [n0 + i * d for i in range(n+1)]
        sp = [self.primes[n0 + i * d] for i in range(n+1)]
        self.user_answer = int(self.user_answer)
        self.check_tips = f'{sp[:-1]})分别是第{si[:-1]}个质数，第{si[n]}个质数不是{self.user_answer}'

    def CheckTipsSD(self):
        a, b, da, db, n = self.numbers
        sa = [a + i*da for i in range(n+1)]
        sb = [b + i*db for i in range(n+1)]
        sd = [sa[i] ** 2 - sb[i] ** 2 for i in range(n+1)]
        self.user_answer = int(self.user_answer)
        self.check_tips = f'{sd[0]} = {sa[0]}*{sa[0]} - {sb[0]}*{sb[0]}'
        self.check_tips += f'，{sd[1]} = {sa[1]}*{sa[1]} - {sb[1]}*{sb[1]}'
        self.check_tips += f'\n{sd[2]} = {sa[2]}*{sa[2]} - {sb[2]}*{sb[2]}'
        self.check_tips += f'，{sd[3]} = {sa[3]}*{sa[3]} - {sb[3]}*{sb[3]}'
        self.check_tips += f'，{sa[n]}*{sa[n]} - {sb[n]}*{sb[n]} ≠ {self.user_answer}'

    def CheckTipsSS(self):
        a, b, da, db, n = self.numbers
        sa = [a + i*da for i in range(n+1)]
        sb = [b + i*db for i in range(n+1)]
        sd = [sa[i] ** 2 + sb[i] ** 2 for i in range(n+1)]
        self.user_answer = int(self.user_answer)
        self.check_tips = f'{sd[0]} = {sa[0]}*{sa[0]} + {sb[0]}*{sb[0]}'
        self.check_tips += f'，{sd[1]} = {sa[1]}*{sa[1]} + {sb[1]}*{sb[1]}'
        self.check_tips += f'\n{sd[2]} = {sa[2]}*{sa[2]} + {sb[2]}*{sb[2]}'
        self.check_tips += f'，{sd[3]} = {sa[3]}*{sa[3]} + {sb[3]}*{sb[3]}'
        self.check_tips += f'，{sa[n]}*{sa[n]} + {sb[n]}*{sb[n]} ≠ {self.user_answer}'

    def CheckTipsSOAS(self): # 二阶等差数列
        a0, d1, d2, n = self.numbers
        s = [a0 + i * d1 + i*(i-1)//2*d2 for i in range(n+1)]
        ds = [s[i+1] - s[i] for i in range(n)]
        dds = [ds[i+1] - ds[i] for i in range(n-1)]
        self.user_answer = int(self.user_answer)
        self.check_tips = f'一阶差分数列：{ds[:-1]}，二阶差分数列：{dds[:-1]}，{s[n-1]} + {ds[n-2]} + {dds[n-2]} ≠ {self.user_answer}'

    def CheckTipsASM(self): # 二阶等差数列
        a0, b0, da, db, n = self.numbers
        sa = [a0 + i * da for i in range(n+1)]
        sb = [b0 + i * db for i in range(n+1)]
        s = [sa[i] * sb[i] for i in range(n+1)]
        self.user_answer = int(self.user_answer)
        self.check_tips = ''
        for i in range(n):
            self.check_tips += f'{s[i]} = {sa[i]} * {sb[i]}，'
        self.check_tips += f'{sa[n]} * {sb[n]} ≠ {self.user_answer}'

    def AnswerTips(self):
        try:
            if self.subtype[0] == 0:
                self.AnswerTipsAS()
            elif self.subtype[0] == 1:
                self.AnswerTipsGS()
            elif self.subtype[0] == 2:
                self.AnswerTipsFib()
            elif self.subtype[0] == 3:
                self.AnswerTipsPS()
            elif self.subtype[0] == 4:
                self.AnswerTipsSD()
            elif self.subtype[0] == 5:
                self.AnswerTipsSS()
            elif self.subtype[0] == 6:
                self.AnswerTipsSOAS()
            elif self.subtype[0] == 7:
                self.AnswerTipsASM()
        except:
            self.answer_tips = '无效的答案'

    def AnswerTipsAS(self):
        a0, d, n = self.numbers
        s = [a0 + i * d for i in range(n)]
        if d >= 0:
            if s[0] >= 0:
                self.answer_tips = f'{s[1]} - {s[0]} = {d}'
            else:
                self.answer_tips = f'{s[1]} - ({s[0]}) = {d}'
            self.answer_tips += f'，正确答案 = {s[n-1]} + {d} = {self.correct_answer}'
        else:
            if s[1] >= 0:
                self.answer_tips = f'{s[0]} - {s[1]} = {-d}'
            else:
                self.answer_tips = f'{s[0]} - ({s[1]}) = {-d}'
            self.answer_tips += f'，正确答案 = {s[n-1]} - {-d} = {self.correct_answer}'

        print(self.answer_tips)

    def AnswerTipsGS(self):
        [a0, d, n] = self.numbers
        s = [a0 * d ** i for i in range(n)]
        self.user_answer = int(self.user_answer)
        if s[0] >= 0:
            self.answer_tips = f'{s[1]} ÷ {s[0]} = {d}，'
        else:
            self.answer_tips = f'{s[1]} ÷ ({s[0]}) = {d}，'
        if d > 0:
            self.answer_tips += f'{s[n-1]} × {d} = {self.correct_answer}'
        else:
            self.answer_tips += f'{s[n-1]} × ({d}) = {self.correct_answer}'

    def AnswerTipsFib(self):
        a, b, n = self.numbers
        s = [a, b]
        self.user_answer = int(self.user_answer)
        for i in range(2, n):
            s.append(s[i-2] + s[i-1])
        if s[1] >= 0:
            self.answer_tips = f'{s[2]} = {s[0]} + {s[1]}'
        else:
            self.answer_tips = f'{s[2]} = {s[0]} + ({s[1]})'
        if s[n-1] >= 0:
            self.answer_tips += f'正确答案 = {s[n-2]} + {s[n-1]} = {self.correct_answer}'
        else:
            self.answer_tips += f'正确答案 = {s[n - 2]} + ({s[n - 1]}) = {self.correct_answer}'

    def AnswerTipsPS(self):
        n0, d, n = self.numbers
        si = [n0 + i * d for i in range(n+1)]
        sp = [self.primes[n0 + i * d] for i in range(n+1)]
        self.user_answer = int(self.user_answer)
        self.answer_tips = f'{sp[:-1]}分别是第{si[:-1]}个质数，第{si[n]}个质数为{self.correct_answer}'

    def AnswerTipsSD(self):
        a, b, da, db, n = self.numbers
        sa = [a + i*da for i in range(n+1)]
        sb = [b + i*db for i in range(n+1)]
        sd = [sa[i] ** 2 - sb[i] ** 2 for i in range(n+1)]
        print(sd)
        dsd = [sd[i+1] - sd[i] for i in range(n)]
        ddsd = [dsd[i+1] - dsd[i] for i in range(n-1)]
        self.answer_tips = f'方法一：正确答案 = {sa[n]}*{sa[n]} - {sb[n]}*{sb[n]} = {self.correct_answer}'
        self.answer_tips += f'\n方法二：一阶差分数列为：{dsd[:-1]}，二阶差分数列为：{ddsd[:-1]}'
        # str_dsd = f'{dsd[n-2]}' if dsd[n-1] >= 0 else f'({dsd[n-2]})'
        # str_ddsd = f'{ddsd[n-2]}' if ddsd[n-2] >= 0 else f'({ddsd[n-2]})'
        str_dsd = self.StrNumber(dsd[n-2])
        str_ddsd = self.StrNumber(ddsd[n-2])
        self.answer_tips += f'，正确答案 = {sd[n-1]} + {str_dsd} + {str_ddsd} = {self.correct_answer}'

    def AnswerTipsSS(self):
        a, b, da, db, n = self.numbers
        sa = [a + i*da for i in range(n+1)]
        sb = [b + i*db for i in range(n+1)]
        sd = [sa[i] ** 2 + sb[i] ** 2 for i in range(n+1)]
        print(sd)
        dsd = [sd[i+1] - sd[i] for i in range(n)]
        ddsd = [dsd[i+1] - dsd[i] for i in range(n-1)]
        self.answer_tips = f'方法一：正确答案 = {sa[n]}*{sa[n]} + {sb[n]}*{sb[n]} = {self.correct_answer}'
        self.answer_tips += f'\n方法二：一阶差分数列为：{dsd[:-1]}，二阶差分数列为：{ddsd[:-1]}'
        # str_dsd = f'{dsd[n-2]}' if dsd[n-2] >= 0 else f'({dsd[n-2]})'
        # str_ddsd = f'{ddsd[n-2]}' if ddsd[n-2] >= 0 else f'({ddsd[n-2]})'
        str_dsd = self.StrNumber(dsd[n-2])
        str_ddsd = self.StrNumber(ddsd[n-2])
        self.answer_tips += f'，正确答案 = {sd[n-1]} + {str_dsd} + {str_ddsd} = {self.correct_answer}'

    def AnswerTipsSOAS(self): # 二阶等差数列
        a0, d1, d2, n = self.numbers
        s = [a0 + i * d1 + i*(i-1)//2*d2 for i in range(n+1)]
        ds = [s[i+1] - s[i] for i in range(n)]
        dds = [ds[i+1] - ds[i] for i in range(n-1)]
        self.answer_tips = f'一阶差分数列：{ds[:-1]}，二阶差分数列：{dds[:-1]}，{s[n-1]} + {ds[n-2]} + {dds[n-2]} = {self.correct_answer}'

    def AnswerTipsASM(self): # 二阶等差数列
        a0, b0, da, db, n = self.numbers
        sa = [a0 + i * da for i in range(n+1)]
        sb = [b0 + i * db for i in range(n+1)]
        s = [sa[i] * sb[i] for i in range(n+1)]
        self.answer_tips = f'{sa[n]} * {sb[n]} = {self.correct_answer}'