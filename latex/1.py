import matplotlib.pyplot as plt

def plot_setting():
    # 设置全局字体为黑体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['font.size'] = 36  # 设置字体大小
    plt.rcParams['font.style'] = 'normal'  # 设置字体风格为正常

def latex_to_png(latex_formula, output_file, dpi=300, margin=0.5, font_size=36):
    fig = plt.figure(figsize=(1, 1))  # 初始尺寸，后续会自动调整
    # 在图形上添加文本（LaTeX 公式）
    text = fig.text(0, 0, latex_formula) #,  fontdict={'family': 'Arial', 'size': font_size})
    # 自动调整布局，增加边距
    fig.tight_layout(pad=margin)
    # 保存图形为 PNG 文件，自动调整图片大小，背景透明
    fig.savefig(output_file, dpi=dpi, format='png', transparent=True, bbox_inches='tight')
    # 关闭图形，释放资源
    plt.close(fig)

# 示例用法
if __name__ == '__main__':
    plot_setting()
    latex_to_png(r'$E=mc^2$', 'output.png')
    latex_to_png(r'$\int_{a}^{b} f(x)dx$', 'integral.png')
    latex_to_png(r'$\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}$', 'infinite_sum.png', font_size=14)
