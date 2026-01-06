@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   题库刷题软件 - 商业级安全打包工具
echo          (虚拟环境修复版)
echo ========================================
echo.

REM --- 0. 环境准备 ---
echo [0/6] 检查并激活虚拟环境...
if exist "venv\Scripts\activate.bat" (
    echo 检测到 venv 虚拟环境，正在激活...
    call venv\Scripts\activate.bat
) else (
    echo 未检测到 venv 目录，将使用全局 Python 环境。
)

REM 检查是否在正确的目录
if not exist "user_version" (
    echo 错误: 未找到 user_version 目录
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

REM --- 第一步：依赖检查 ---
echo.
echo [1/6] 检查环境依赖...
python -c "import PyInstaller" 2>nul
if errorlevel 1 pip install pyinstaller
python -c "import pyarmor" 2>nul
if errorlevel 1 pip install pyarmor
python -c "from Crypto.PublicKey import RSA" 2>nul
if errorlevel 1 pip install pycryptodome

REM --- 第二步：清理旧文件 ---
echo.
echo [2/6] 清理旧构建文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "user_version\build" rmdir /s /q "user_version\build"
if exist "user_version\dist" rmdir /s /q "user_version\dist"
if exist "*.spec" del "*.spec"

REM --- 第三步：PyArmor 代码混淆 (核心安全层) ---
echo.
echo [3/6] 正在进行 PyArmor 代码混淆...
echo 正在生成高强度加密代码...

REM 尝试定位 pyarmor 命令
set PYARMOR_CMD=pyarmor
if exist "venv\Scripts\pyarmor.exe" (
    set PYARMOR_CMD=venv\Scripts\pyarmor.exe
)

REM 执行混淆
REM 修改说明：
REM 因为 admin 在根目录，不在 user_version 里，所以不需要 exclude user_version/admin
REM -r user_version 表示只处理 user_version 文件夹里的内容，自然不会包含外面的 admin
%PYARMOR_CMD% gen -O dist/obfuscated -r user_version --platform windows.x86_64 --exclude user_version/tests

if errorlevel 1 (
    echo.
    echo ------------------------------------------------
    echo [错误] PyArmor 混淆失败！
    echo 可能是 PyArmor 未正确安装或路径问题。
    echo 尝试手动运行: pip install pyarmor --upgrade
    echo ------------------------------------------------
    pause
    exit /b 1
)

REM --- 第四步：准备资源文件 ---
echo.
echo [4/6] 迁移资源文件...
REM 复制 data, ui, core 中的非py资源到混淆目录
xcopy "user_version\data" "dist\obfuscated\data\" /E /I /Y >nul
xcopy "user_version\ui" "dist\obfuscated\ui\" /E /I /Y >nul
xcopy "user_version\core" "dist\obfuscated\core\" /E /I /Y >nul

REM --- 第五步：PyInstaller 打包 ---
echo.
echo [5/6] 开始打包 EXE...
echo 目标：dist\obfuscated\main.py

cd dist\obfuscated

pyinstaller --onefile ^
  --windowed ^
  --name="题库刷题软件" ^
  --clean ^
  --noconfirm ^
  --add-data="data;data" ^
  --add-data="ui;ui" ^
  --add-data="core;core" ^
  --strip ^
  --noupx ^
  --hidden-import=PyQt5.QtWidgets ^
  --hidden-import=PyQt5.QtCore ^
  --hidden-import=PyQt5.QtGui ^
  --hidden-import=Crypto ^
  main.py

if errorlevel 1 (
    echo 打包失败！
    cd ..\..
    pause
    exit /b 1
)

REM 将生成的 exe 移动到项目根目录的 dist 下
move "dist\题库刷题软件.exe" "..\..\dist\题库刷题软件.exe"
cd ..\..

REM --- 第六步：验证与完成 ---
echo.
echo [6/6] 验证打包结果...
if exist "dist\题库刷题软件.exe" (
    for %%F in ("dist\题库刷题软件.exe") do (
        set "filesize=%%~zF"
        set /a filesize_mb=!filesize! / 1048576
        echo.
        echo ========================================
        echo          🎉 打包成功！
        echo ========================================
        echo 输出文件: dist\题库刷题软件.exe
        echo 安全等级: ★★★★★ (PyArmor 混淆 + RSA 签名)
        echo.
    )
) else (
    echo ❌ 错误：未找到生成的 EXE 文件。
)

pause