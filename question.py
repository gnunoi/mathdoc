import random
import numpy as np
import itertools
import re
from fractions import Fraction
from datetime import datetime
from collections import Counter
from itertools import combinations

"""
类名称: Question
说明：各种题目的基础类

变量: 
answer_tips: 答题提示
check_tips: 检查提示
comments: 答题说明
correct_answer: 正确答案
end_time: 答题结束时间
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


ConvertToFraction(): 将表达式中的数字替换为分数，确保计算严格准确
ProcessUserInput(): 处理用户输入，将中文符号替换为英文符号，删除空白符
CheckUserInput(): 检查用户输入的表达式是否包含了全部数字
ProcessCalculation(): 显示完整的计算步骤

ClassName(): 获取类名称
SuperName(): 获取父类名称
"""
class Question():
    def __init__(self, type=0, subtype=[0], range=[1, 10]):
        self.answer_tips = None
        self.check_tips = None
        self.correct_answer = None
        self.comments = None
        self.end_time = None
        self.expression = None
        self.is_correct = False
        self.name = None
        self.numbers = []
        self.operators = []
        self.question = None
        self.range = range
        self.start_time = None
        self.solution = None
        self.subtype = subtype
        self.time_used = None
        self.type = type
        self.user_input = None
        self.user_answer = None
        self.user_results = None


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
        return np.random.randint(a, b)

    def BeforeGenerate(self):
        """
        以下变量不能重新初始化
        comments
        name
        type
        subtype
        range
        """
        self.answer_tips = None
        self.check_tips = None
        self.correct_answer = None
        # self.comments = None
        self.end_time = None
        self.expression = None
        self.is_correct = False
        # self.name = None
        self.numbers = []
        self.operators = []
        self.question = None
        self.start_time = None
        self.solution = None
        self.time_used = None
        self.user_input = None
        self.user_answer = None
        self.user_rusults = None

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
        self.check_tips = None
        self.answer_tips = None
        self.solution = None
        self.is_correct = False

    def JudgeAnswer(self):
        self.BeforeJudgeAnswer()
        self.end_time = datetime.now()
        self.time_used = round((self.end_time - self.start_time).total_seconds(), 1)
        self.start_time = datetime.now()
        if self.correct_answer in [self.user_answer] + self.user_results:
            self.is_correct = True
            return True
        else:
            self.is_correct = False
            return False

    def ConvertToFraction(self, expression):
        """
        将表达式中的每个数字转换为 Fraction 类型，并形成新的表达式。

        参数:
            expression (str): 输入的数学表达式，例如 "3 + 4 * 5.5"

        返回:
            str: 转换后的表达式，例如 "Fraction(3) + Fraction(4) * Fraction(5.5)"
        """
        # 使用正则表达式匹配表达式中的数字（包括整数、浮点数和科学计数法）
        pattern = r'(?<!\w)(-?\d+\.?\d*|\.\d+)([eE][-+]?\d+)?(?!\w)'

        # 替换每个数字为 Fraction(数字)
        def replace_with_fraction(match):
            number = match.group(0)
            return f"Fraction('{number}')"

        new_expression = re.sub(pattern, replace_with_fraction, expression)
        # print(new_expression)
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
            result = eval(self.ConvertToFraction(self.user_answer))
            self.user_results.append(result)
            print(self.results)
        except:
            pass
        return True

    def ProcessCalculation(self):
        print(self.expression)
        return


"""
类名称：Question24Point
题目类型：计算24点
"""
class Question24Point(Question):
    def __init__(self, range=[1, 10]):
        super().__init__(type=0, subtype=[0], range=range)
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
            self.numbers = [random.randint(min_val, max_val) for _ in range(4)]
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
                        converted_expr = self.ConvertToFraction(expr)
                        if eval(converted_expr) == 24:
                            return expr
                    except ZeroDivisionError:
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
        # print('计算24点：AnswerTips()')
        self.answer_tips = f'{self.Validate24Point()}'
        return self.answer_tips

    def UsedAllNumbers(self):
        # 使用正则表达式提取表达式中的所有数字
        numbers_in_expression = re.findall(r'\d+', self.user_answer)

        # 将提取的数字字符串转换为整数
        numbers_in_expression = [int(num_str) for num_str in numbers_in_expression]

        # 检查两个数组是否完全相同（数量和内容都相同，顺序可以不同）
        print(sorted(numbers_in_expression))
        print(sorted(self.numbers))
        return sorted(numbers_in_expression) == sorted(self.numbers)

    def JudgeAnswer(self):
        if not self.UsedAllNumbers():
            self.is_correct = False
            return False
        return super().JudgeAnswer()


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
            self.question = expr.replace('*', '×') + " = "
            return self.expression
        except:
            print('无法生成题目')
            return None

    def Answer(self):
        self.correct_answer = eval(self.ConvertToFraction(self.expression))
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
                if eval(self.ConvertToFraction(expr)) == self.user_answer:
                    return True
        except:
            print('判断正负号的计算过程出错')

    def CheckTips(self):
        # print(self.user_answer)
        tips = ''
        if type(self.user_answer) == str:
            self.user_answer = eval(self.ConvertToFraction(self.user_answer))
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

    # def JudgeAnswer(self):
    #     super().JudgeAnswer()
    #     try:
    #         user_answer = eval(self.ConvertToFraction(self.user_answer))
    #         self.is_correct = user_answer == self.correct_answer
    #         return self.is_correct
    #     except:
    #         return False


"""
类名称：QuestionQC
题目类型：两位数乘法速算
"""
class QuestionQC(QuestionLR):
    def __init__(self, subtype=[0, 0], range=[10, 50]):
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

        if subtype < 0 or subtype > 5:
            print(f"不支持的子类型: {subtype}")
            return False

        if subtype == 0:  # 平方数
            number = self.RandInt(min_val, max_val)
            self.numbers.append(number)
            self.operators.append('*')
            self.numbers.append(number)
        elif subtype == 1:  # 平方差法
            n1 = self.RandInt(int(min_val / 5), int(max_val / 5)) * 5
            n2 = self.RandInt(1, 5)
            self.numbers.append(n1 + n2)
            self.operators.append('*')
            self.numbers.append(n1 - n2)
        elif subtype == 2:  # 和十速算法
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
        elif subtype == 3:  # 大数凑十法
            n1 = self.RandInt(int(min_val / 10), int(max_val / 10)) * 10
            n2 = self.RandInt(1, 3)
            num1 = n1 - n2 if n1 - n2 >= min_val else n1 + 10 - n2
            n3 = self.RandInt(int(min_val / 10), int(max_val / 10)) * 10
            n4 = self.RandInt(1, 3)
            num2 = n3 + n4 if n3 + n4 <= max_val else n3 - 10 + n4
            self.numbers.append(num1)
            self.operators.append('*')
            self.numbers.append(num2)
        elif subtype == 4:  # 逢五凑十法
            n1 = self.RandInt(int(min_val / 5), int(max_val / 5)) * 5
            num1 = n1 if n1 % 10 != 0 else n1 + 5 if n1 + 5 <= max_val else n1 - 5
            n2 = self.RandInt(int(min_val / 2), int(max_val / 2)) * 2
            self.numbers.append(num1)
            self.operators.append('*')
            self.numbers.append(n2)
        elif subtype == 5:  # 双向凑十法
            n1 = self.RandInt(int(min_val / 10), int(max_val / 10)) * 10
            num1 = n1 + self.RandInt(8, 9)
            n2 = self.RandInt(int(min_val / 10), int(max_val / 10)) * 10
            num2 = n2 + 10 - self.RandInt(1, 2)
            self.numbers.append(num1)
            self.operators.append('*')
            self.numbers.append(num2)
        return True

    def AnswerTips(self):
        # print('乘法速算：AnswerTips()')
        tips = ''
        if self.subtype[0] == 0: # 平方数
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
        if self.subtype[0] == 1: # 平方差法
            m = self.numbers[0]
            n = self.numbers[1]
            a = int((m + n)/2)
            b = abs(a - self.numbers[0])
            tips += f'{m} × {n} = ({a} + {b})({a} - {b}) = {a} × {a} - {b} × {b} = {a*a} - {b*b} = {a*a-b*b}'
        if self.subtype[0] == 2: # 和十速算法
            m = self.numbers[0]
            n = self.numbers[1]
            a = int(m/10)
            b = m % 10
            c = 10 -b
            tips += f'{a} × ({a} + 1) = {a} × {a+1} = {a*(a+1)}；{b} × {c} = {b*c}；{m} × {n} = {m*n}'
        if self.subtype[0] == 3: # 大数凑十法
            m = self.numbers[0]
            n = self.numbers[1]
            r = m % 10
            c = 10 - r
            tips += f'{m} × {n} = ({m+c} - {c}) × {n} = {m+c} × {n} - {c} × {n} = {(m+c)*n} - {c*n} = {m*n}'
        if self.subtype[0] == 4: # 逢五凑十法
            m = self.numbers[0]
            n = self.numbers[1]
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
            tips += f'{m} × {n} = {a} × {b} × {c} × {d} = {a} × {d} × {b*c} = {a * d} × {b*c} = {m * n}'
        if self.subtype[0] == 5: # 双向凑十法
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
        super().__init__(type=2, subtype=subtype, range=range)
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
        # print(self.numbers)
        # print(self.operators)
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
        print('四则运算：AnswerTips()')
        self.answer_tips = self.ProcessCalculation()
        return self.answer_tips
        pass
