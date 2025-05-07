import random
import itertools
import re
from fractions import Fraction
from datetime import datetime
from itertools import combinations
import sympy as sp
import ast

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
        if a > b:
            return random.randint(b, a)
        else:
            return random.randint(a, b)

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
        # self.name = ''
        self.numbers = []
        self.operators = []
        self.question = ''
        self.start_time = ''
        self.solution = ''
        self.time_used = ''
        self.user_input = ''
        self.user_answer = ''
        self.user_rusults = []

    def Generate(self):
        pass

    def AfterGenerate(self):
        self.start_time = datetime.now()
        pass

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
            # print(self.user_results)
        except:
            pass
        return True

    def ProcessCalculation(self):
        print(self.expression)
        return


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
        self.Generate()

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
        self.Generate()

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

    def GCD(self, a, b):
        while b:
            a, b = b, a % b
        return a

    def LCM(self, a, b):
        return a * b // self.GCD(a, b)

    def Generate(self):
        """生成一个10到1000之间的随机数，保证有至少3个质因数"""
        # print(f'self.subtype = {self.subtype}')
        subtype = self.subtype[0]
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
        if subtype == 0:
            self.user_answer = self.user_input.strip().replace('*', ' ')
            self.user_answer = self.user_answer.split()
            for i in range(len(self.user_answer)):
                self.user_answer[i] = int(self.user_answer[i])
        else:
            self.user_answer = self.user_input.strip().replace('*', ' ')
            self.user_answer = self.user_answer.replace(',', ' ')
            self.user_answer = self.user_answer.replace('，', ' ')
            self.user_answer = self.user_answer.replace(' ', '=')
            self.user_answer = self.user_answer.split('=')[-1]
            self.user_answer = int(self.user_answer)

    def JudgeAnswer(self):
        # print(f'JudgeAnswer() in QuestionFactor')
        super().BeforeJudgeAnswer()
        self.BeforeJudgeAnswer()
        self.end_time = datetime.now()
        self.time_used = round((self.end_time - self.start_time).total_seconds(), 1)

        subtype = self.subtype[0]
        if subtype == 0:
            return self.JudgeAnswerQFactor()
        else:
            self.is_correct = self.user_answer == self.correct_answer
            # print(self.is_correct)
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
        for answer in self.user_answer:
            if not self.IsPrime(answer):
                l.append(answer)
        if len(l) > 0:
            err = f'{l}中的数不是质数；'
        ret = eval(expr)
        if not ret == self.numbers[0]:
            err += f'{expr} = {ret} != {self.numbers[0]}'
        self.check_tips = f'错误：质因数分解不完整。{err}'


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
        # print(range)
        self.name = "计算24点"
        self.comments = "输入表达式，使得表达式的值为24。如: (5+3)*(8-5)。"
        self.Generate()

    def Generate(self):
        self.BeforeGenerate()
        self.Question()
        self.Answer()
        self.AfterGenerate()

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
        self.Generate()

    def Generate(self):
        self.BeforeGenerate()
        self.Question()
        self.Answer()
        self.AfterGenerate()

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
        print(type(self.correct_answer))
        print(type(self.user_answer))
        for opr in ['+', '-', '*', '/', '=',]:
            self.user_answer == self.user_answer.replace(opr, ' ')
        self.user_answer = self.user_answer.split(' ')[-1]
        if self.correct_answer == int(self.user_answer):
            self.is_correct = True
            return True
        else:
            self.is_correct = False
            self.error_number += 1
            return False

    def Answer(self):
        print(f'self.expression = {self.expression}')
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
        # print(self.user_answer)
        tips = ''
        if type(self.user_answer) == str:
            self.user_answer = eval(self.Fraction(self.user_answer))
        user_answer = abs(self.user_answer)
        correct_answer = abs(self.correct_answer)
        if self.IsSignError():
            tips += '1. 正负号'
        elif user_answer % 10 != correct_answer % 10:
            tips += '2. 个位数'
        elif len(str(user_answer)) != len(str(correct_answer)):
            tips += '3. 总位数'
        elif user_answer // 10 != correct_answer // 10:
            tips += '4. 进借位'
        self.check_tips = f'{tips}'
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
        self.Generate()

    def BeforeGenerate(self):
        super().BeforeGenerate()
        self.numbers = []
        self.operators = []
        subtype = self.subtype[0]
        min_val = self.range[0]
        max_val = self.range[1]

        if subtype < 0 or subtype > 7:
            print(f"不支持的子类型: {subtype}")
            return False

        if subtype == 7:
            subtype = self.RandInt(0, 5)
            self.subtype2 = [subtype]
            # print(f'subtpe = {subtype}')
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
            print(m, n)
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
        self.Generate()

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

class QuestionEquation(QuestionLR):
    def __init__(self, subtype=[0, 0], range=[1, 5, 1, 20]):
        super().__init__(type=1, subtype=subtype, range=range)
        self.name = "解方程"
        if self.subtype[0] == 0:
            self.comments = "输入未知数x的解，如：5，或者  x = 5"
        elif self.subtype[0] == 1:
            self.comments = "输入未知数x和y的解，可以包括推导过程。如：2x = 2, x = 1, 3y = -1, y = -1/3 "
        elif self.subtype[0] == 2:
            self.comments = "输入未知数x的解，可以包括推导过程。如：delta = 4 * 4 - 4 * 2 = 8, x1 = -2 - sqrt(2), x2 = -2 + sqrt(2)"
        self.Generate()

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
        while True:
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
                pass

    def Generate1v2d(self):
        min1 = self.range[0]
        max1 = self.range[1]
        min2 = self.range[2]
        max2 = self.range[3]
        while True:
            a = self.RandInt(min1, max1)
            b = self.RandInt(min1, max1)
            c = self.RandInt(min2, max2)
            while a == 0:
                a = self.RandInt(min1, max1)
            b = self.RandInt(min1, max1)
            c = self.RandInt(min2, max2)
            if b * b - 4 * a * c < 0:
                continue
            self.numbers = [a, b, c]
            x = sp.symbols('x')
            eq = sp.Eq(a * x ** 2 + b * x + c, 0)

            solutions = sorted(sp.solve(eq, x))
            if not solutions:
                print('方程组无解')
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

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        self.end_time = datetime.now()
        self.time_used = round((self.end_time - self.start_time).total_seconds(), 1)
        subtype = self.subtype[0]
        if subtype == 0:
            return self.JudgeAnswer1v1d()
        elif subtype == 1:
            return self.JudgeAnswer2v1d()
        elif subtype == 2:
            return self.JudgeAnswer1v2d()

    def JudgeAnswer1v1d(self):
        self.user_answer = re.sub(r"\s+", "", self.user_answer) # 删除空白符
        for opr in [',', '，', '＝']:
            self.user_answer == self.user_answer.replace(opr, '=')
        print(self.user_answer)
        self.user_answer = self.user_answer.split('=')[-1]
        if float(self.correct_answer[0]) == float(eval(self.user_answer)):
            self.is_correct = True
            return True
        else:
            self.is_correct = False
            self.error_number += 1
            return False

    def get_two_numbers(self):
        user_input = self.user_input.replace(',', ' ').replace('  ', ' ')
        print(user_input)
        # 尝试将输入分割为两个部分
        parts = user_input.split()
        if len(parts) != 2:
            # 如果不是两个部分，检查是否可能包含逗号分隔
            if ',' in user_input:
                parts = user_input.split(',')
            else:
                print("输入格式错误，请输入两个数！")
        x_val = sp.Rational(parts[0])
        y_val = sp.Rational(parts[1])
        return x_val, y_val

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
            x_val, y_val = self.get_two_numbers()
            print(x_val, y_val)
        if self.correct_answer == [x_val, y_val]:
            self.is_correct = True
        else:
            self.is_correct = False
        return self.is_correct

    def JudgeAnswer1v2d(self):
        user_input = self.user_input.strip()
        print(user_input)
        numbers = []

        # 尝试匹配带x1=和x2=的格式（允许逗号后有空格）
        # 正则表达式模式
        pattern = r'(x1|x2)\s*=\s*(.*?)(?=,|$)'

        # 查找所有匹配项
        matches = re.findall(pattern, user_input)
        print(matches)
        if matches:
            # 提取x1和x2后的内容
            result = {match[0]: match[1].strip() for match in matches}
            print(result)
            numbers = [result['x1'], result['x2']]
            print(numbers)
        else:
            # 处理直接输入两个数字的情况（逗号或空格分隔）
            parts = re.split(r'[,\s]+', user_input)
            parts = [p for p in parts if p]  # 去除空字符串
            numbers = parts
        print(numbers)
        if len(self.correct_answer) != len(numbers):
            self.is_correct = False
            return self.is_correct
        correct_answer = [str(answer).strip() for answer in self.correct_answer]
        print(correct_answer)
        print(numbers)
        user_answer = [str(answer).strip() for answer in numbers]
        print(user_answer)
        self.is_correct = True
        for answer in user_answer:
            if not answer in correct_answer:
                self.is_correct = True
        return self.is_correct

    def CheckTips(self):
        pass

    def AnswerTips(self):
        subtype = self.subtype[0]
        if subtype == 0:
            self.AnswerTips1v1d()
        elif subtype == 1:
            self.AnswerTips2v1d()

    def AnswerTips1v1d(self):
        a = self.numbers[0]
        b = self.numbers[1]
        c = self.numbers[2]
        d = self.numbers[3]
        if a > c:
            e = a - c
            f = d - b
        elif a < c:
            e = c - a
            f = b - d
        else:
            err = '方程系数不能为0'
            print(err)
        self.answer_tips = f'{e}x = {f}, x = {f} / {e} = {self.correct_answer[0]}'

    def AnswerTips2v1d(self):
        pass