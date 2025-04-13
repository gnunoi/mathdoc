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
name：题目类型名称
numbers：操作数的数组
operators：运算符的数组
question：题目的题干
range：取值范围
start_time：答题开始时间
subtype：数组，分别是题目子类型及更详细的分类
type：题目类型编号
user_input：用户输入的原始答案
user_answer：整理并计算后的用户答案
used_time：提提所用时间

函数：
Dump()：输出所有成员
RandInt(a, b)：随机生成整数a到b之间的整数
Generate()：生成新题目
Question()：生成完整的题干
Answer()：生成正确答案
Tips()：生成检查提示与答题提示
CheckTips()：生成检查提示
AnswerTips()：生成检查提示
JudgeAnswer()：判断用户答案是否正确

ConvertToFraction()：将表达式中的数字替换为分数，确保计算严格准确
ProcessUserInput()：处理用户输入，将中文符号替换为英文符号，删除空白符
CheckUserInput()：检查用户输入的表达式是否包含了全部数字
"""
class Question():
    def __init__(self, type=0, subtype=[0], range=[1, 10]):
        self.type = type
        self.name = None
        self.subtype = subtype
        self.range = range
        self.numbers = []
        self.operators = []
        self.expression = None
        self.question = None
        self.user_input = None
        self.user_answer = None
        self.correct_answer = None
        self.comments = None
        self.check_tips = None
        self.answer_tips = None
        self.is_correct = None
        self.start_time = None
        self.end_time = None
        self.used_time = None

    def Dump(self):
        print()
        print(f'Dumping Object: {self}')
        for name, value in self.__dict__.items():
            print(f"{name}: {value}")
        print()

    def RandInt(self, a, b):
        return np.random.randint(a, b)

    def Generate(self):
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

    def JudgeAnswer(self):
        pass

    def ConvertToFraction(self, expression):
        pattern = r'(?<!\w)(-?\d+\.?\d*|\.\d+)(?!\w)'
        def replace_with_fraction(match):
            num_str = match.group(0)
            if num_str.startswith('.'):
                num_str = '0' + num_str
            return f'Fraction({num_str})'
        converted_expression = re.sub(pattern, replace_with_fraction, expression)
        return converted_expression

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
        return True

    def CheckUserInput(self):
        digits_in_expression = re.findall(r'\d+\.?\d*', self.user_answer)
        digits_in_expression = [float(digit) for digit in digits_in_expression]
        numbers = [float(num) for num in self.numbers]
        return Counter(digits_in_expression) == Counter(numbers)

    def test(self):
        print(self.name)
        # 初始化题目
        if self.Generate() == False:
            return
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
                self.Generate()  # 生成下一题
            else:
                print('回答错误：再来一次')
                self.Tips()
                if self.check_tips is not None:
                    print(self.check_tips)
                if self.answer_tips is not None:
                    print(self.answer_tips)
            print()


class QuestionQC(Question):
    def __init__(self, subtype=[0], range=[1, 10]):
        super().__init__(type=1, subtype=subtype, range=range)
        self.name = "两位数乘法速算"
        self.comments = "输入答案，可以含中间过程。如：36 * 36 = 32 * 40 + 4 * 4 = 1280 + 16 = 1296"
        self.Generate()

    def Generate(self):
        if self.GenerateQC() == True:
            self.Question()
            self.Answer()
            return True
        else:
            return False

    def GenerateQC(self):
        """
        :return:
            False，错误
            True，正确
        """
        self.numbers = []
        self.operators = []
        subtype = self.subtype[0]
        min_val = self.range[0]
        max_val = self.range[1]

        if subtype < 0 or subtype > 5:
            print(f"不支持的子类型：{subtype}")
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

    def Question(self):
        try:
            expr = str(self.numbers[0])
            for i in range(1, len(self.numbers)):
                op = self.operators[i-1]
                num = self.numbers[i]
                expr += f" {op} {num}"
            self.question = expr.replace('*', '×') + " ="
            return self.question
        except:
            print('无法生成题目')
            return None

    def Answer(self):
        self.correct_answer = eval(self.question.replace('×', '*').replace('÷', '/').replace('=', ''))
        return self.correct_answer

    def CheckTips(self):
        pass

    def AnswerTips(self):
        pass

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

    def CheckTips(self):
        print('self.CheckTips()')
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
        elif len(str(user_answer)) != len(str(correct_answer)):
            tips.append('3. 总位数')
        elif user_answer // 10 != correct_answer // 10:
            tips.append('4. 进借位')
        self.check_tips = f'检查提示：{tips}'
        return self.check_tips

    def JudgeAnswer(self):
        try:
            user_answer = eval(self.user_answer)
            return user_answer == self.correct_answer
        except:
            return False


class Question24Point(Question):
    def __init__(self, range=[1, 13]):
        super().__init__(type=0, subtype=[0], range=range)
        self.name = "24点游戏"
        self.comments = "输入表达式，使得表达式的值为24。如：(5+3)*(8-5)。"
        self.Generate()

    def Generate(self):
        self.Generate24Point()
        self.Question()
        self.Answer()

    def Generate24Point(self):
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
        self.question = f'24点游戏：{self.numbers}'
        return self.question

    def Answer(self):
        self.correct_answer = 24
        return self.correct_answer

    def CheckTips(self):
        if not self.CheckUserInput():
            self.check_tips = f'检查提示：{self.user_input} ，未包括全部数字'
        else:
            try:
                user_answer = eval(self.user_answer)
                if user_answer != self.correct_answer:
                    self.check_tips = f'检查提示：{self.user_input} = {user_answer} != {self.correct_answer}'
                else:
                    self.check_tips = f'检查提示：正确！'
            except:
                self.check_tips = f'检查提示：无法正确求值，请检查输入是否正确'
        return self.check_tips

    def AnswerTips(self):
        self.answer_tips = f'答题提示：{self.Validate24Point()}'
        return self.answer_tips

    def JudgeAnswer(self):
        if not self.ProcessUserInput():
            return False
        try:
            # 转化为分数再计算，处理诸如：[3, 3, 8, 8]：8 / (3 - (8 / 3))
            user_answer = eval(self.ConvertToFraction(self.user_answer))
        except:
            return False
        if not self.CheckUserInput():
            return False
        return user_answer == self.correct_answer


class QuestionManager:
    def __init__(self, type=0, subtype=[0], range=[1, 10]):
        self.type = type
        self.subtype = subtype
        self.range = range
        self.q = self.CreateQuestion()

    def CreateQuestion(self):
        if self.type == 0:
            return QuestionQC(subtype=self.subtype, range=self.range)
        if self.type == 1:
            return Question24Point(range=self.range)
        else:
            print(f'{self.type}：无效的类型')
            return None

    def test(self):
        self.q.test()


if __name__ == "__main__":
    qm = QuestionManager(type=0, subtype=[2], range=[11, 50])
    qm.test()