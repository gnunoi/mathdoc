import sys
import os
from tempfile import NamedTemporaryFile
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np


class LaTeXImageGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 创建主窗口
        self.setWindowTitle('LaTeX公式生成器')
        self.setGeometry(100, 100, 800, 600)

        # 创建布局
        layout = QVBoxLayout()

        # 创建显示图片的标签
        self.image_label = QLabel("点击下方按钮生成LaTeX公式", self)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        # 创建按钮
        button = QPushButton("生成LaTeX公式", self)
        button.clicked.connect(self.generate_latex_image)
        layout.addWidget(button)

        # 设置布局
        self.setLayout(layout)

    def generate_latex_image(self):
        # 创建一个临时文件
        with NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
            tmpfile_path = tmpfile.name

        # 创建一个Matplotlib图像
        fig = plt.figure(figsize=(6, 3))
        canvas = FigureCanvas(fig)

        # 使用LaTeX渲染公式
        plt.text(0.5, 0.5, r'$y = \frac{1}{2}x + \sin(x)$',
                 ha='center', va='center', fontsize=20)
        plt.axis('on')

        # 保存图像到临时文件
        plt.savefig(tmpfile_path, dpi=100)
        plt.close(fig)

        # 在标签中显示图片
        pixmap = QPixmap(tmpfile_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)

        # 删除临时文件
        os.unlink(tmpfile_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LaTeXImageGenerator()
    ex.show()
    sys.exit(app.exec_())