@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ========================================
echo   极智考典 - 打包修复版 (V11)
echo   修复 AES 加密库丢失导致的闪退问题
echo ========================================
echo.

REM --- 1. 环境与依赖 ---
echo [1/5] 检查环境...
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
pip install pycryptodome >nul 2>&1

REM --- 2. 清理与准备 ---
echo [2/5] 清理旧文件...
if exist "dist\staging" rmdir /s /q "dist\staging"
if not exist "dist\staging" mkdir "dist\staging"

REM 复制源码
xcopy "user_version\*" "dist\staging\" /E /I /Y >nul
if exist "data" xcopy "data" "dist\staging\data\" /E /I /Y >nul
if exist "logo2.ico" copy "logo2.ico" "dist\staging\logo2.ico" /Y >nul

REM --- 3. PyArmor 加密 (关键) ---
echo [3/5] 加密核心代码...
set PYARMOR_CMD=pyarmor
if exist "venv\Scripts\pyarmor.exe" set PYARMOR_CMD=venv\Scripts\pyarmor.exe
%PYARMOR_CMD% gen -O dist/staging dist/staging/core/app_entry.py dist/staging/core/question_bank.py dist/staging/core/license_manager.py
if errorlevel 1 goto error

REM --- 4. PyInstaller 打包 (修复重点) ---
echo [4/5] 正在打包 (已添加 Crypto 完整依赖)...
cd dist\staging

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
  --hidden-import=Crypto.Cipher ^
  --hidden-import=Crypto.Util.Padding ^
  --hidden-import=Crypto.Random ^
  --hidden-import=core ^
  --hidden-import=core.app_entry ^
  --hidden-import=core.question_bank ^
  --hidden-import=core.license_manager ^
  --hidden-import=ui ^
  --hidden-import=ui.main_window ^
  --hidden-import=ui.license_dialog ^
  main.py

if errorlevel 1 goto error

REM --- 5. 提取 ---
cd ..\..
if exist "dist\staging\dist\极智考典.exe" (
    copy "dist\staging\dist\极智考典.exe" "dist\极智考典.exe" /Y >nul
    echo.
    echo [成功] 新文件已生成: dist\极智考典.exe
    echo 请将此文件移动到桌面进行测试！
) else (
    goto error
)
pause
exit /b 0

:error
echo.
echo [失败] 打包过程中出现错误，请检查上方红字。
cd ..\..
pause
exit /b 1