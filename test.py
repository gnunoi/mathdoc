import re
from collections import Counter


def validate_expression(expression, numbers):
    """
    判断用户输入的表达式是否包含给定数组中的数字，并且数字的出现次数与数组中的完全一致。

    参数:
        expression (str): 用户输入的表达式
        numbers (list): 给定的数字数组

    返回:
        bool: 如果表达式中的数字与给定数组完全一致（包括出现次数），返回 True，否则返回 False
    """
    # 提取表达式中的所有数字
    # 使用正则表达式匹配数字，包括整数和小数
    digits_in_expression = re.findall(r'\d+\.?\d*', expression)

    # 将提取的数字转换为浮点数
    digits_in_expression = [float(digit) for digit in digits_in_expression]

    # 将给定的数字数组转换为浮点数列表
    numbers = [float(num) for num in numbers]

    # 比较两个列表中的数字及其出现次数
    return Counter(digits_in_expression) == Counter(numbers)


# 测试用例
if __name__ == "__main__":
    # 测试用例 1：完全匹配
    print(validate_expression("15+3*24", [3, 15, 24]))  # 输出: True

    # 测试用例 2：部分匹配
    print(validate_expression("3 + 5 * 2", [3, 5]))  # 输出: False

    # 测试用例 3：顺序不同但完全匹配
    print(validate_expression("5 * 2 + 3", [3, 5, 2]))  # 输出: True

    # 测试用例 4：包含重复数字
    print(validate_expression("3 + 3 * 2", [3, 3, 2]))  # 输出: True

    # 测试用例 5：不匹配
    print(validate_expression("3 + 4 * 2", [3, 5, 2]))  # 输出: False