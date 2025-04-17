import re


def string_to_numbers(s):
    # 使用正则表达式提取字符串中的所有数字
    numbers_str = re.findall(r'\d+', s)

    # 将提取的数字字符串转换为整数
    numbers = [int(num) for num in numbers_str]

    return numbers

def check_numbers(expression, numbers):
    # 使用正则表达式提取表达式中的所有数字
    numbers_in_expression = re.findall(r'\d+', expression)

    # 将提取的数字字符串转换为整数
    numbers_in_expression = [int(num_str) for num_str in numbers_in_expression]

    # 检查两个数组是否完全相同（数量和内容都相同，顺序可以不同）
    print(sorted(numbers_in_expression))
    print(sorted(numbers))
    return sorted(numbers_in_expression) == sorted(numbers)


# 示例用法
if __name__ == "__main__":
    print('输入一组数字：')
    numbers = string_to_numbers(input())
    print('输入一个表达式：')
    expression = input()
    if check_numbers(expression, numbers):
        print("表达式中的数字与数组中的数字完全相同")
    else:
        print("表达式中的数字与数组中的数字不完全相同")