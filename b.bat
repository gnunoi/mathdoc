@echo off
setlocal enabledelayedexpansion

:: 定义一个变量，存储需要删除的目录（用空格分隔）
set "directories=build dist"

:: 遍历变量中的每个目录
for %%i in (%directories%) do (
    if exist "%%i" (
        rmdir /s /q "%%i"
    ) 
)

endlocal
pyinstaller -F -w -i favicon.ico mathdoc.py