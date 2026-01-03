@echo off
echo 启动题库刷题软件...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 检查依赖包...
pip list | findstr PyQt5 >nul
if errorlevel 1 (
    echo 安装PyQt5...
    pip install PyQt5
)

pip list | findstr pycryptodome >nul
if errorlevel 1 (
    echo 安装pycryptodome...
    pip install pycryptodome
)

echo.
echo 启动软件...
python main.py

pause