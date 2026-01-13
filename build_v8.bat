@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo.
echo ========================================
echo   极智考典 - 商业发布版打包工具
echo      (V8 - 排除用户数据版)
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

REM --- 3. 构建临时工作区 (关键修改) ---
echo [3/6] 构建临时工作区...
if not exist "dist\staging" mkdir "dist\staging"

echo 复制源码...
xcopy "user_version\*" "dist\staging\" /E /I /Y >nul

echo 复制资源...
if exist "data" (
    xcopy "data" "dist\staging\data\" /E /I /Y >nul
)

REM ========================================================
REM 【重点修改】在这里删除不需要打包进 EXE 的用户数据文件
REM 这样打包出的软件就是“干净”的，且支持用户保存进度到外部
REM ========================================================
echo 正在清理敏感用户数据...

REM 1. 删除用户进度 (必须排除，否则用户无法保存)
if exist "dist\staging\data\user_progress.json" (
    del "dist\staging\data\user_progress.json"
    echo   - 已排除: user_progress.json
)

REM 2. 删除激活记录 (建议排除，让用户重新激活)
if exist "dist\staging\data\activations.json" (
    del "dist\staging\data\activations.json"
    echo   - 已排除: activations.json
)

REM 3. 删除用户统计 (建议排除)
if exist "dist\staging\data\user_stats.json" (
    del "dist\staging\data\user_stats.json"
    echo   - 已排除: user_stats.json
)

REM 注意：questions.json 和 pics 文件夹会被保留，因为它们是题库基础数据
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

REM 执行打包
pyinstaller --onefile ^
  --windowed ^
  --name="极智考典" ^
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
  --hidden-import=ui.new_main_window ^
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
    echo    SUCCESS: 打包成功！(已排除用户数据)
    echo =================================================
    echo.
    echo 软件位置: dist\极智考典.exe
    echo.
    echo [重要提示]
    echo 软件运行时，会自动在 EXE 旁边创建 data 文件夹
    echo 用于存放新的 user_progress.json。
    echo.
) else (
    echo.
    echo ❌ 错误: 未找到生成的 EXE。
)

pause