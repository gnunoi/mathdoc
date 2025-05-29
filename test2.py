import random

def length_conversion_quiz():
    print("欢迎使用长度换算练习程序！")
    print("请输入答案，输入'退出'结束程序")
    
    # 定义长度单位之间的换算关系（基数为米）
    conversion_rates = {
        "公里": 1000,
        "米": 1,
        "分米": 0.1,
        "厘米": 0.01,
        "毫米": 0.001,
        "微米": 1e-6,
        "纳米": 1e-9,
    }
    
    units = list(conversion_rates.keys())
    
    score = 0
    attempts = 0
    
    while True:
        # 随机选择两个不同的单位
        unit1 = random.choice(units)
        units_copy = units.copy()
        units_copy.remove(unit1)
        unit2 = random.choice(units_copy)
        
        # 随机生成一个数值（避免过小或过大的数值）
        value = round(random.uniform(0.1, 10), 1)
        
        # 计算正确答案
        correct_answer = value * conversion_rates[unit1] / conversion_rates[unit2]
        
        # 格式化题目并输出
        print(f"\n问题：{value}{unit1} 等于多少{unit2}？")
        
        # 获取用户输入
        user_input = input("请输入答案：")
        
        # 判断是否退出
        if user_input.lower() == "退出":
            print(f"\n练习结束！你的得分：{score} / {attempts}")
            break
        
        # 验证用户输入
        try:
            user_answer = float(user_input)
            attempts += 1
            
            # 检查答案是否正确（考虑浮点数精度问题）
            if abs(user_answer - correct_answer) < 0.005:  # 允许一定的误差范围
                print("回答正确！")
                score += 1
                print(f"正确答案是：{correct_answer:.2f}{unit2}")
            else:
                print("回答错误！")
                print(f"正确答案是：{correct_answer:.2f}{unit2}")
            
        except ValueError:
            print("输入无效，请输入数字或'退出'结束程序")

if __name__ == "__main__":
    length_conversion_quiz()
