import random

class Expression:
    def __init__(self, numbers=None, operators=None,
                 min1=1, max1=50,
                 min2=5, max2=10):
        # 初始化操作数和运算符列表（处理默认值）
        self.numbers = numbers if numbers is not None else []
        self.operators = operators if operators is not None else []
        self.min1 = min1 if min1 is not None else 1
        self.max1 = max1 if max1 is not None else 50
        self.min2 = min2 if min2 is not None else 5
        self.max2 = max2 if max2 is not None else 10
        self.expression = None

        # 检查运算符数量是否合法（可选）
        if len(self.operators) >0 and len(self.operators) != len(self.numbers) - 1:
            raise ValueError("运算符数量必须比操作数少1")

    def clear(self):
        self.numbers = []
        self.operators = []

    def generate_divisor(self):
        num = random.randint(self.min2, self.max2)
        while num == 0:
            num = random.randint(self.min2, self.max2)
        return num

    def check(self):
        count = len(self.numbers)

        # 检查乘除数的取值范围
        for i in range(count-2, -1, -1): # 开始值, 结束值(不包含）,步长
            if self.operators[i] in ['*', '/']:
                self.numbers[i+1] = self.generate_divisor()
                self.numbers[i] = self.generate_divisor()

        # 检查整除
        flag = 0
        for i in range(count-2, -1, -1): # 开始值, 结束值(不包含）,步长
            if self.operators[i] == '/':
                if flag == 0:
                    flag = 1
                    # print("self.numbers[{}] = {}".format(i + 1, self.numbers[i + 1]))
                    # print("self.numbers[{}] = {}".format(i, self.numbers[i]))
                    num = self.numbers[i+1] * self.numbers[i]
                    # print("num = {}".format(num))
                else:
                    num *= self.numbers[i]
                    # print("self.numbers[{}] = {}".format(i, self.numbers[i]))
                    # print("num = {}".format(num))
                if i == 0:
                    self.numbers[i] = num
            else:
                if flag == 1:
                    # print("self.numbers[{}] = {}".format(i, self.numbers[i]))
                    self.numbers[i+1] = num
                    flag = 0

    def generate_expression(self):
        if not self.numbers:
            return ""
        self.check()
        expr = str(self.numbers[0])
        for i in range(1, len(self.numbers)):
            op = self.operators[i-1]
            num = self.numbers[i]
            expr += f" {op} ({num})" if num < 0 else f" {op} {num}"
        self.expression = expr
        return expr

    def evaluate(self):
        try:
            result = eval(self.expression)
            # 判断是否是整数或可转换为整数的浮点数
            if isinstance(result, int):
                return result
            elif isinstance(result, float):
                if result.is_integer():
                    return int(result)
                else:
                    return result
            else:
                return "结果不是数字类型"
        except Exception as e:
            return f"错误: {e}"

class Question(Expression):
    def __init__(self, numbers=None, operators=None,
                 min1 = None, max1 = None,
                 min2 = None, max2 = None):
        super().__init__(numbers = numbers, operators = operators,
                         min1 = min1, max1 = max1,
                         min2 = min2, max2 = max2)

    def generate_question(self, count=2, min1=10, max1=99, min2=5, max2=10):
        for i in range(count):
            num = random.randint(min1, max1)
            op = random.choice(['+', '-', '*', '/'])
            self.numbers.append(num)
            if i < count-1:
                self.operators.append(op)
        return self.generate_expression().replace('*', '×').replace('/', '÷')

if __name__ == '__main__':
    q = Question()
    for i in range(1, 101):
        question = q.generate_question(count=3, min1=15, max1=80, min2=5, max2=15)
        print("{}: {} = {}".format(i, question, q.evaluate()))
        q.clear()