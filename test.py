import random


class Question():
    def __init__(self, term_count=2, range=None, user_operators=None):
        self.term_count = term_count # 多项式的项数
        if range is None:
            self.range = [10, 50, 5, 10]
        else:
            self.range = range # 操作数取值范围
        if user_operators is None:
            self.user_operators = ['+', '-', '*', '/']
        else:
            self.user_operators = user_operators
        self.numbers = [] # 操作数
        self.operators = [] # 运算符
        self.expression = None # 表达式
        self.question = None # 题干
        self.correct_answer = None # 正确答案
        self.user_answer = None # 用户答案
        self.tips = None # 提示
        self.Generate()

    def Set(self, term_count, range, user_operators):
        if term_count is not None:
            self.term_count = term_count
        if range is not None:
            self.range = range
        if user_operators is not None:
            self.user_operators = user_operators
        self.Generate()

    def Print(self):
        # print("term_count = {}".format(self.term_count))
        # print("range = {}".format(self.range))
        # print("user_operators = {}".format(self.user_operators))
        # print("numbers = {}".format(self.numbers))
        # print("opeators = {}".format(self.operators))
        # print("expresssion = {}".format(self.expression))
        print("question = {}".format(self.question))
        print("correct_answer = {}".format(self.correct_answer))
        # print("user_answer = {}".format(self.correct_answer))

    def Generate(self):
        self.numbers = []
        self.operators = []
        for i in range(self.term_count):
            self.numbers.append(random.randint(self.range[0], self.range[1]))
            if i < self.term_count - 1:
                self.operators.append(random.choice(self.user_operators))

        self.Validate()
        self.GenerateExpression()

    # 生成表达式
    def GenerateExpression(self):
        expr = str(self.numbers[0])
        for i in range(1, len(self.numbers)):
            op = self.operators[i-1]
            num = self.numbers[i]
            expr += f" {op} ({num})" if num < 0 else f" {op} {num}"
        self.expression = expr
        self.Evaluate()
        self.question = expr.replace('*', '×').replace('/', '÷') + " ="
        return self.expression

    # 在range[2]与range[3]之间，生成随机的乘除数
    def Divisor(self):
        num = random.randint(self.range[2], self.range[3])
        while num == 0:
            num = random.randint(self.range[2], self.range[3])
        return num

    def Validate(self):
        count = self.term_count
        # 检查乘除数的取值范围
        for i in range(count - 2, -1, -1):  # 开始值, 结束值(不包含）,步长
            if self.operators[i] in ['*', '/']:
                self.numbers[i + 1] = self.Divisor()
                self.numbers[i] = self.Divisor()

        # 检查整除
        flag = 0
        for i in range(count - 2, -1, -1):  # 开始值, 结束值(不包含）,步长
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
            # 判断是否是整数或可转换为整数的浮点数
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
    q = Question(term_count = 3, range=[5,20,5,10], user_operators=['+'])
    q.Print()
    q.Set(term_count = 4, range = [-100, 100, 5, 20], user_operators=['+', '-', '*', '/'])
    q.Print()
    for i in range(100):
        q.Generate()
        print("{}: {} {} ".format(i+1, q.question, q.correct_answer))


