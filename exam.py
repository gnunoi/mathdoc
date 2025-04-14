from question import *

"""
类名称: Exam
变量: 
type: 题目类型
   0: 24点游戏
   1: 乘法速算
   2: 四则运算
subtype: 子类型
  乘法速算:
    参数一:
      0: 平方数
      1: 平方差法
      2: 和十速算法
      3: 大数凑十法
      4: 逢五凑十法
      5: 双向凑十法
  四则运算:
    参数一：
      2: 二项式
      3: 三项式 
      4: 四项式
      5: 五项式
    参数二:
      0: 加法
      1: 减法
      2: 乘法
      3: 除法
      4: 混合运算
range: 取值范围
q: Question对象

函数: 
CreateQuestion(): 生成与type相对应的题目类别的对象
Update(): 更新成员变量的函数
Test(): 测试函数

"""
class Exam:
    def __init__(self, type=0, subtype=[0], range=[1, 10]):
        self.type = type
        self.subtype = subtype
        self.range = range
        self.q = self.CreateQuestion()

    def Dump(self):
        print()
        print(f'Dumping Object: {self}')
        for name, value in self.__dict__.items():
            print(f"{name}: {value}")
        print()

    def Update(self, type, subtype, range):
        if type is not None: self.type = type
        if subtype is not None: self.subtype = subtype
        if range is not None: self.range = range
        self.q = self.CreateQuestion()

    def CreateQuestion(self):
        if self.type == 0: # 0: 24点游戏
            return Question24Point(range=self.range)
        elif self.type == 1: # 1: 乘法速算
            return QuestionQC(subtype=self.subtype, range=self.range)
        elif self.type == 2: # 2: 四则运算
            return Question4AO(subtype=self.subtype, range=self.range)
        else:
            print(f'{self.type}: 无效的类型')
            return None

    def Test(self):
        type = 0
        parms = [{'type': 0, 'subtype': [], 'range': [1, 10]},
                 {'type': 1, 'subtype': [1], 'range': [10, 50]},
                 {'type': 2, 'subtype': [3, 4], 'range': [-50, 50, 2, 10]},
                 ]
        self.Update(parms[type]['type'], parms[type]['subtype'], parms[type]['range'])
        q = self.q
        print(q.name)
        # 初始化题目
        if q.Generate() == False:
            return
        # q.Dump()
        while True:
            print(q.comments)
            print("输入EXIT或QUIT退出程序")
            print(q.start_time)
            print(q.question)
            q.user_input = input()
            if q.user_input.upper() == 'EXIT' or q.user_input.upper() == 'QUIT':
                print('用户退出程序')
                break
            if not q.ProcessUserInput():
                print('无效输入，继续做题')
                continue
            if q.JudgeAnswer():
                if q.type == 0:
                    print('回答正确: {} = {}'.format(q.user_input, q.correct_answer))
                else:
                    print('回答正确: {} = {}'.format(q.expression, q.user_answer))
                print(f'答题结束时间：{q.end_time}, 答题用时：{q.used_time}秒')
                q.Generate()  # 生成下一题
            else:
                print('回答错误: 再来一次')
                q.Tips()
                if q.check_tips is not None:
                    print(f'检查提示：{q.check_tips}')
                if q.answer_tips is not None:
                    print(f'答题提示：{q.answer_tips}')
                print(f'答题结束时间：{q.end_time}, 答题用时：{q.used_time}秒')
            print()


"""
类名称：User
说明：管理用户相关信息的类

"""
class User:
    def __init__(self):
        self.id = None
        self.name = None
        self.email = None
        self.mentor_email = None
        self.mobile = None
        self.grade = None
        self.register_date = None
        self.verification = None
        self.expired_date = None
        pass
"""
测试代码
"""
if __name__ == "__main__":
    exam = Exam()
    exam.Test()