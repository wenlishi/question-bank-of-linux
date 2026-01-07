
@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo.
echo ========================================
echo   极智考典 - 商业发布版打包工具
echo      (V9 - 增加应用图标版)
echo ========================================
echo.

REM --- 0. 环境准备 ---
echo [0/6] 检查虚拟环境...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM --- 1. 依赖检查 ---
echo [1/6] 检查依赖库...
python -c "import PyInstaller" 2>nul
if errorlevel 1 pip install pyinstaller
python -c "import pyarmor" 2>nul
if errorlevel 1 pip install pyarmor
python -c "from Crypto.PublicKey import RSA" 2>nul
if errorlevel 1 pip install pycryptodome

REM --- 2. 清理旧文件 ---
echo [2/6] 清理旧文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del "*.spec"

REM --- 3. 构建临时工作区 ---
echo [3/6] 构建临时工作区...
if not exist "dist\staging" mkdir "dist\staging"

echo 复制源码...
xcopy "user_version\*" "dist\staging\" /E /I /Y >nul

echo 复制资源...
if exist "data" (
    xcopy "data" "dist\staging\data\" /E /I /Y >nul
)

REM ========================================================
REM 【新增】复制图标文件
REM ========================================================
if exist "logo2.ico" (
    echo 正在复制应用图标...
    copy "logo2.ico" "dist\staging\logo2.ico" /Y >nul
) else (
    echo [警告] 未在根目录找到 logo.ico，打包出的 EXE 将使用默认图标。
)

REM ========================================================
REM 数据清理 (同 V8)
REM ========================================================
echo 正在清理敏感用户数据...
if exist "dist\staging\data\questions.json" del "dist\staging\data\questions.json"
if exist "dist\staging\data\user_progress.json" del "dist\staging\data\user_progress.json"
if exist "dist\staging\data\user_progress.dat" del "dist\staging\data\user_progress.dat"
if exist "dist\staging\data\activations.json" del "dist\staging\data\activations.json"
if exist "dist\staging\data\user_stats.json" del "dist\staging\data\user_stats.json"
echo 用户数据清理完毕。

REM --- 4. PyArmor 核心混淆 ---
echo [4/6] 正在加密核心逻辑...

set PYARMOR_CMD=pyarmor
if exist "venv\Scripts\pyarmor.exe" set PYARMOR_CMD=venv\Scripts\pyarmor.exe

REM 加密核心文件
%PYARMOR_CMD% gen -O dist/staging dist/staging/core/app_entry.py dist/staging/core/question_bank.py dist/staging/core/license_manager.py

if errorlevel 1 (
    echo [错误] PyArmor 加密失败！
    pause
    exit /b 1
)

REM --- 5. PyInstaller 打包 ---
echo [5/6] 开始打包 EXE...
cd dist\staging

REM ========================================================
REM 【关键修改】增加 --icon 和修改 --name
REM ========================================================
pyinstaller --onefile ^
  --windowed ^
  --name="极智考典" ^
  --icon="logo2.ico" ^
  --clean ^
  --noconfirm ^
  --paths="." ^
  --add-data="data;data" ^
  --noupx ^
  --hidden-import=PyQt5 ^
  --hidden-import=PyQt5.QtWidgets ^
  --hidden-import=PyQt5.QtCore ^
  --hidden-import=PyQt5.QtGui ^
  --hidden-import=Crypto ^
  --hidden-import=core ^
  --hidden-import=core.app_entry ^
  --hidden-import=core.question_bank ^
  --hidden-import=core.license_manager ^
  --hidden-import=core.protection ^
  --hidden-import=ui ^
  --hidden-import=ui.main_window ^
  --hidden-import=ui.license_dialog ^
  main.py

if errorlevel 1 (
    echo 打包失败！
    cd ..\..
    pause
    exit /b 1
)

REM --- 6. 提取与完成 ---
echo.
echo [6/6] 正在提取 EXE 文件...
cd ..\..

if exist "dist\staging\dist\极智考典.exe" (
    if not exist "dist" mkdir "dist"
    copy "dist\staging\dist\极智考典.exe" "dist\极智考典.exe" /Y >nul
    
    echo.
    echo =================================================
    echo    SUCCESS: 打包成功！(已包含图标)
    echo =================================================
    echo.
    echo 软件位置: dist\极智考典.exe
    echo.
) else (
    echo.
    echo ❌ 错误: 未找到生成的 EXE。
)

pause