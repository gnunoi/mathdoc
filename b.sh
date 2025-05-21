#!/bin/bash

# 删除 dist 和 build 目录（如果存在）
echo "删除 dist 和 build 目录..."
rm -rf dist build

# 检查 mathdoc.py 文件是否存在
if [ ! -f "mathdoc.py" ]; then
    echo "错误：mathdoc.py 文件不存在"
    exit 1
fi

# 使用 pyinstaller 打包 mathdoc.py
echo "使用 pyinstaller 打包 mathdoc.py..."
pyinstaller --onefile -i favicon.icns --noupx -w --name mathdoc mathdoc.py

# 检查 pyinstaller 是否成功
if [ $? -eq 0 ]; then
    echo "打包成功！可执行文件位于 dist/mathdoc"
else
    echo "打包失败！"
    exit 1
fi
