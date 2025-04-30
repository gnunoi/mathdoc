from sympy import symbols, Eq, solve
from random import randint, choice

x = symbols('x')


def generate_equation():
    # 生成随机的一元一次方程参数
    a = randint(1, 10)
    b = randint(1, 10)
    c = randint(1, 10)
    d = randint(1, 10)

    # 确保方程有整数解
    if a == 0:
        a = 1
    if c == 0:
        c = 1

    # 构建方程
    equation = Eq(a * x + b, c * x + d)
    return equation, solve(equation, x)[0]


def main():
    while True:
        equation, correct_answer = generate_equation()
        print("\n新方程已生成:")
        print(f"{equation}")

        user_input = input("请输入解法（或输入'退出'结束程序）: ").strip()

        if user_input.lower() in ['退出', 'exit']:
            print("感谢使用方程求解器！再见！")
            break

        try:
            # 判断用户的答案是否正确
            if str(user_input) == str(correct_answer):
                print("恭喜！您的答案正确！")
            else:
                print(f"很遗憾，您的答案有误。正确解是 x = {correct_answer}")

        except Exception as e:
            print(f"输入解析错误: {e}")
            print("请输入正确的方程格式，例如: 3x + 5 = 7x - 1")


if __name__ == "__main__":
    main()