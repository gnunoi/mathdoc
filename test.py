import random
import re
import math


def generate_equation():
    """生成一个随机的一元一次方程，可以有各种变形"""
    # 生成方程的三种基本形式中的一个
    equation_form = random.randint(0, 5)

    # 方程中x的值
    x_value = random.randint(-10, 10)
    while x_value == 0:  # 避免x为0
        x_value = random.randint(-10, 10)

    if equation_form == 0:  # ax + b = c
        a = random.randint(1, 10)
        b = random.randint(-10, 10)
        c = a * x_value + b
        equation = f"{a}x + {b} = {c}"

    elif equation_form == 1:  # ax = bx + c
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        while b == a:  # 确保方程有解
            b = random.randint(1, 10)
        c = (a - b) * x_value
        equation = f"{a}x = {b}x + {c}"

    elif equation_form == 2:  # ax + b = cx + d
        a = random.randint(1, 10)
        b = random.randint(-10, 10)
        c = random.randint(1, 10)
        while c == a:  # 确保方程有解
            c = random.randint(1, 10)
        d = (a - c) * x_value + b
        equation = f"{a}x + {b} = {c}x + {d}"

    elif equation_form == 3:  # a(x + b) = c
        a = random.randint(1, 10)
        b = random.randint(-10, 10)
        c = a * (x_value + b)
        equation = f"{a}(x + {b}) = {c}"

    elif equation_form == 4:  # a(x + b) = c(x + d)
        a = random.randint(1, 10)
        b = random.randint(-10, 10)
        c = random.randint(1, 10)
        d = random.randint(-10, 10)
        while c == a:  # 避免两边系数相同
            c = random.randint(1, 10)
        equation = f"{a}(x + {b}) = {c}(x + {d})"

    elif equation_form == 5:  # 分数方程，如 (ax + b)/c = d
        a = random.randint(1, 10)
        b = random.randint(-10, 10)
        c = random.randint(2, 5)
        d = (a * x_value + b) / c
        equation = f"({a}x + {b}) / {c} = {d}"

    # 确保方程中没有多余的 '+' 符号，如在负数前
    equation = equation.replace(" + -", " - ")

    return equation, x_value


def parse_user_input(user_input):
    """解析用户输入，支持整数或分数形式"""
    # 先尝试直接转换为浮点数
    try:
        return float(user_input)
    except ValueError:
        pass

    # 尝试解析分数形式 (如 "3/2" 或 "-5/4")
    match = re.match(r"(-?\d+)\s*/\s*(-?\d+)", user_input)
    if match:
        numerator = int(match.group(1))
        denominator = int(match.group(2))
        if denominator == 0:
            return None  # 避免除以零
        return numerator / denominator

    return None


def run_exercise():
    """运行一元一次方程练习程序"""
    print("欢迎使用一元一次方程练习程序！")
    print("输入你的答案，正确会进入下一题，错误需要重新回答当前方程")
    print("输入 'q' 可以退出程序")

    answered_correctly = 0
    total_questions = 0

    while True:
        equation, correct_answer = generate_equation()
        print(f"\n方程: {equation}")

        correct = False
        while not correct:
            user_input = input("请输入x的值: ")

            # 检查是否要退出
            if user_input.lower() == 'q':
                print("退出程序")
                return

            # 解析用户输入
            user_answer = parse_user_input(user_input)

            if user_answer is None:
                print("输入格式不正确，请输入整数或分数形式 (如 3/2)")
                continue

            # 检查答案是否正确
            if abs(user_answer - correct_answer) < 0.0001:  # 允许小数点后四位误差
                print("恭喜你，回答正确！")
                answered_correctly += 1
                total_questions += 1
                correct = True
            else:
                print(f"回答错误！请再试一次。")

    print(f"\n练习结束！你正确回答了 {answered_correctly} 道题目，总共练习了 {total_questions} 道题目。")


# 运行程序
if __name__ == "__main__":
    run_exercise()