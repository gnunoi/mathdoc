"""
pip install ntplib pandas pyqt5 xlsxwriter
"""
import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QMessageBox,
                             QLineEdit, QRadioButton, QPushButton, QGroupBox,
                             QVBoxLayout, QHBoxLayout, QFormLayout, QDesktopWidget,
                             QDialog)
from PyQt5.QtGui import (QFont, QPalette, QColor, QScreen)
from PyQt5.QtCore import (Qt, QRect)
from exam import *

def GetScreenSize():
    screen = QDesktopWidget().screenGeometry()
    return screen.width(), screen.height()

"""
类名称：MathDoc
说明：数字博士App的UI

成员变量：
appname: 软件名称
author：软件作者
authorization: 软件授权
base_font: 基本字体
big_font: 大字体
height: 窗口高度
title: 软件标题
version: 软件版本
width: 窗口宽度

成员对象：
exam: 测试对象

成员函数：
Register(): 用户注册
InitUI(): UI初始化
UpdateQuestion(): 更新试题
SubmitAnswer(): 提交答案
SetWindowSize(): 设置窗口大小
"""
class MathDoc(QWidget):
    def __init__(self):
        super().__init__()
        self.appname = "数字博士"
        self.author = "致慧星空工作室出品"
        self.version = "2025.05.30(V1.5.1)"
        self.title = f"{self.appname}({self.author})，版本：{self.version}"
        self.set_list = []
        self.sets = set([])
        self.exam = Exam()
        self.Register()
        self.authorization= Authorization()
        if os.name == "nt":
            self.base_font = QFont("SimSun", 24)
        else:
            self.base_font = QFont("Pingfang SC", 24)
        self.big_font = QFont("Arial", 32)
        self.screen_geometry = QDesktopWidget().screenGeometry()
        self.setGeometry(self.screen_geometry)
        self.prompter = TelePrompter(self)
        if self.prompter.second_screen:
            self.prompter.showMaximized()
        self.InitUI()

    def InitUI(self):
        self.setWindowTitle(self.title)

        main_layout = QVBoxLayout()
        control_panel = QHBoxLayout()

        self.type_group = QGroupBox("题型")
        self.type_group.setFont(self.base_font)
        type_layout = QVBoxLayout()
        self.type_options = [
            QRadioButton('计算24点'), # type = 0
            QRadioButton('乘法速算'), # type = 1
            QRadioButton('四则运算'), # type = 2
            QRadioButton('质因数分解'), # type = 3
            QRadioButton('解方程'),  # type = 4
            QRadioButton('单位换算'),  # type = 5
        ]
        self.type_options[self.exam.setting.type].setChecked(True)
        for rb in self.type_options:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            type_layout.addWidget(rb)
        self.type_group.setLayout(type_layout)
        control_panel.addWidget(self.type_group, 1)

        # 速算
        self.qc_group = QGroupBox("速算类型")
        self.qc_group.setFont(self.base_font)
        qc_layout = QVBoxLayout()
        self.qc_options = [
            QRadioButton('和十速算法'),  # 0
            QRadioButton('逢五凑十法'),  # 1
            QRadioButton('平方差法'),  # 2
            QRadioButton('平方数'), # 3
            QRadioButton('小数凑十法'),  # 4
            QRadioButton('大数凑十法'), # 5
            QRadioButton('双向凑十法'), # 6
            QRadioButton('综合练习'), # 7
        ]
        if not any(rb.isChecked() for rb in self.qc_options):
            self.qc_options[self.exam.setting.type_qc].setChecked(True)
        for rb in self.qc_options:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            qc_layout.addWidget(rb)
        self.qc_group.setLayout(qc_layout)
        control_panel.addWidget(self.qc_group, 1)

        # 质因数分解题型
        self.factor_group = QGroupBox("质因数题型")
        self.factor_group.setFont(self.base_font)
        factor_layout = QVBoxLayout()
        self.factor_radios = [QRadioButton('质因数分解'),
                              QRadioButton('最大公约数'),
                              QRadioButton('最小公倍数')]
        self.factor_radios[self.exam.setting.factor_type].setChecked(True)
        for rb in self.factor_radios:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            factor_layout.addWidget(rb)
        self.factor_group.setLayout(factor_layout)
        control_panel.addWidget(self.factor_group, 1)

        # 算术项数
        self.term_group = QGroupBox("算术项数")
        self.term_group.setFont(self.base_font)
        term_layout = QVBoxLayout()
        self.radio_terms = [QRadioButton(f'{i + 2}项') for i in range(4)]
        self.radio_terms[self.exam.setting.sn_term].setChecked(True)
        for rb in self.radio_terms:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            term_layout.addWidget(rb)
        self.term_group.setLayout(term_layout)
        control_panel.addWidget(self.term_group, 1)

        # 运算类型
        self.operator_group = QGroupBox("运算类型")
        self.operator_group.setFont(self.base_font)
        operator_layout = QVBoxLayout()
        self.radio_operator = [
            QRadioButton('加法'),
            QRadioButton('减法'),
            QRadioButton('乘法'),
            QRadioButton('除法'),
            QRadioButton('混合运算')
        ]
        self.radio_operator[self.exam.setting.sn_operator].setChecked(True)
        for rb in self.radio_operator:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            operator_layout.addWidget(rb)
        self.operator_group.setLayout(operator_layout)
        control_panel.addWidget(self.operator_group, 1)

        # 方程题型
        self.equation_group = QGroupBox("方程类型")
        self.equation_group.setFont(self.base_font)
        equation_layout = QVBoxLayout()
        self.equation_options = [
            QRadioButton('一元一次方程'),  # 0
            QRadioButton('二元一次方程组'),  # 1
            QRadioButton('一元二次方程'),  # 2
        ]
        if not any(rb.isChecked() for rb in self.equation_options):
            self.equation_options[self.exam.setting.type_equation].setChecked(True)
        for rb in self.equation_options:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            equation_layout.addWidget(rb)
        self.equation_group.setLayout(equation_layout)
        control_panel.addWidget(self.equation_group, 1)

        # 单位换算题型
        self.conversion_group = QGroupBox("单位换算题型")
        self.conversion_group.setFont(self.base_font)
        conversion_layout = QVBoxLayout()
        self.conversion_options = [
            QRadioButton('长度换算'),  # 0
            QRadioButton('面积换算'),  # 1
            QRadioButton('体积换算'),  # 2
            QRadioButton('质量换算'),  # 3
            QRadioButton('时间换算'),  # 4
        ]
        if not any(rb.isChecked() for rb in self.conversion_options):
            self.conversion_options[self.exam.setting.type_conversion].setChecked(True)
        for rb in self.conversion_options:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            conversion_layout.addWidget(rb)
        self.conversion_group.setLayout(conversion_layout)
        control_panel.addWidget(self.conversion_group, 1)

        # 数值范围
        self.range_groups = []
        self.num_edit = []
        self.num_label = []
        widget_lists = [[{'label' : '24点最小值:', 'number' : 'min_24point'},
                   {'label' : '24点最大值:', 'number' : 'max_24point'}],
                  [{'label' : '乘数最小值:', 'number' : 'min_qc'},
                   {'label' : '乘数最大值:', 'number' : 'max_qc'}],
                  [{'label' : '加减数最小值:', 'number' : 'min_addend'},
                   {'label' : '加减数最大值:', 'number' : 'max_addend'},
                   {'label' : '乘除数最小值:', 'number' : 'min_divisor'},
                   {'label' : '乘除数最大值:', 'number' : 'max_divisor'}],
                  [{'label' : '合数最小值:', 'number' : 'min_composite'},
                   {'label' : '合数最大值:', 'number' : 'max_composite'}],
                  [{'label' : '系数最小值:', 'number': 'min_coefficient'},
                   {'label' : '系数最大值:', 'number': 'max_coefficient'},
                   {'label' : '常数最小值:', 'number': 'min_constant'},
                   {'label' : '常数最大值:', 'number': 'max_constant'}],
                  ]
        for wl in widget_lists:
            range_group = QGroupBox("数值范围")
            range_group.setFont(self.base_font)
            range_layout = QFormLayout()
            num_edit_list = []
            num_label_list = []
            for w in wl:
                number = getattr(self.exam.setting, w['number'])
                num_edit = QLineEdit(str(number))
                num_label = QLabel(w['label'], font=self.base_font)
                num_edit.setFont(self.base_font)
                num_edit.setFixedWidth(360)
                num_edit.setAlignment(Qt.AlignCenter)
                range_layout.addRow(num_label, num_edit)
                num_edit.editingFinished.connect(self.UpdateSettings)
                num_edit_list.append(num_edit)
                num_label_list.append(num_label)
            self.num_edit.append(num_edit_list)
            self.num_label.append(num_label_list)
            range_group.setLayout(range_layout)
            control_panel.addWidget(range_group, 2)
            self.range_groups.append(range_group)
        main_layout.addLayout(control_panel)

        # 题目显示
        self.question_label = QLabel()
        self.question_label.setFont(self.big_font)
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setObjectName("question_label")
        main_layout.addWidget(self.question_label, 2)

        # 答案输入
        self.answer_input = QLineEdit()
        self.answer_input.setFont(self.big_font)
        self.answer_input.setAlignment(Qt.AlignCenter)
        self.answer_input.returnPressed.connect(self.SubmitAnswer)

        # 答题注释
        self.answer_label = QLabel()
        self.answer_label.setFont(self.base_font)
        self.answer_label.setAlignment(Qt.AlignCenter)
        self.answer_label.setText(self.exam.q.comments)
        main_layout.addWidget(self.answer_input, 1)
        main_layout.addWidget(self.answer_label, 1)

        # 提示栏
        self.check_tips_label = QLabel()
        self.check_tips_label.setFont(self.base_font)
        self.check_tips_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.check_tips_label, 1)
        self.answer_tips_label = QLabel()
        self.answer_tips_label.setFont(self.base_font)
        self.answer_tips_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.answer_tips_label, 1)

        # 状态栏
        self.status_label = QLabel()
        self.status_label.setFont(self.base_font)
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label, 1)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.review_btn = QPushButton("复习")
        self.review_btn.setFont(self.base_font)
        # self.submit_btn.clicked.connect(self.SubmitAnswer)
        self.submit_btn = QPushButton("提交答案")
        self.submit_btn.setFont(self.base_font)
        self.submit_btn.clicked.connect(self.SubmitAnswer)
        self.generate_error_btn = QPushButton("导出错题本")
        self.generate_error_btn.setFont(self.base_font)
        self.generate_error_btn.clicked.connect(lambda: self.ExportWorkbook(1))
        self.generate_hard_btn = QPushButton("导出难题本")
        self.generate_hard_btn.setFont(self.base_font)
        self.generate_hard_btn.clicked.connect(lambda: self.ExportWorkbook(2))
        self.generate_all_btn = QPushButton("导出习题本")
        self.generate_all_btn.setFont(self.base_font)
        self.generate_all_btn.clicked.connect(lambda: self.ExportWorkbook(0))
        self.exit_btn = QPushButton("退出程序")
        self.exit_btn.setFont(self.base_font)
        self.exit_btn.clicked.connect(self.ExitApp)
        # btn_layout.addStretch(1)
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.generate_error_btn)
        btn_layout.addWidget(self.generate_hard_btn)
        btn_layout.addWidget(self.generate_all_btn)
        btn_layout.addWidget(self.review_btn)
        btn_layout.addWidget(self.exit_btn)
        # btn_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.answer_input.setObjectName("answer_input")
        if os.name == "posix":
            self.SetStyle()
        self.answer_input.setFont(self.big_font)
        palette = QPalette()
        palette.setColor(QPalette.WindowText, QColor(0, 120, 215)) #0078D7
        self.check_tips_label.setPalette(palette)
        self.answer_tips_label.setPalette(palette)

        self.set_list = [
            set([self.range_groups[0]]), # type = 0
            set([self.qc_group, self.range_groups[1]]), # type = 1 # 24点题型
            set([self.term_group, self.operator_group,self.range_groups[2]]), # type = 2 # 速算题型
            set([self.factor_group, self.range_groups[3]]), # type = 3 # 质因数分解题型
            set([self.equation_group, self.range_groups[4]]),  # type = 4 # 解方程题型
            set([self.conversion_group]),  # type = 5 # 单位换算题型
        ]
        self.sets = set([])
        for s in self.set_list:
            self.sets |= s
        self.UpdateSettings()

    def SetStyle(self):
        style = """
        QGroupBox {
            border: 2px solid #0078D7;
            border-radius: 10px;
            margin-top: 15px;
            padding: 15px;
            font-size: 24px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            color: #0078D7;
            font-size: 24px;
        }
        QPushButton {
            min-width: 200px;
            padding: 12px;
            font-size: 24px;
            background: #F0F0F0;
            border: 2px solid #CCCCCC;
            border-radius: 8px;
        }
        QPushButton:hover {
            background: #E0E0E0;
        }
        QLineEdit {
            border: 3px solid #0078D7;
            border-radius: 8px;
            padding: 10px;
            font-size: 24px;
        }
        QLineEdit#answer_input {
            font-size: 36px;
        }
        """
        self.setStyleSheet(style)

    def ChangeState(self):
        type = self.exam.setting.type
        if not type in range(0, len(self.set_list)):
            print(f'无效的类型')
            return False
        for s in self.sets - self.set_list[type]:
            s.setVisible(False)
        for s in self.set_list[type]:
            s.setVisible(True)
        return True

    def UpdateSettings(self):
        self.exam.setting.min_24point = int(self.num_edit[0][0].text())
        self.exam.setting.max_24point = int(self.num_edit[0][1].text())
        self.exam.setting.min_qc = int(self.num_edit[1][0].text())
        self.exam.setting.max_qc = int(self.num_edit[1][1].text())
        self.exam.setting.min_addend = int(self.num_edit[2][0].text())
        self.exam.setting.max_addend = int(self.num_edit[2][1].text())
        self.exam.setting.min_divisor = int(self.num_edit[2][2].text())
        self.exam.setting.max_divisor = int(self.num_edit[2][3].text())
        self.exam.setting.min_composite = int(self.num_edit[3][0].text())
        self.exam.setting.max_composite = int(self.num_edit[3][1].text())
        self.exam.setting.min_coefficient = int(self.num_edit[4][0].text())
        self.exam.setting.max_coefficient = int(self.num_edit[4][1].text())
        self.exam.setting.min_constant = int(self.num_edit[4][2].text())
        self.exam.setting.max_constant = int(self.num_edit[4][3].text())
        if self.exam.setting.min_24point > self.exam.setting.max_24point:
            self.exam.setting.min_24point, self.exam.setting.max_24point = (self.exam.setting.max_24point, self.exam.setting.min_24point)
            self.num_edit[0][0].setText(str(self.exam.setting.min_24point))
            self.num_edit[0][1].setText(str(self.exam.setting.max_24point))
        if not self.exam.setting.min_24point in range(1, 4):
            self.exam.setting.min_24point = 3
            self.num_edit[0][0].setText(str(self.exam.setting.min_24point))
        if not self.exam.setting.max_24point in range(8, 14):
            self.exam.setting.max_24point = 8
            self.num_edit[0][1].setText(str(self.exam.setting.max_24point))
        if self.exam.setting.min_qc > self.exam.setting.max_qc:
            self.exam.setting.min_qc, self.exam.setting.max_qc = (self.exam.setting.max_qc, self.exam.setting.min_qc)
            self.num_edit[1][0].setText(str(self.exam.setting.min_qc))
            self.num_edit[1][1].setText(str(self.exam.setting.max_qc))
        if self.exam.setting.max_qc - self.exam.setting.min_qc < 10:
            self.exam.setting.max_24point = self.exam.setting.min_qc + 10
            self.num_edit[1][1].setText(str(self.exam.setting.max_qc))
        if self.exam.setting.min_addend > self.exam.setting.max_addend:
            self.exam.setting.min_addend, self.exam.setting.max_addend = (self.exam.setting.max_addend, self.exam.setting.min_addend)
            self.num_edit[2][0].setText(str(self.exam.setting.min_addend))
            self.num_edit[1][1].setText(str(self.exam.setting.max_addend))
        if self.exam.setting.min_divisor > self.exam.setting.max_divisor:
            self.exam.setting.min_divisor, self.exam.setting.max_divisor = (self.exam.setting.max_divisor, self.exam.setting.min_divisor)
            self.num_edit[2][2].setText(str(self.exam.setting.min_divisor))
            self.num_edit[2][3].setText(str(self.exam.setting.max_divisor))
        if self.exam.setting.min_composite > self.exam.setting.max_composite:
            self.exam.setting.min_composite, self.exam.setting.max_composite = (self.exam.setting.max_composite, self.exam.setting.min_composite)
            self.num_edit[3][0].setText(str(self.exam.setting.min_composite))
            self.num_edit[3][1].setText(str(self.exam.setting.max_composite))
        if self.exam.setting.min_coefficient > self.exam.setting.max_coefficient:
            self.exam.setting.min_coefficient, self.exam.setting.max_coefficient = (self.exam.setting.max_coefficient, self.exam.setting.min_coefficient)
            self.num_edit[4][0].setText(str(self.exam.setting.min_coefficient))
            self.num_edit[4][1].setText(str(self.exam.setting.max_coefficient))
        if self.exam.setting.min_constant > self.exam.setting.max_constant:
            self.exam.setting.min_constant, self.exam.setting.max_constant = (self.exam.setting.max_constant, self.exam.setting.min_constant)
            self.num_edit[4][2].setText(str(self.exam.setting.min_constant))
            self.num_edit[4][3].setText(str(self.exam.setting.max_constant))
        for i, rb in enumerate(self.type_options):
            if rb.isChecked():
                self.exam.setting.type = i
                self.ChangeState()
                if i == 0:
                    self.exam.UpdateSetting(type=self.exam.setting.type,
                                            subtype = [0],
                                            range = [self.exam.setting.min_24point,
                                                     self.exam.setting.max_24point])
                elif i == 1:
                    for i, rb in enumerate(self.qc_options):
                        if rb.isChecked():
                            self.exam.setting.type_qc = i
                            break
                    self.exam.UpdateSetting(type=self.exam.setting.type,
                                            subtype = [self.exam.setting.type_qc],
                                            range = [self.exam.setting.min_qc,
                                                     self.exam.setting.max_qc])
                elif i == 2:
                    for i in range(4):
                        if self.radio_terms[i].isChecked():
                            self.exam.setting.sn_term = i
                    for i in range(5):
                        if self.radio_operator[i].isChecked():
                            self.exam.setting.sn_operator = i
                    self.exam.UpdateSetting(type=self.exam.setting.type,
                                            subtype = [self.exam.setting.sn_term,
                                                       self.exam.setting.sn_operator],
                                            range = [self.exam.setting.min_addend,
                                                     self.exam.setting.max_addend,
                                                     self.exam.setting.min_divisor,
                                                     self.exam.setting.max_divisor])
                elif i == 3:
                    for i, rb in enumerate(self.factor_radios):
                        if rb.isChecked():
                            self.exam.setting.factor_type = i
                            break
                    self.exam.UpdateSetting(type=self.exam.setting.type,
                                            subtype = [self.exam.setting.factor_type],
                                            range = [self.exam.setting.min_composite,
                                                     self.exam.setting.max_composite])
                elif i == 4:
                    for i, rb in enumerate(self.equation_options):
                        if rb.isChecked():
                            self.exam.setting.type_equation = i
                            break
                    self.exam.UpdateSetting(type=self.exam.setting.type,
                                            subtype = [self.exam.setting.type_equation],
                                            range = [self.exam.setting.min_coefficient,
                                                     self.exam.setting.max_coefficient,
                                                     self.exam.setting.min_constant,
                                                     self.exam.setting.max_constant])
                elif i == 5 :
                    for i, rb in enumerate(self.conversion_options):
                        if rb.isChecked():
                            self.exam.setting.type_conversion = i
                            break
                    self.exam.UpdateSetting(type=self.exam.setting.type,
                                            subtype=[self.exam.setting.type_conversion])
        self.exam.setting.Write()
        self.UpdateQuestion()
        self.answer_input.clear() # 更新题目以后，清除用户答案
        self.answer_label.setText(self.exam.q.comments)

    def UpdateQuestion(self):
        if self.authorization.authorization == False:
            QMessageBox.warning(None, "提醒", "软件超过使用期，请联系软件作者")
            self.ExitApp()
        self.exam.Generate()
        self.check_tips_label.setText('')
        self.answer_tips_label.setText('')
        self.question_label.setText(f"{self.exam.q.question}")
        self.answer_label.setText(self.exam.q.comments)

        total = self.exam.record.question_number - 1
        correct_rate = self.exam.record.correct_number / total * 100 if total > 0 else 0
        self.status_label.setText(
            f"已答题：{total} 道 | 正确：{self.exam.record.correct_number} 道 | "
            f"错误：{total - self.exam.record.correct_number} 道 | 正确率：{correct_rate:.1f}%"
        )
        self.answer_input.setFocus()
        self.exam.q.AnswerTips()
        self.prompter.Update(self.exam.q.question, self.exam.q.check_tips, self.exam.q.answer_tips)

    def SubmitAnswer(self):
        self.exam.q.user_input = self.answer_input.text()
        self.exam.SubmitAnswer()
        self.answer_input.clear()
        if not self.exam.q.is_correct:
            self.check_tips_label.setText(f'用户答案：{self.exam.q.user_answer}，检查提示：{self.exam.q.check_tips}')
            if self.exam.q.answer_tips:
                self.answer_tips_label.setText(f'答题提示：{self.exam.q.answer_tips}')
            if self.exam.q.error_number >= 3:
                self.exam.record.question_number += 1
                self.exam.q.error_number = 0
                self.UpdateQuestion()
            self.prompter.Update(self.exam.q.question, self.exam.q.check_tips, self.exam.q.answer_tips)
        else:
            self.UpdateQuestion()

    def Register(self):
        while not self.exam.user.IsCompleted():
            signup = SignupDialog(self.exam)
            signup.exec()

    def SetWindowSize(self):
        self.setGeometry(0, 0, self.width, self.height)


    def ExportWorkbook(self, type):
        self.exam.ExportRecords(type)
        name = ['习题本', '错题本', '难题本']
        QMessageBox.information(self, '导出答题记录', f'{name[type]}已导出')

    def closeEvent(self, event):
        self.exam.Exit()
        event.accept()

    def ExitApp(self):
        self.exam.Exit()
        QApplication.quit()

class SignupDialog(QDialog):
    import ast
    def __init__(self, exam):
        super().__init__()
        self.exam = exam
        self.vcode = str(random.randint(100000, 999999))
        self.ucode = self.vcode
        self.username = exam.user.username
        self.grade = exam.user.grade
        self.mobile = exam.user.mobile
        self.email = exam.user.email
        self.mentor_email = exam.user.mentor_email
        self.InitDialog()

    def InitDialog(self):
        if os.name == "nt":
            self.base_font = QFont("SimSun", 24)
        else:
            self.base_font = QFont("Pingfang SC", 24)
        width, height = GetScreenSize()
        self.setWindowTitle("用户注册")

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setSpacing(32)

        # 创建控件的标签文本和初始值的列表
        form_items = [
            {"label": "用 户 名（必填）:", "value": self.username},
            {"label": "年级（数字1-12，必填）:", "value": self.grade},
            {"label": "手　　机（必填）:", "value": self.mobile},
            {"label": "本人邮箱（必填）:", "value": self.email},
            {"label": "教师/家长邮箱（选填）:", "value": self.mentor_email},
            {"label": "邮箱验证码（必填）:", "value": ''}
        ]
        # 创建输入框对象并添加到表单布局中
        self.inputs = []
        for item in form_items:
            label = QLabel(item["label"])
            label.setFont(self.base_font)
            input = QLineEdit()
            input.setFont(self.base_font)
            # input.returnPressed.connect(self.Register)
            if item["value"]:
                input.setText(str(item["value"]))
                input.setEnabled(False)
            form_layout.addRow(label, input)
            self.inputs.append(input)

        if not self.email is None and self.email.find('@'): # 已注册用户，补全其它信息，不重复发送验证码
            self.inputs[5].setText(str(self.vcode))
            self.inputs[5].setEnabled(False)

        # 创建按钮及其对应的槽函数的列表
        buttons = [
            {"text": "发送邮箱验证码", "func": self.SendVCode},
            {"text": "用户注册", "func": self.Register},
            {"text": "退出软件", "func": self.Exit}
        ]

        # 创建按钮布局
        btn_layout = QHBoxLayout()
        for button in buttons:
            btn = QPushButton(button["text"])
            btn.setFont(self.base_font)
            btn.clicked.connect(button["func"])
            btn_layout.addStretch(1)
            btn_layout.addWidget(btn)
            if button["text"] == "用户注册":
                self.register_btn = btn  # 保存“用户注册”按钮的引用
                btn.setDefault(True)  # 设置为默认按钮
        btn_layout.addStretch(1)

        # 组装主布局
        main_layout.addLayout(form_layout)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        if os.name == "posix":
            self.SetStyle()

    def Exit(self):
        sys.exit()

    def Register(self):
        if not self.email is None:
            print(f'self.email = {self.email}')
            self.ucode = self.vcode
        # 依次获取输入框中的值
        self.username = self.inputs[0].text()
        self.grade = self.inputs[1].text()
        self.mobile = self.inputs[2].text()
        self.email = self.inputs[3].text()
        self.mentor_email = self.inputs[4].text()
        self.ucode = self.inputs[5].text()
        try:
            grade = self.ast.literal_eval(self.grade)
        except:
            grade = 0
        try:
            mobile = self.ast.literal_eval(self.mobile)
        except:
            mobile = 0
        if self.username.strip() == '':
            QMessageBox.warning(self, '用户名', '用户名不能为空')
            return
        if not grade in range(1, 13):
            QMessageBox.warning(self, '年级', '年级必须是1-12的数字，请重新输入')
            return
        if self.email.strip() == '' or self.email.find('@') == -1:
            QMessageBox.warning(self, '邮箱', '邮箱不能为空')
            return
        if not mobile in range(int(1e10), int(2e10)):
            QMessageBox.warning(self, '手机号', '手机号必须为11位有效号码')
            return
        if self.ucode != self.vcode:
            QMessageBox.warning(self, '邮箱', '请输入正确的验证码')
            return

        QMessageBox.information(self, '注册成功', f'{self.username}用户注册成功，邮箱：{self.email}')

        self.exam.user.Register(username=self.username, email=self.email, mobile=self.mobile,
                                grade=self.grade, mentor_email=self.mentor_email)
        self.close()

    def SendVCode(self):
        email = self.inputs[3].text()
        if email == '' or email.find('@') == -1:
            QMessageBox.warning(self, '邮箱', '请输入有效的邮箱')
        else:
            m = Mail()
            m.receiver = email
            m.subject = '验证码'
            m.body = '验证码：\n' + self.vcode
            m.Send()
            QMessageBox.information(self, '验证码已发送', f'验证码已发送，请在邮箱{email}中查收邮件。')

    def SetStyle(self):
        style = """
        QPushButton {
            min-width: 200px;
            padding: 12px;
            font-size: 24px;
            background: #F0F0F0;
            border: 2px solid #CCCCCC;
            border-radius: 8px;
        }
        QPushButton:hover {
            background: #E0E0E0;
        }
        QLineEdit {
            min-width: 320px;
            border: 3px solid #0078D7;
            border-radius: 8px;
            padding: 10px;
            font-size: 24px;
        }
        QLabel {
            font-size: 24px;
        }
        """
        self.setStyleSheet(style)

import ntplib
class Authorization:
    def __init__(self):
        self.magic_date = "2025-12-28"  # 月份2位，不满2位补0
        self.authorization = True
        self.GetNetTimeInThread(self.HandleAuthorization)
        # self.GetNetTime()

    def GetNetTime(self):
        servers = ['ntp.aliyun.com', 'time.hicloud.com', 'ntp.ntsc.ac.cn',
                   'ntp.tuna.tsinghua.edu.cn']
        ntp_client = ntplib.NTPClient()
        for server in servers:
            try:
                response = ntp_client.request(server)
                utc_time = datetime.fromtimestamp(response.tx_time)
                tz_time = utc_time.astimezone()
                local_date = tz_time.strftime("%Y-%m-%d")
                return local_date
            except Exception as e:
                print(f"Error fetching NTP time: {e}")
        return None

    def GetNetTimeInThread(self, callback):
        def wrapper():
            callback(self.GetNetTime())

        Thread(target=wrapper).start()

    def HandleAuthorization(self, net_time):
        if net_time:
            self.authorization = net_time <= self.magic_date
        else:
            self.authorization = True


class TelePrompter(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.second_screen = None
        self.InitUI()

    def InitUI(self):
        self.setWindowTitle("提词器")

        # 获取屏幕信息
        screens = QApplication.instance().screens()
        if len(screens) >= 2:
            # 获取第二个屏幕的几何信息
            screen_geometry = screens[1].geometry()
            self.second_screen = screens[1]
            print(self.second_screen)
        else:
            print("第二屏幕未检测到")
            screen_geometry = screens[0].geometry()
        # 设置窗口在第屏幕的位置和大小
        self.setGeometry(screen_geometry)
        # 创建主布局
        main_layout = QVBoxLayout()
        print(screen_geometry)
        # 创建题目显示标签控件
        self.question_label = QLabel("题目", self)
        self.question_label.setFont(QFont("Arial", 60))
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setStyleSheet("QLabel { background-color: #F0F0F0; }")
        main_layout.addWidget(self.question_label)

        # 创建题目显示标签控件
        self.check_label = QLabel("检查提示", self)
        self.check_label.setFont(QFont("Arial", 60))
        self.check_label.setAlignment(Qt.AlignCenter)
        self.check_label.setStyleSheet("QLabel { background-color: #F0F0F0; color: #C03020;}")
        main_layout.addWidget(self.check_label)

        # 创建答案显示标签控件
        self.answer_label = QLabel("答案提示", self)
        self.answer_label.setFont(QFont("Arial", 60))
        self.answer_label.setAlignment(Qt.AlignCenter)
        self.answer_label.setStyleSheet("QLabel { background-color: #F0F0F0; color: #0078D7;}")
        main_layout.addWidget(self.answer_label)

        # 设置窗口布局
        self.setLayout(main_layout)

    def Update(self, question, check_tips, answer_tips):
        self.question_label.setText(f'题目：{question}')
        self.check_label.setText(f'检查提示：\n{check_tips}')
        self.answer_label.setText(f'答题提示：\n{answer_tips}')

if __name__ == '__main__':
    local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app = QApplication(sys.argv)
    window = MathDoc()
    window.showMaximized()
    sys.exit(app.exec())