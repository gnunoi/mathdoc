<<<<<<< HEAD
import random

def is_prime(n):
    """判断一个数是否为质数"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def prime_factors(n):
    """返回n的质因数分解结果"""
    factors = []

    # 处理2的因子
    while n % 2 == 0:
        factors.append(2)
        n = n // 2

    # 处理奇数因子
    i = 3
    while i * i <= n:
        while n % i == 0:
            factors.append(i)
            n = n // i
        i += 2

    # 如果剩余的n是质数
    if n > 1:
        factors.append(n)

    return factors


def generate_random_number():
    """生成一个10到1000之间的随机数，保证有至少3个质因数"""
    while True:
        num = random.randint(10, 100)
        if len(prime_factors(num)) >= 3: # 有3个及以上的质因数
            return num

def validate_user_input(generated_num, user_factors):
    """验证用户输入的质因数是否正确"""
    # 将用户输入转换为整数列表
    try:
        user_factors = [int(factor) for factor in user_factors]
    except ValueError:
        return False, "输入中包含非整数值"

    # 获取正确的质因数分解
    correct_factors = prime_factors(generated_num)

    # 检查用户输入是否与正确分解匹配
    if set(user_factors) == set(correct_factors):
        return True, "正确！您提供的所有质因数都正确。"
    elif set(user_factors) != set(correct_factors):
        return False, f"错误：您提供的质因数不正确。正确质因数为：{correct_factors}"
    else:
        # 用户提供了正确的质因数，但数量或重复次数不正确
        return False, f"错误：质因数分解不完整。正确质因数为：{correct_factors}"


def run():
    print("欢迎使用质因数验证程序！")
    print("我们将生成一个介于10-1000之间的随机数，该数有至少3个质因数（允许重复）。")
    print("请输入您认为正确的所有质因数（用空格分隔）：")

    while True:
        # 生成随机数
        random_num = generate_random_number()
        print(f"\n生成的随机数为：{random_num}")

        # 获取用户输入
        user_input = input("请输入质因数（用空格分隔），EXIT或QUIT退出：")
        if user_input.strip().upper() in ['EXIT', 'QUIT']:
            break
        else:
            user_input = user_input.replace('*', ' ')
            print(user_input)
            user_factors = user_input.split()
            print(user_factors)
            if not user_factors:
                print("错误：您没有输入任何质因数！")
                return

            is_valid, message = validate_user_input(random_num, user_factors)
            print(message)

if __name__ == "__main__":
    run()
=======
str = '35 × 25 = '
str_list = ['55 × 45 = ',
            '20 × 10 = ',
            '49 × 41 = ',
            '49 × 41 = ',
            '54 × 46 = ',
            '33 × 27 = ',
            '23 × 17 = ',
            '49 × 41 = ',
            '46 × 44 = ',
            '35 × 25 = '
            ]

if str in str_list:
    print(f'{[str]}在{str_list}中')
else:
    print(f'{[str]}不在{str_list}中')
>>>>>>> 3565bcaf95c938ea838c463e462a11bb02b8d9fd
