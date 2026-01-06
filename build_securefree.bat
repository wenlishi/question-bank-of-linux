@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo.
echo ========================================
echo   题库刷题软件 - 商业发布版打包工具
echo      (V6 - 核心逻辑分离加密版)
echo ========================================
echo.

REM --- 0. 环境准备 ---
echo [0/6] 检查虚拟环境...
if exist "venv\Scripts\activate.bat" (
    echo 正在激活 venv...
    call venv\Scripts\activate.bat
) else (
    echo 使用全局 Python 环境。
)

REM 检查关键文件是否存在
if not exist "user_version\main.py" (
    echo 错误: user_version\main.py 未找到！
    pause
    exit /b 1
)
if not exist "user_version\core\app_entry.py" (
    echo 错误: user_version\core\app_entry.py 未找到！
    echo 请确保你已经按照之前的步骤创建了 app_entry.py 文件。
    pause
    exit /b 1
)

REM --- 1. 依赖检查 ---
echo.
echo [1/6] 检查依赖库...
python -c "import PyInstaller" 2>nul
if errorlevel 1 pip install pyinstaller
python -c "import pyarmor" 2>nul
if errorlevel 1 pip install pyarmor
python -c "from Crypto.PublicKey import RSA" 2>nul
if errorlevel 1 pip install pycryptodome

REM --- 2. 清理旧文件 ---
echo.
echo [2/6] 清理旧文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del "*.spec"

REM --- 3. 构建临时工作区 ---
echo.
echo [3/6] 构建临时工作区 (Staging)...
if not exist "dist\staging" mkdir "dist\staging"

echo 复制源码...
REM 扁平化复制：user_version/* -> dist/staging/
xcopy "user_version\*" "dist\staging\" /E /I /Y >nul

echo 复制数据资源...
if exist "data" (
    xcopy "data" "dist\staging\data\" /E /I /Y >nul
)

REM --- 4. PyArmor 核心混淆 ---
echo.
echo [4/6] 正在加密核心逻辑模块...

set PYARMOR_CMD=pyarmor
if exist "venv\Scripts\pyarmor.exe" set PYARMOR_CMD=venv\Scripts\pyarmor.exe

REM 【关键修改】
REM 1. main.py 保持明文（作为引导壳，PyInstaller 能分析它）。
REM 2. 加密 app_entry.py (真实入口)、question_bank.py (核心业务)、license_manager.py (验证锁)。
REM 这样既符合试用版限制，又保护了所有重要逻辑。

echo 正在加密: app_entry.py, question_bank.py, license_manager.py ...

%PYARMOR_CMD% gen -O dist/staging dist/staging/core/app_entry.py dist/staging/core/question_bank.py dist/staging/core/license_manager.py

if errorlevel 1 (
    echo.
    echo [错误] PyArmor 加密失败！
    pause
    exit /b 1
)

echo 核心模块加密完成。main.py 保持明文。

REM --- 5. PyInstaller 打包 ---
echo.
echo [5/6] 开始打包 EXE...
cd dist\staging

REM 【关键修改】显式添加 hidden-import
REM 因为 app_entry 等文件被加密了，PyInstaller 无法分析里面的 import 语句
REM 所以我们必须手动把 UI 模块和其他核心模块加进去

pyinstaller --onefile ^
  --windowed ^
  --name="题库刷题软件" ^
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

REM 移动生成的 exe
move "dist\题库刷题软件.exe" "..\..\dist\题库刷题软件.exe" >nul
cd ..\..

REM --- 6. 验证 ---
echo.
echo [6/6] 验证结果...

if exist "dist\题库刷题软件.exe" (
    for %%F in ("dist\题库刷题软件.exe") do (
        set "filesize=%%~zF"
        set /a filesize_mb=!filesize! / 1048576
        
        echo.
        echo =================================================
        echo    SUCCESS: dist\题库刷题软件.exe 已生成！
        echo =================================================
        echo 大小: !filesize_mb! MB
        echo 安全策略: 引导壳(main) + 核心加密(AppEntry/QuestionBank)
        echo.
        echo 请在纯净环境（无 Python）中测试运行。
    )
) else (
    echo.
    echo ❌ 错误: 未找到生成的 EXE 文件。
)

pause