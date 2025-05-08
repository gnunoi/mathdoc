import random
import re
import sympy
from sympy import symbols, expand


def generate_polynomial():
    """生成一个随机的多项式用于因式分解练习"""
    x = symbols('x')

    # 随机决定是生成二次多项式还是三次多项式
    if random.random() < 0.5:
        # 二次多项式 ax² + bx + c
        a = random.randint(1, 5)
        b = random.randint(-10, 10)
        c = random.randint(-10, 10)
        return a * x ** 2 + b * x + c

    else:
        # 三次多项式 ax³ + bx² + cx + d
        a = random.randint(1, 3)
        b = random.randint(-5, 5)
        c = random.randint(-5, 5)
        d = random.randint(-5, 5)
        return a * x ** 3 + b * x ** 2 + c * x + d


def get_factors(polynomial):
    """获取多项式的因式分解结果"""
    x = symbols('x')
    return sympy.factor(polynomial)


def parse_user_answer(answer_str):
    """解析用户输入的答案"""
    x = symbols('x')

    # 去除空格
    answer_str = answer_str.replace(' ', '')

    # 处理不同的输入格式
    if '(' in answer_str:
        # 如果用户以因式形式输入
        factors = re.findall(r'\(.*?\)', answer_str)
        return [sympy.sympify(factor) for factor in factors]
    else:
        # 如果用户以多项式形式输入
        return [sympy.sympify(answer_str)]


def check_answer(user_factors, correct_factors):
    """检查用户的答案是否正确"""
    # 将因式转换为多项式形式
    user_poly = expand(user_factors[0] * user_factors[1] if len(user_factors) > 1 else user_factors[0])
    correct_poly = expand(correct_factors)

    # 排序因式以便比较
    user_factors = sorted([str(fac) for fac in user_factors])
    correct_factors = sorted([str(fac) for fac in correct_factors])

    return user_factors == correct_factors


def main():
    """主函数"""
    print("欢迎使用因式分解练习程序！")

    # 生成多项式
    x = symbols('x')
    poly = generate_polynomial()
    correct_factors = get_factors(poly)

    print(f"\n请因式分解多项式：{poly}")
    print(f"注意：答案应为因式乘积形式，如 (x+a)(x+b) 或 (ax+b)(cx+d)")

    while True:
        print(correct_factors)
        user_input = input("\n请输入你的答案(或输入'q'退出程序)：")

        if user_input.lower() == 'q':
            print("程序已退出。")
            break

        try:
            user_factors = parse_user_answer(user_input)
            if len(user_factors) == 0:
                print("输入格式错误，请重新输入。")
                continue

            if check_answer(user_factors, correct_factors):
                print("\n🎉 正确！")
            else:
                print("\n❌ 错误！请再试一次。")

        except:
            print("输入无法解析为有效的数学表达式，请检查格式后重新输入。")


if __name__ == "__main__":
    main()