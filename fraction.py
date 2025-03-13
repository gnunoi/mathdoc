import random
from fractions import Fraction

calculate = {
    '+': lambda num1, num2: num1 + num2,
    '-': lambda num1, num2: num1 - num2,
    '×': lambda num1, num2: num1 * num2,
    '÷': lambda num1, num2: num1 / num2
}

if __name__ == '__main__':
    def main():
        min_num = -5
        max_num = 5

        for i in range(1, 100 + 1):
            # 生成分数（分母范围2-10）
            num1 = Fraction(random.randint(min_num, max_num), random.randint(2, 10))
            num2 = Fraction(random.randint(min_num, max_num), random.randint(2, 10))
            operator = random.choice(['+', '-', '×', '÷'])

            if operator in ['÷'] and num2 == 0:
                i -= 1
                continue
            # 构建表达式并计算结果
            expression = f'{num1} {operator} {num2}'
            result = calculate[operator](num1, num2)

            # 输出带编号的题目和答案
            print(f'{i}: {expression} = {result}')


    main()