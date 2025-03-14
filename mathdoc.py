import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QMessageBox,
                             QLineEdit, QRadioButton, QPushButton, QGroupBox,
                             QVBoxLayout, QHBoxLayout, QFormLayout, QDesktopWidget)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from exam import Exam
from threading import Thread

class MathQuizUI(QWidget):
    def __init__(self):
        super().__init__()
        self.exam = Exam()
        if self.exam.os == "nt":
            self.base_font = QFont("SimSun", 24)  # 修改为24号字
        else:
            self.base_font = QFont("Pingfang SC", 24)  # 修改为24号字
        self.big_font = QFont("Arial", 32)
        self.initUI()
        self.SetWindowSize(self)

    def SetWindowSize(self, window):
        screen = QDesktopWidget().screenGeometry()
        window.setGeometry(0, 0, screen.width(), screen.height())

    def initUI(self):
        self.setWindowTitle(self.exam.title)
        main_layout = QVBoxLayout()
        control_panel = QHBoxLayout()

        # 算术项式
        term_group = QGroupBox("算术项式")
        term_group.setFont(self.base_font)
        term_layout = QVBoxLayout()
        self.radio_terms = [QRadioButton(f'{i + 2}项式') for i in range(4)]
        self.radio_terms[self.exam.q.term_count - 2].setChecked(True)
        for rb in self.radio_terms:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            term_layout.addWidget(rb)
        term_group.setLayout(term_layout)
        control_panel.addWidget(term_group, 1)

        # 运算类型
        operator_group = QGroupBox("运算类型")
        operator_group.setFont(self.base_font)
        operator_layout = QVBoxLayout()
        self.radio_operator = [
            QRadioButton('加法'), QRadioButton('减法'),
            QRadioButton('乘法'), QRadioButton('除法'),
            QRadioButton('混合运算')
        ]
        self.radio_operator[self.exam.operator].setChecked(True)
        for rb in self.radio_operator:
            rb.setFont(self.base_font)
            rb.toggled.connect(self.UpdateSettings)
            operator_layout.addWidget(rb)
        operator_group.setLayout(operator_layout)
        control_panel.addWidget(operator_group, 1)

        # 数值范围
        range_group = QGroupBox("数值范围")
        range_group.setFont(self.base_font)
        range_layout = QFormLayout()
        labels = ["加减数最小值:", "加减数最大值:", "乘除数最小值:", "乘除数最大值:"]
        self.exam.num_edit = [QLineEdit(str(n)) for n in self.exam.num_range]
        for i in range(4):
            self.exam.num_edit[i].setFont(self.base_font)
            self.exam.num_edit[i].setFixedWidth(120)
            self.exam.num_edit[i].setAlignment(Qt.AlignCenter)
            range_layout.addRow(QLabel(labels[i], font=self.base_font), self.exam.num_edit[i])
            self.exam.num_edit[i].editingFinished.connect(self.UpdateSettings)
        range_group.setLayout(range_layout)
        control_panel.addWidget(range_group, 2)

        main_layout.addLayout(control_panel)

        # 题目显示
        self.question_label = QLabel()
        self.question_label.setFont(self.big_font)
        self.question_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.question_label, 2)

        # 答案输入
        self.answer_input = QLineEdit()
        self.answer_input.setFont(self.big_font)
        self.answer_input.setAlignment(Qt.AlignCenter)
        self.answer_input.returnPressed.connect(self.submit_answer)
        main_layout.addWidget(self.answer_input, 1)

        # 状态栏
        self.status_label = QLabel()
        self.status_label.setFont(self.big_font)
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label, 1)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.submit_btn = QPushButton("提交答案 (Enter)")
        self.submit_btn.setFont(self.base_font)
        self.submit_btn.clicked.connect(self.submit_answer)
        self.generate_error_btn = QPushButton("导出错题本")
        self.generate_error_btn.setFont(self.base_font)
        self.generate_error_btn.clicked.connect(lambda: self.ExportWorkbook(1))  # 导出错题
        self.generate_hard_btn = QPushButton("导出难题本")
        self.generate_hard_btn.setFont(self.base_font)
        self.generate_hard_btn.clicked.connect(lambda: self.ExportWorkbook(2))  # 导出难题
        self.generate_all_btn = QPushButton("导出习题本")
        self.generate_all_btn.setFont(self.base_font)
        self.generate_all_btn.clicked.connect(lambda: self.ExportWorkbook(0))  # 导出所有习题
        self.exit_btn = QPushButton("退出程序")
        self.exit_btn.setFont(self.base_font)
        self.exit_btn.clicked.connect(self.ExitApp)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.generate_error_btn)
        btn_layout.addWidget(self.generate_hard_btn)
        btn_layout.addWidget(self.generate_all_btn)
        btn_layout.addWidget(self.exit_btn)
        btn_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        if self.exam.os == "posix":
            self.apply_styles()
        self.answer_input.setFont(self.base_font)
        self.UpdateQuestion()


    def apply_styles(self):
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
        }
        QPushButton {
            min-width: 320px;
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
        """
        self.setStyleSheet(style)

    def UpdateSettings(self):
        # 更新数值范围
        for i in range(4):
            try:
                self.exam.num_range[i] = int(self.exam.num_edit[i].text())
            except:
                pass

        # 更新运算符
        for i in range(5):
            if self.radio_operator[i].isChecked():
                self.exam.operator = i

        # 更新项数
        for i in range(4):
            if self.radio_terms[i].isChecked():
                self.exam.q.term_count = i + 2

        # 更新题目生成器
        self.exam.q.Set(
            range=self.exam.num_range,
            term_count=self.exam.q.term_count,
            user_operators=self.exam.ops[self.exam.operator]
        )

        # 保存设置到数据库
        self.exam.SaveSettingsToDB()

    def UpdateQuestion(self):
        if self.exam.authorization == False:
            QMessageBox.warning(None, "提醒", "软件超过使用期，请联系软件作者")
            self.ExitApp()
        question = self.exam.next_question()
        self.question_label.setText(f"当前题目：\n{question}")

        total = self.exam.question_number - 1
        correct_rate = self.exam.correct_number / total * 100 if total > 0 else 0
        self.status_label.setText(
            f"已答题：{total} 道 | 正确：{self.exam.correct_number} 道 | "
            f"错误：{total - self.exam.correct_number} 道 | 正确率：{correct_rate:.1f}%"
        )
        self.answer_input.setFocus()

    def submit_answer(self):
        result = self.exam.submit_answer(self.answer_input.text().strip())
        self.answer_input.clear()
        if result[0]:
            self.UpdateQuestion()
        else:
            QMessageBox.warning(self, "答案错误", result[1])


    def ExportWorkbook(self, type=None):
        wb = None
        if type == 1:
            wb = "错题本"
        elif type == 2:
            wb = "难题本"
        elif type == 0:
            wb = "习题本"
        else:
            pass
        self.exam.export_workbook(type)
        QMessageBox.information(self, "导出成功", f"{wb}已成功导出。")

    def ExitApp(self):
        self.exam.SaveSettingsToDB()
        self.exam.SaveWorkbook()
        self.exam.CloseDatabase()
        if self.exam.current_row == 1:
            # print(f"self.exam.current_row = {self.exam.current_row}")
            try:
                if os.path.exists(self.exam.file_path): os.remove(self.exam.file_path)
            except Exception as e:
                print(f"删除文件时出错: {e}")
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MathQuizUI()
    window.showMaximized()
    window.exam.SubmitHomework()
    sys.exit(app.exec())
