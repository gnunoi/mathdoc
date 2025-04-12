import re
from fractions import Fraction


def convert_to_fraction(expression):
    # 使用正则表达式匹配所有整数或浮点数
    pattern = r'(?<!\w)(-?\d+\.?\d*|\.\d+)(?!\w)'

    # 替换函数：将匹配到的数字转换为 Fraction
    def replace_with_fraction(match):
        num_str = match.group(0)
        # 如果是小数点开头的数字，比如 .5，转换为 0.5
        if num_str.startswith('.'):
            num_str = '0' + num_str
        # 返回 Fraction(...) 的形式
        return f'Fraction({num_str})'

    # 使用正则表达式替换所有数字
    converted_expression = re.sub(pattern, replace_with_fraction, expression)
    return converted_expression


# 示例表达式
expression = "3 + 4.5 * (2 - .5) / 2.0"
converted_expression = convert_to_fraction(expression)
print("原始表达式:", expression)
print("转换后的表达式:", converted_expression)

# 验证转换后的表达式是否正确
try:
    result = eval(converted_expression)
    print("计算结果:", result)
except Exception as e:
    print("计算失败:", e)