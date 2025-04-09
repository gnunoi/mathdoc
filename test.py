from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty

from exam import Exam
from mail import Mail
import random
from datetime import datetime
import time
import os

# 设置窗口大小
Window.size = (1200, 800)

# Kivy UI 定义
kv = '''
<MathQuizUI>:
    orientation: 'vertical'
    spacing: 10
    padding: 10

    # 控制面板
    BoxLayout:
        orientation: 'horizontal'
        spacing: 10
        size_hint_y: None
        height: 300

        # 题型选择
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: None
            width: 200
            Label:
                text: '题型'
                font_size: 24
                size_hint_y: None
                height: 50
            ToggleButton:
                text: '四则运算'
                group: 'type'
                on_press: root.UpdateSettings('type', 0)
            ToggleButton:
                text: '乘法速算'
                group: 'type'
                on_press: root.UpdateSettings('type', 1)

        # 速算类型选择
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: None
            width: 200
            Label:
                text: '乘法速算'
                font_size: 24
                size_hint_y: None
                height: 50
            ToggleButton:
                text: '平方数'
                group: 'quick_calc'
                on_press: root.UpdateSettings('quick_calc', 0)
            ToggleButton:
                text: '平方差法'
                group: 'quick_calc'
                on_press: root.UpdateSettings('quick_calc', 1)
            ToggleButton:
                text: '和十速算法'
                group: 'quick_calc'
                on_press: root.UpdateSettings('quick_calc', 2)
            ToggleButton:
                text: '大数凑十法'
                group: 'quick_calc'
                on_press: root.UpdateSettings('quick_calc', 3)
            ToggleButton:
                text: '逢五凑十法'
                group: 'quick_calc'
                on_press: root.UpdateSettings('quick_calc', 4)
            ToggleButton:
                text: '双向凑十法'
                group: 'quick_calc'
                on_press: root.UpdateSettings('quick_calc', 5)

        # 算术项式选择
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: None
            width: 200
            Label:
                text: '算术项式'
                font_size: 24
                size_hint_y: None
                height: 50
            ToggleButton:
                text: '2项式'
                group: 'term'
                on_press: root.UpdateSettings('term', 2)
            ToggleButton:
                text: '3项式'
                group: 'term'
                on_press: root.UpdateSettings('term', 3)
            ToggleButton:
                text: '4项式'
                group: 'term'
                on_press: root.UpdateSettings('term', 4)
            ToggleButton:
                text: '5项式'
                group: 'term'
                on_press: root.UpdateSettings('term', 5)

        # 运算类型选择
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: None
            width: 200
            Label:
                text: '运算类型'
                font_size: 24
                size_hint_y: None
                height: 50
            ToggleButton:
                text: '加法'
                group: 'operator'
                on_press: root.UpdateSettings('operator', 0)
            ToggleButton:
                text: '减法'
                group: 'operator'
                on_press: root.UpdateSettings('operator', 1)
            ToggleButton:
                text: '乘法'
                group: 'operator'
                on_press: root.UpdateSettings('operator', 2)
            ToggleButton:
                text: '除法'
                group: 'operator'
                on_press: root.UpdateSettings('operator', 3)
            ToggleButton:
                text: '混合运算'
                group: 'operator'
                on_press: root.UpdateSettings('operator', 4)

        # 数值范围输入
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: None
            width: 400
            Label:
                text: '数值范围'
                font_size: 24
                size_hint_y: None
                height: 50
            BoxLayout:
                Label:
                    text: '加减数最小值:'
                    font_size: 20
                TextInput:
                    id: range_min_add
                    text: '0'
                    input_filter: 'int'
                    on_text: root.UpdateSettings('range', 0, int(self.text))
            BoxLayout:
                Label:
                    text: '加减数最大值:'
                    font_size: 20
                TextInput:
                    id: range_max_add
                    text: '100'
                    input_filter: 'int'
                    on_text: root.UpdateSettings('range', 1, int(self.text))
            BoxLayout:
                Label:
                    text: '乘除数最小值:'
                    font_size: 20
                TextInput:
                    id: range_min_mul
                    text: '1'
                    input_filter: 'int'
                    on_text: root.UpdateSettings('range', 2, int(self.text))
            BoxLayout:
                Label:
                    text: '乘除数最大值:'
                    font_size: 20
                TextInput:
                    id: range_max_mul
                    text: '10'
                    input_filter: 'int'
                    on_text: root.UpdateSettings('range', 3, int(self.text))

    # 题目显示区域
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        Label:
            id: question_label
            text: '当前题目：'
            font_size: 32
            halign: 'center'
            valign: 'middle'
            size_hint_y: None
            height: 100

        # 答案输入区域
        BoxLayout:
            orientation: 'vertical'
            TextInput:
                id: answer_input
                hint_text: '输入答案'
                font_size: 32
                multiline: False
                on_text_validate: root.SubmitAnswer()
            Label:
                id: answer_tips_label
                text: ''
                font_size: 24
                halign: 'center'

        # 提示区域
        Label:
            id: tips_label
            text: ''
            font_size: 24
            halign: 'center'
            size_hint_y: None
            height: 50

        # 状态栏
        Label:
            id: status_label
            text: '已答题：0 道 | 正确：0 道 | 错误：0 道 | 正确率：0.0%'
            font_size: 20
            halign: 'center'
            size_hint_y: None
            height: 50

    # 操作按钮
    BoxLayout:
        spacing: 10
        size_hint_y: None
        height: 60
        Button:
            text: '提交答案 (Enter)'
            font_size: 20
            on_press: root.SubmitAnswer()
        Button:
            text: '导出错题本'
            font_size: 20
            on_press: root.ExportWorkbook(1)
        Button:
            text: '导出难题本'
            font_size: 20
            on_press: root.ExportWorkbook(2)
        Button:
            text: '导出习题本'
            font_size: 20
            on_press: root.ExportWorkbook(0)
        Button:
            text: '退出程序'
            font_size: 20
            on_press: root.ExitApp()

<SignupDialog>:
    title: '用户注册'
    size_hint: None, None
    size: 600, 800
    auto_dismiss: False

    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: 20

        TextInput:
            id: username_input
            hint_text: '用户名'
            font_size: 24
            multiline: False
        TextInput:
            id: grade_input
            hint_text: '年级'
            font_size: 24
            multiline: False
        TextInput:
            id: email_input
            hint_text: '邮箱'
            font_size: 24
            multiline: False
        TextInput:
            id: mobile_input
            hint_text: '手机'
            font_size: 24
            multiline: False
        Button:
            text: '发送验证码'
            font_size: 20
            on_press: root.SendVCode()
        TextInput:
            id: code_input
            hint_text: '验证码'
            font_size: 24
            multiline: False
        Button:
            text: '注册'
            font_size: 20
            on_press: root.Register()
'''

Builder.load_string(kv)

class SignupDialog(Popup):
    def __init__(self, exam, **kwargs):
        super(SignupDialog, self).__init__(**kwargs)
        self.exam = exam
        self.VerificationCode = None

    def SendVCode(self):
        email = self.ids.email_input.text
        if not email or '@' not in email:
            print("请输入有效的邮箱")
            return
        self.VerificationCode = str(random.randint(100000, 999999))
        m = Mail()
        m.Receiver = email
        m.Subject = '验证码'
        m.Body = f'验证码：{self.VerificationCode}'
        m.Send()
        print(f"验证码已发送到 {email}")

    def Register(self):
        username = self.ids.username_input.text
        code = self.ids.code_input.text
        email = self.ids.email_input.text
        mobile = self.ids.mobile_input.text
        grade = self.ids.grade_input.text

        if not username:
            print("用户名不能为空")
            return

        if code != self.VerificationCode:
            print("验证码不正确")
            return

        self.exam.SaveUserToDB(username, email, mobile, grade)
        self.dismiss()

class MathQuizUI(BoxLayout):
    question = StringProperty('')
    answer_tips = StringProperty('')
    tips = StringProperty('')
    status = StringProperty('已答题：0 道 | 正确：0 道 | 错误：0 道 | 正确率：0.0%')

    def __init__(self, **kwargs):
        super(MathQuizUI, self).__init__(**kwargs)
        self.exam = Exam()
        self.exam.GetUser()
        self.username = self.exam.username
        self.email = self.exam.email
        self.mobile = self.exam.mobile
        self.grade = self.exam.grade
        self.UpdateQuestion()

    def UpdateSettings(self, setting_type, value=None, index=None):
        if setting_type == 'type':
            self.exam.q.type = value
        elif setting_type == 'quick_calc':
            self.exam.q.quick_calc_type = value
        elif setting_type == 'term':
            self.exam.q.term_count = value
        elif setting_type == 'operator':
            self.exam.operator = value
        elif setting_type == 'range' and index is not None:
            self.exam.num_range[index] = value

        self.exam.q.Set(
            range=self.exam.num_range,
            term_count=self.exam.q.term_count,
            user_operators=self.exam.ops[self.exam.operator]
        )
        self.exam.SaveSettingsToDB()
        self.UpdateQuestion()

    def UpdateQuestion(self):
        # if not self.exam.authorization:
        #     print("软件超过使用期，请联系软件作者")
        #     self.ExitApp()
        question = self.exam.NextQuestion()
        self.ids.question_label.text = f"当前题目：\n{question}"
        self.tips = ''
        self.answer_tips = ''

        total = self.exam.question_number - 1
        correct_rate = self.exam.correct_number / total * 100 if total > 0 else 0
        self.status = (
            f"已答题：{total} 道 | 正确：{self.exam.correct_number} 道 | "
            f"错误：{total - self.exam.correct_number} 道 | 正确率：{correct_rate:.1f}%"
        )
        self.ids.answer_input.focus = True

    def SubmitAnswer(self):
        answer_input = self.ids.answer_input.text.strip()
        answer_input = answer_input.split('=')[-1]
        result = self.exam.SubmitAnswer(answer_input)
        self.ids.answer_input.text = ''

        if result[0]:
            self.UpdateQuestion()
        else:
            self.tips = f'用户答案：{self.exam.user_answer}；检查提示：{self.exam.tips}'
            if self.exam.answer_tips:
                self.answer_tips = f'答题提示：{self.exam.answer_tips}'

    def ExportWorkbook(self, type=None):
        wb_type = {0: "习题本", 1: "错题本", 2: "难题本"}.get(type, "")
        if wb_type:
            self.exam.export_workbook(type)
            print(f"{wb_type}已成功导出。")

    def ExitApp(self):
        self.exam.SaveSettingsToDB()
        self.exam.SaveWorkbook()
        self.exam.CloseDatabase()
        App.get_running_app().stop()

class MathQuizApp(App):
    def build(self):
        return MathQuizUI()

if __name__ == '__main__':
    local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app = MathQuizApp()
    app.run()