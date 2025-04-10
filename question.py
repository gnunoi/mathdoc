import random
import time
import itertools

class Question():
    def __init__(self, term_count=2, range=None, user_operators=None, numbers=None, operators=None):
        self.term_count = term_count
        if range is None:
            self.range = [10, 50, 5, 10]
        else:
            self.range = range
        if user_operators is None:
            self.user_operators = ['+', '-', '*', '/']
        else:
            self.user_operators = user_operators
        self.type = None
        self.quick_calc_type = None
        self.numbers = numbers
        self.operators = operators
        self.expression = None
        self.question = None
        self.correct_answer = None
        self.user_answer = None
        self.tips = None
        if self.numbers is None or self.operators is None:
            self.Generate()
            pass
        else:
            self.GenerateExpression()
            pass

    def RandInt(self, a, b):
        random.seed(time.time())
        for i in range(1, random.randint(1,10)):
            random.randint(a, b)
        return random.randint(a, b)

    def calculate24(self, nums):
        """
        尝试用四个数字计算24点
        返回一个可能的解法，如果没有解则返回None
        """
        # 尝试所有可能的排列组合和运算符组合
        r = []
        for perm in itertools.permutations(nums):
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
                        if abs(eval(expr) - 24.0) < 1e-6:
                            return expr
                    except ZeroDivisionError:
                        continue
        return None

    def generate_24point_numbers(self):
        r = None
        while r is None:
            """生成四个1-13之间的随机整数"""
            numbers = [random.randint(1, 13) for _ in range(4)]
            r = self.calculate24(numbers)
        # print(numbers)
        return numbers

    def Set(self, term_count=None, range=None, user_operators=None, type=None, quick_calc_type=None):
        if term_count is not None:
            self.term_count = term_count
        if range is not None:
            self.range = range
        if user_operators is not None:
            self.user_operators = user_operators
        if type is not None:
            self.type = type
        if quick_calc_type is not None:
            self.quick_calc_type = quick_calc_type
        self.Generate()

    def Print(self):
        print("question = {}".format(self.question))
        print("correct_answer = {}".format(self.correct_answer))

    def Generate(self):
        self.numbers = []
        self.operators = []
        if self.type == 0:  # 四则运算
            for i in range(self.term_count):
                self.numbers.append(self.RandInt(self.range[0], self.range[1]))
                if i < self.term_count - 1:
                    self.operators.append(random.choice(self.user_operators))
            self.Validate()
            self.GenerateExpression()
        elif self.type == 1:  # 速算
            if self.quick_calc_type == 0: # 平方数
                number = self.RandInt(self.range[2], self.range[3])
                self.numbers.append(number)
                self.operators.append('*')
                self.numbers.append(number)
                self.GenerateExpression()
            if self.quick_calc_type == 1: # 平方差法
                n1 = self.RandInt(int(self.range[2]/5), int(self.range[3]/5))*5
                n2 = self.RandInt(1, 5)
                self.numbers.append(n1 + n2)
                self.operators.append('*')
                self.numbers.append(n1 - n2)
                self.GenerateExpression()
            if self.quick_calc_type == 2: # 和十速算法
                n1 = self.RandInt(int(self.range[2]/10), int(self.range[3]/10))*10
                n2 = self.RandInt(1, 9)
                a = n1 + n2
                b = n1 + 10 - n2
                if a > self.range[3]:
                    a = a - 10
                    b = b - 10
                self.numbers.append(a)
                self.operators.append('*')
                self.numbers.append(b)
                self.GenerateExpression()
            if self.quick_calc_type == 3: # 大数凑十法
                n1 = self.RandInt(int(self.range[2]/10), int(self.range[3]/10))*10
                n2 = self.RandInt(1, 3)
                num1 = n1 - n2 if n1 - n2 >= self.range[2] else n1 + 10 - n2
                n3 = self.RandInt(int(self.range[2]/10), int(self.range[3]/10))*10
                n4 = self.RandInt(1, 3)
                num2 = n3 + n4 if n3 + n4 <= self.range[3] else n3 - 10 + n4
                self.numbers.append(num1)
                self.operators.append('*')
                self.numbers.append(num2)
                self.GenerateExpression()
            if self.quick_calc_type == 4: # 逢五凑十法
                n1 = self.RandInt(int(self.range[2]/5), int(self.range[3]/5))*5
                num1 = n1 if n1 % 10 != 0 else n1 + 5 if n1 + 5 <= self.range[3] else n1 - 5
                n2 = self.RandInt(int(self.range[2]/2), int(self.range[3]/2))*2
                self.numbers.append(num1)
                self.operators.append('*')
                self.numbers.append(n2)
                self.GenerateExpression()
            if self.quick_calc_type == 5: # 双向凑十法
                n1 = self.RandInt(int(self.range[2]/10), int(self.range[3]/10))*10
                num1 = n1 + self.RandInt(8,9)
                n2 = self.RandInt(int(self.range[2]/10), int(self.range[3]/10))*10
                num2 = n2 + 10 - self.RandInt(1,2)
                self.numbers.append(num1)
                self.operators.append('*')
                self.numbers.append(num2)
                self.GenerateExpression()
        elif self.type == 2:
            self.numbers = self.generate_24point_numbers()
            self.GenerateExpression()

    def GenerateExpression(self):
        if self.type == 0 or self.type == 1:
            expr = str(self.numbers[0])
            for i in range(1, len(self.numbers)):
                op = self.operators[i-1]
                num = self.numbers[i]
                expr += f" {op} ({num})" if num < 0 else f" {op} {num}"
            self.expression = expr
            self.Evaluate()
            self.question = expr.replace('*', '×').replace('/', '÷') + " ="
        elif self.type == 2:
            self.correct_answer = 24
            self.expression = ',  '.join(map(str, self.numbers))
            print(self.expression)
            self.question = f'计算24点：{self.expression}'
            print(self.question)

    def Divisor(self):
        num = self.RandInt(self.range[2], self.range[3])
        while num == 0:
            num = self.RandInt(self.range[2], self.range[3])
        return num

    def Validate(self):
        count = self.term_count
        for i in range(count - 2, -1, -1):
            if self.operators[i] in ['*', '/']:
                self.numbers[i + 1] = self.Divisor()
                self.numbers[i] = self.Divisor()

        flag = 0
        for i in range(count - 2, -1, -1):
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

    def Evaluate(self):
        try:
            result = eval(self.expression)
            if isinstance(result, int):
                self.correct_answer = result
            elif isinstance(result, float):
                if result.is_integer():
                    self.correct_answer = int(result)
                else:
                    self.correct_answer = result
            else:
                return "结果不是数字类型"
        except Exception as e:
            return f"错误: {e}"

if __name__ == "__main__":
    q = Question(term_count=3, range=[5, 20, 5, 10], user_operators=['+'])
    q.Print()
    q.Set(term_count=4, range=[-100, 100, 5, 20], user_operators=['+', '-', '*', '/'])
    q.Print()
    for i in range(100):
        q.Generate()
        print("{}: {} {} ".format(i+1, q.question, q.correct_answer))