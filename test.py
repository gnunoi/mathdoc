import re
import itertools


def extract_numbers_and_operators(expr):
    # 提取表达式中的数字和运算符
    numbers = list(map(float, re.findall(r'\d+\.?\d*', expr)))
    operators = re.findall(r'[+\-*/]', expr)
    return numbers, operators


def generate_sign_combinations(n):
    # 生成n个数字的所有可能的符号组合
    l = list(itertools.product(['+', '-'], repeat=n))
    print(l)
    return l

def apply_sign_combination(numbers, signs):
    # 应用符号组合到数字上
    signed_numbers = []
    for i in range(len(numbers)):
        if signs[i] == '-':
            signed_numbers.append(-numbers[i])
        else:
            signed_numbers.append(numbers[i])
    return signed_numbers


def construct_expression(signed_numbers, operators):
    # 构造新的表达式
    expression = ""
    for i in range(len(signed_numbers)):
        expression += str(signed_numbers[i])
        if i < len(operators):
            expression += operators[i]
    return expression


def check_user_answer(user_answer, correct_expression):
    result = False
    exp = None
    # 提取正确表达式中的数字和运算符
    numbers, operators = extract_numbers_and_operators(correct_expression)
    n = len(numbers)
    print(f'numbers = {numbers}')
    print(f'oprators = {operators}')

    # 生成所有可能的符号组合
    sign_combinations = generate_sign_combinations(n)
    # print(sign_combinations)

    # 遍历所有符号组合
    for signs in sign_combinations:
        # 应用符号组合到数字上
        signed_numbers = apply_sign_combination(numbers, signs)
        print(f'signed_numbers = {signed_numbers}')

        # 构造新的表达式
        new_expression = construct_expression(signed_numbers, operators)
        print(new_expression)
        try:
            # 计算新表达式的结果
            new_result = eval(new_expression)
            print(f'{new_expression} = {new_result}')
            # 比较结果
            if new_result == user_answer:
                result= True
                exp = new_expression
                return result, exp
        except:
            continue

    return result, exp


# 正确的表达式
correct_expression = "3 + (-5) * 2"
correct_result = eval(correct_expression)

# 用户输入的答案
print(correct_expression)
user_answer = float(input("请输入你的计算答案: "))

# 检查用户答案是否正确
if user_answer == correct_result:
    print("你的计算是正确的！")
else:
    print("你的计算结果与正确答案不符。")
    # 检查是否可能是因为符号错误导致的
    found, corrected_expression = check_user_answer(user_answer, correct_expression)
    if found:
        print(f"这可能是由于你在表达式中弄错了符号。你可能将表达式: {corrected_expression}")
    else:
        print("请检查你的计算过程。")