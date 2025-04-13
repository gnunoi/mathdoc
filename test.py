import random
import numpy as np
import itertools
import re
from fractions import Fraction
from datetime import datetime
from collections import Counter
from itertools import combinations

"""
类名称：Question

变量：
answer_tips：答题提示
check_tips：检查提示
cls：题目类别，包括类型、描述、各种生成函数
comments：答题说明
correct_answer：正确答案
end_time：答题结束时间
expression：题目的表达式
is_correct：答题是否正确
numbers：操作数的数组
operators：运算符的数组
question：题目的题干
range：取值范围
start_time：答题开始时间
subtype：数组，分别是题目子类型及更详细的分类
type：题目类型
user_input：用户输入的原始答案
user_answer：整理并计算后的用户答案
used_time：提提所用时间

函数：
Dump()：输出所有成员
RandInt(a, b)：随机生成整数a到b之间的整数
Generate()：生成新题目
GenerateQuestion()：生成完整的题干
GenerateAnswer()：生成正确答案
GenerateTips()：生成检查提示与答题提示
JudgeAnswer()：判断用户答案是否正确

ConvertToFraction()：将表达式中的数字替换为分数，确保计算严格准确
ProcessUserInput()：处理用户输入，将中文符号替换为英文符号，删除空白符
CheckUserInput()：检查用户输入的表达式是否包含了全部数字

Generate24Point()：生成24点游戏的题目
Validate24Point()：计算24点游戏的数字是否正确，并返回正确答案，否则返回None
Generate24PointCheckTips()：生成24点游戏的检查提示

GenerateQC()：生成两位数乘法速算的题目
GenerateCheckTips()：生成检查提示
"""
class Question():
    def __init__(self, type = 0, subtype = [0], range = [1, 10]):
        # 题目类别，包括类型、描述、各种生成函数
        self.cls = [
            {"type" : 0,
             "name" : "24点游戏",
             "Generate" : self.Generate24Point,
             "Question" : lambda : f'24点游戏：{self.numbers}',
             'Answer' : lambda:24,
             'Comments' : lambda : '输入表达式，使得表达式的值为24。如：(5+3)*(8-5)。',
             'CheckTips': self.Generate24PointCheckTips,
             'AnswerTips' : lambda : f'答题提示：{self.Validate24Point()}',
             'JudgeAnswer' : self.Judge24PointAnswer,
            },
            {"type": 1,
             "name": "两位数乘法速算",
             "Generate": self.GenerateQC,
             "Question": lambda: f'{self.question}',
             'Answer': lambda: eval(self.expression),
             'Comments': lambda: '输入答案，可以含中间过程。如：36 * 36 = 32 * 40 + 4 * 4 = 1280 + 16 = 1296',
             'CheckTips': self.GenerateCheckTips,
             'AnswerTips': lambda: f'答题提示：',
             'JudgeAnswer': lambda: eval(self.expression) == eval(self.user_answer) # self.JudgeQCAnaswer,
             },
        ]
        self.type = type # 题目类型
        self.subtype = subtype  # 题目子类型
        self.range = range  # 取值范围
        self.numbers = [] # 操作数的数组
        self.operators = [] # 运算符的数组
        self.expression = None # 题目的表达式
        self.question = None # 题目的题干
        self.user_input = None # 用户输入的原始答案
        self.user_answer = None # 整理并计算后的用户答案
        self.correct_answer = None # 正确答案
        self.comments = None # 答题说明
        self.check_tips = None # 检查提示
        self.answer_tips = None # 答题提示
        self.is_correct = None # 答题是否正确
        self.start_time = None # 答题开始时间
        self.end_time = None # 答题结束时间
        self.used_time = None # 答题所用时间

        self.Generate()

    def Dump(self):
        print()
        print(f'Dumping Object: {self}')
        for name, value in self.__dict__.items():
            if name == 'cls':
                print(f"name: {value[0]['name']}")
                continue # 不输出cls成员变量
            else:
                print(f"{name}: {value}")
        print()

    def RandInt(self, a, b):
        for i in range(1, np.random.randint(1,100)):
            np.random.randint(a, b)
        return np.random.randint(a, b)

    def Generate(self):
        if self.type is None:
            print('Question对象未初始化')
            return False
        elif self.type >= len(self.cls):
            print(f'self.type = {self.type}：越界')
            return False
        else:
            self.cls[self.type]['Generate']()
            self.GenerateQuestion()
            self.GenerateComments()
            self.GenerateAnswer()
            # self.Dump()
            return True

    def GenerateQuestion(self):
        if self.type is None or len(self.numbers) == 0:
            print('Question对象未初始化')
        else:
            self.question = self.cls[self.type]['Question']()
            return self.question

    def GenerateAnswer(self):
        if self.type is None or len(self.numbers) == 0:
            print('Question对象未初始化')
        else:
            self.correct_answer = self.cls[self.type]['Answer']()
            return self.correct_answer

    def GenerateComments(self):
        if self.type is None or len(self.numbers) == 0:
            print('Question对象未初始化')
        else:
            self.comments = self.cls[self.type]['Comments']()

    def GenerateTips(self):
        if self.type is None or len(self.numbers) == 0:
            print('Question对象未初始化')
            return
        try:
            self.check_tips = self.cls[self.type]['CheckTips']()
        except:
            self.check_tips = f'{self.user_input}：无法正确求值，请检查输入是否正确'
        self.answer_tips = self.cls[self.type]['AnswerTips']()

    def Generate24PointCheckTips(self):
        if self.CheckUserInput():
            ret = f'检查提示：{self.user_input} = {eval(self.user_answer)} != {self.correct_answer}'
        else:
            ret = f'检查提示：{self.user_input} ，未包括全部数字'
        return ret

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
            print(f'求值出错：{abs(self.user_answer)}')
        try:
            correct_answer = abs(self.correct_answer)
        except:
            print(f'求值出错：{abs(self.correct_answer)}')

        if user_answer / self.user_answer != correct_answer / self.correct_answer:
            return True
        try:
            for numbers in numbers_list:
                expr = ''
                for i in range(len(self.operators)):
                    expr += str(numbers[i]) + self.operators[i]
                expr += str(numbers[i])
                if eval(expr) == self.user_answer:
                    return True
        except:
            print('判断正负号的计算过程出错')

    def GenerateCheckTips(self):
        print('self.GenerateCheckTips()')
        tips = []
        self.user_answer = eval(self.user_answer)
        user_answer = abs(self.user_answer)
        correct_answer = abs(self.correct_answer)
        print(self.user_answer)
        print(self.correct_answer)
        if self.IsSignError():
            tips.append('1. 正负号')
            print('1. 正负号')
        elif user_answer % 10 != correct_answer % 10:
            tips.append('2. 个位数')
            # print('2. 个位数')
        elif len(str(user_answer)) != len(str(correct_answer)):
            tips.append('3. 总位数')
            # print('3. 总位数')
        else:
            if user_answer // 10 != correct_answer // 10:
                tips.append('4. 进借位')
                # print('4. 进借位')
        self.check_tips = f'检查提示：{tips}'
        return self.check_tips

    def JudgeAnswer(self):
        if self.type is None or self.numbers is None:
            print('Question对象未初始化')
            return False
        else:
            print(f'self.user_answer: {self.user_answer}')
            print(f'self.correct_answer: {self.correct_answer}')

            self.is_correct = self.cls[self.type]['JudgeAnswer']()
            print(f'self.is_correct: {self.is_correct}')
            return self.is_correct

    def Judge24PointAnswer(self):
        if not self.ProcessUserInput():
            return False
        try:
            user_answer = eval(self.user_answer)
        except:
            print('求值出错：{}'.format(self.user_input))
        if not self.CheckUserInput():
            return False
        else:
            return user_answer == self.correct_answer

    def Generate24Point(self):
        if len(self.range) == 2:
            min = self.range[0]
            max = self.range[1]
        else:
            min = 1
            max = 10
        r = None
        while r is None:
            """生成四个1-13之间的随机整数"""
            self.numbers = [random.randint(min, max) for _ in range(4)]
            r = self.Validate24Point()
        return self.numbers

    def Validate24Point(self):
        """
        尝试用四个数字计算24点
        返回一个可能的解法，如果没有解则返回None
        """
        # 尝试所有可能的排列组合和运算符组合
        r = []
        for perm in itertools.permutations(self.numbers):
            for ops in itertools.product(['+', '-', '*', '/'], repeat=3):
                # 尝试三种不同的括号组合
                expressions = [
                    f"({perm[0]} {ops[0]} {perm[1]}) {ops[1]} ({perm[2]} {ops[2]} {perm[3]})",
                    f"(({perm[0]} {ops[0]} {perm[1]}) {ops[1]} {perm[2]}) {ops[2]} {perm[3]}",
                    f"{perm[0]} {ops[0]} (({perm[1]} {ops[1]} {perm[2]}) {ops[2]} {perm[3]})",
                    f"{perm[0]} {ops[0]} ({perm[1]} {ops[1]} ({perm[2]} {ops[2]} {perm[3]}))",
                    f"({perm[0]} {ops[0]} {perm[1]}) {ops[1]} {perm[2]} {ops[2]} {perm[3]}"
                ]
                for expr in expressions:
                    try:
                        # 使用eval计算表达式
                        converted_expression = self.ConvertToFraction(expr)
                        if eval(converted_expression) == 24: # 24点的正确结果为24
                            return expr
                    except ZeroDivisionError:
                        continue
        return None

    def GenerateExpression(self):
        if self.numbers is None or self.operators is None or len(self.numbers) - len(self.operators) != 1:
            return False
        expr = str(self.numbers[0])
        for i in range(1, len(self.numbers)):
            op = self.operators[i-1]
            num = self.numbers[i]
            expr += f" {op} ({num})" if num < 0 else f" {op} {num}"
        self.expression = expr
        # self.Evaluate()
        self.question = expr.replace('*', '×').replace('/', '÷') + " ="

    def GenerateQC(self):
        self.numbers = [] # 生成新题必须重新初始化
        self.operators = [] # 生成新题必须重新初始化
        subtype = self.subtype[0]
        min = self.range[0]
        max = self.range[1]

        if subtype < 0 or subtype > 5:
            print(f"不支持的子类型：{subtype}")
            return None

        if subtype == 0: # 平方数
            number = self.RandInt(min, max)
            self.numbers.append(number)
            self.operators.append('*')
            self.numbers.append(number)
        elif subtype == 1: # 平方差法
            n1 = self.RandInt(int(min/5), int(max/5))*5
            n2 = self.RandInt(1, 5)
            self.numbers.append(n1 + n2)
            self.operators.append('*')
            self.numbers.append(n1 - n2)
        elif subtype == 2: # 和十速算法
            n1 = self.RandInt(int(min/10), int(max/10))*10
            n2 = self.RandInt(1, 9)
            a = n1 + n2
            b = n1 + 10 - n2
            if a > max:
                a = a - 10
                b = b - 10
            self.numbers.append(a)
            self.operators.append('*')
            self.numbers.append(b)
        elif subtype == 3: # 大数凑十法
            n1 = self.RandInt(int(min/10), int(max/10))*10
            n2 = self.RandInt(1, 3)
            num1 = n1 - n2 if n1 - n2 >= min else n1 + 10 - n2
            n3 = self.RandInt(int(min/10), int(max/10))*10
            n4 = self.RandInt(1, 3)
            num2 = n3 + n4 if n3 + n4 <= max else n3 - 10 + n4
            self.numbers.append(num1)
            self.operators.append('*')
            self.numbers.append(num2)
            self.GenerateExpression()
        elif subtype == 4: # 逢五凑十法
            n1 = self.RandInt(int(min/5), int(max/5))*5
            num1 = n1 if n1 % 10 != 0 else n1 + 5 if n1 + 5 <= max else n1 - 5
            n2 = self.RandInt(int(min/2), int(max/2))*2
            self.numbers.append(num1)
            self.operators.append('*')
            self.numbers.append(n2)
        elif subtype == 5: # 双向凑十法
            n1 = self.RandInt(int(min/10), int(max/10))*10
            num1 = n1 + self.RandInt(8,9)
            n2 = self.RandInt(int(min/10), int(max/10))*10
            num2 = n2 + 10 - self.RandInt(1,2)
            self.numbers.append(num1)
            self.operators.append('*')
            self.numbers.append(num2)
        self.GenerateExpression()

    def ConvertToFraction(self, expression):
        # 使用正则表达式匹配所有整数或浮点数
        pattern = r'(?<!\w)(-?\d+\.?\d*|\.\d+)(?!\w)'

        # 替换函数：将匹配到的数字转换为 Fraction
        def replace_with_fraction(match):
            num_str = match.group(0)
            # 如果是小数点开头的数字，比如 .5，转换为 0.5
            if num_str.startswith('.'):
                num_str = '0' + num_str
            # 返回 Fraction(...) 的形式
            return f'Fraction({num_str})'

        # 使用正则表达式替换所有数字
        converted_expression = re.sub(pattern, replace_with_fraction, expression)
        return converted_expression

    def ProcessUserInput(self):
        # 定义替换映射
        replace_map = {
            "（": "(",
            "）": ")",
            "[": "(",
            "]": ")",
            "{": "(",
            "}": ")",
            "【": "(",
            "】": ")",
            "＋": "+",
            "➖": "-",
            "×": "*",
            "÷": "/",
        }

        user_input = self.user_input.strip()
        if user_input == '': return False
        # 执行替换
        for old, new in replace_map.items():
            user_input = user_input.replace(old, new)
        user_input = user_input.split('=')[-1]
        self.user_answer = user_input
        return True

    def CheckUserInput(self):
        digits_in_expression = re.findall(r'\d+\.?\d*', self.user_answer)
        digits_in_expression = [float(digit) for digit in digits_in_expression]
        numbers = [float(num) for num in self.numbers]
        self.user_answer = self.ConvertToFraction(self.user_answer)
        if Counter(digits_in_expression) == Counter(numbers):
            return True
        else:
            # print(f'{Counter(digits_in_expression)} != {Counter(numbers)}')
            return False

    def test(self):
        # self.Dump()
        while True:
            print(self.comments)
            print("输入EXIT或QUIT退出程序")
            print(self.question)
            self.user_input = input()
            if self.user_input.upper() == 'EXIT' or self.user_input.upper() == 'QUIT':
                print('用户退出程序')
                break
            if not self.ProcessUserInput():
                print('无效输入，继续做题')
                continue

            if self.JudgeAnswer():
                print('回答正确：{} = {}'.format(self.user_input, self.correct_answer))
                self.Generate()
            else:
                print('回答错误：再来一次')
                self.GenerateTips()
                if self.check_tips is not None: print(self.check_tips)
                if self.answer_tips is not None: print(self.answer_tips)
            print()

if __name__ == "__main__":
    q = Question(type = 1, subtype = [1], range=[10, 50])
    q.test()
