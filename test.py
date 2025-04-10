import random
import itertools


def calculate24(nums):
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
                        r.append(expr)
                except ZeroDivisionError:
                    continue
    if len(r) != 0:
        return r
    else:
        return None


def generate_numbers():
    r = None
    while r is None:
        """生成四个1-13之间的随机整数"""
        numbers = [random.randint(1, 13) for _ in range(4)]
        r = calculate24(numbers)
    return numbers

def main():
    print("欢迎来到24点游戏！")
    print("程序会随机生成四个数字，尝试用加减乘除运算得到24。")
    # print("你可以先自己试试，或者让程序帮你解！")

    nums = generate_numbers()
    print(f"\n生成的数字是：{nums}")

    print("好的，输入你的解法（例如：(3 + 5) * (8 - 5)）：")
    user_input = input("> ")
    try:
        if abs(eval(user_input) - 24.0) < 1e-6:
            print("恭喜你！解法正确！")
        else:
            print("解法不正确，请再试一次！")
    except:
        print("输入的表达式有误，请检查格式！")

    solution = calculate24(nums)
    if solution:
        print(f"找到了解法：")
        for s in solution:
            print(s)
    else:
        print("很遗憾，我没有找到解法。可能这组数字没有解！")


if __name__ == "__main__":
    while True: main()