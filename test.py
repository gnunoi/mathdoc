import random
import sympy as sp


def generate_quadratic_equation():
    # 生成一元二次方程的系数
    a = random.randint(1, 5)
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)

    # 确保方程有实数解（判别式非负）
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        # 如果判别式为负，重新生成系数以确保有实数解
        b = random.randint(1, 10)  # 确保b不为0
        # 确保判别式非负
        discriminant = b ** 2 - 4 * a * c
        if discriminant < 0:
            # 如果仍然为负，调整c以确保判别式非负
            c = b ** 2 // (4 * a) - 1
    return a, b, c


def solve_quadratic_equation(a, b, c):
    x = sp.symbols('x')
    equation = a * x ** 2 + b * x + c
    solutions = sp.solve(equation, x)
    # 格式化为浮点数列表
    # solutions = [round(float(sol), 2) for sol in solutions]
    print(solutions)
    return sorted(solutions)


def main():
    while True:
        # 生成新问题
        a, b, c = generate_quadratic_equation()
        solutions = solve_quadratic_equation(a, b, c)

        # 显示方程
        print(f"\n解这个一元二次方程: {a}x² + {b}x + {c} = 0")
        print("输入你的答案，用逗号分隔多个答案，保留两位小数，例如：2.00, 3.00")

        # 获取用户输入
        user_input = input("你的答案：")

        # 解析用户输入
        try:
            user_solutions = [round(float(num.strip()), 2) for num in user_input.split(',')]
            user_solutions = sorted(user_solutions)
        except ValueError:
            print("输入格式错误，请使用逗号分隔的数字")
            user_solutions = []

        # 判断答案是否正确
        if user_solutions == solutions:
            print("正确！")
        else:
            print(f"错误，正确答案是：{', '.join(map(str, solutions))}")

        # 询问是否继续
        while True:
            continue_input = input("是否继续（是/否）？").strip().lower()
            if continue_input in ['是', 'y', 'yes']:
                break
            elif continue_input in ['否', 'n', 'no']:
                print("感谢使用！")
                return
            else:
                print("无效输入，请回答是或否")


if __name__ == "__main__":
    main()