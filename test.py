import sys
import random
from fractions import Fraction
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class FractionMathApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.generate_question()

    def initUI(self):
        self.setWindowTitle('分数运算练习')
        self.setGeometry(100, 100, 600, 300)

        # 创建控件
        self.question_label = QLabel(self)
        self.question_label.setFont(QFont('Arial', 16))
        self.question_label.setAlignment(Qt.AlignCenter)

        self.answer_input = QLineEdit(self)
        self.answer_input.setFont(QFont('Arial', 14))
        self.answer_input.setPlaceholderText("输入你的答案，例如：3/4 或 5")

        self.submit_button = QPushButton('提交答案', self)
        self.submit_button.setFont(QFont('Arial', 12))
        self.submit_button.clicked.connect(self.check_answer)

        # 布局
        main_layout = QVBoxLayout()

        question_layout = QHBoxLayout()
        question_layout.addWidget(self.question_label)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.answer_input)
        input_layout.addWidget(self.submit_button)

        main_layout.addLayout(question_layout)
        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)

    def generate_question(self):
        """生成一个随机的分数运算题"""
        # 随机选择运算符
        operators = ['+', '-', '*', '/']
        operator = random.choice(operators)

        # 生成两个随机分数
        numerator1 = random.randint(1, 10)
        denominator1 = random.randint(2, 10)
        fraction1 = Fraction(numerator1, denominator1)

        numerator2 = random.randint(1, 10)
        denominator2 = random.randint(2, 10)
        fraction2 = Fraction(numerator2, denominator2)

        # 计算正确答案
        if operator == '+':
            correct_answer = fraction1 + fraction2
        elif operator == '-':
            correct_answer = fraction1 - fraction2
        elif operator == '*':
            correct_answer = fraction1 * fraction2
        elif operator == '/':
            correct_answer = fraction1 / fraction2

        # 格式化正确答案为字符串
        if correct_answer.denominator == 1:
            correct_answer_str = str(correct_answer.numerator)
        else:
            correct_answer_str = f"{correct_answer.numerator}/{correct_answer.denominator}"

        # 格式化问题
        question = f"{numerator1}/{denominator1} {operator} {numerator2}/{denominator2} = ?"

        # 更新界面
        self.question_label.setText(question)
        self.correct_answer = correct_answer_str
        self.answer_input.clear()
        self.answer_input.setFocus()

    def check_answer(self):
        """检查用户输入的答案是否正确"""
        user_answer = self.answer_input.text().strip()

        if not user_answer:
            QMessageBox.warning(self, '警告', '请输入答案！')
            return

        try:
            # 将用户答案转换为分数形式
            if '/' in user_answer:
                numerator, denominator = user_answer.split('/')
                user_fraction = Fraction(int(numerator), int(denominator))
            else:
                user_fraction = Fraction(int(user_answer), 1)

            # 将正确答案转换为分数形式
            if '/' in self.correct_answer:
                correct_numerator, correct_denominator = self.correct_answer.split('/')
                correct_fraction = Fraction(int(correct_numerator), int(correct_denominator))
            else:
                correct_fraction = Fraction(int(self.correct_answer), 1)

            # 比较答案
            if user_fraction == correct_fraction:
                QMessageBox.information(self, '恭喜', '回答正确！')
                self.generate_question()  # 生成下一题
            else:
                QMessageBox.warning(self, '错误', f'回答错误！正确答案是：{self.correct_answer}')
                self.answer_input.clear()
                self.answer_input.setFocus()

        except:
            QMessageBox.warning(self, '错误', '请输入有效的分数格式，例如：3/4 或 5')
            self.answer_input.clear()
            self.answer_input.setFocus()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FractionMathApp()
    ex.show()
    sys.exit(app.exec_())