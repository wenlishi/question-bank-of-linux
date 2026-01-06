@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   题库刷题软件 - 用户版本打包工具
echo ========================================
echo.

REM 检查是否在正确的目录
if not exist "user_version" (
    echo 错误: 未找到 user_version 目录
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 进入 user_version 目录
cd user_version

REM 检查依赖是否安装
echo 检查Python依赖...
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo PyQt5 未安装，正在安装...
    pip install PyQt5>=5.15.0
) else (
    echo ✓ PyQt5 已安装
)

python -c "from Crypto.Cipher import AES" 2>nul
if errorlevel 1 (
    echo pycryptodome 未安装，正在安装...
    pip install pycryptodome>=3.15.0
) else (
    echo ✓ pycryptodome 已安装
)

echo.
echo ========================================
echo   开始打包用户版本
echo ========================================
echo.

REM 清理旧的打包文件
if exist "build" (
    echo 清理旧的 build 目录...
    rmdir /s /q build
)

if exist "dist" (
    echo 清理旧的 dist 目录...
    rmdir /s /q dist
)

if exist "题库刷题软件.spec" (
    echo 清理旧的 spec 文件...
    del "题库刷题软件.spec"
)

echo.
echo 正在打包，请稍候...
echo.

REM PyInstaller 打包命令
pyinstaller --onefile ^
  --windowed ^
  --name="题库刷题软件" ^
  --clean ^
  --noconfirm ^
  --add-data="data;data" ^
  --add-data="ui;ui" ^
  --add-data="core;core" ^
  --exclude-module=admin ^
  --exclude-module=generate_codes ^
  --exclude-module=encrypt_exams ^
  --exclude-module=decrypt_exams ^
  --exclude-module=import_papers ^
  --exclude-module=fix_activation_data ^
  --exclude-module=manage_image_mapping ^
  --hidden-import=PyQt5.QtWidgets ^
  --hidden-import=PyQt5.QtCore ^
  --hidden-import=PyQt5.QtGui ^
  --hidden-import=crypto ^
  --hidden-import=crypto.Cipher ^
  --hidden-import=crypto.Cipher.AES ^
  --hidden-import=Crypto.PublicKey.RSA ^
  --hidden-import=Crypto.Cipher.PKCS1_OAEP ^
  --hidden-import=Crypto.Signature.pkcs1_15 ^
  --hidden-import=Crypto.Hash.SHA256 ^
  main.py

if errorlevel 1 (
    echo.
    echo ✗ 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.

REM 显示生成的文件信息
if exist "dist\题库刷题软件.exe" (
    for %%F in ("dist\题库刷题软件.exe") do (
        set "filesize=%%~zF"
        set /a filesize_mb=!filesize! / 1048576
        echo ✓ EXE文件: dist\题库刷题软件.exe
        echo ✓ 文件大小: !filesize_mb! MB
    )

    echo.
    echo 下一步操作:
    echo 1. 测试 dist\题库刷题软件.exe 是否正常运行
    echo 2. 将exe文件分发给用户
    echo 3. 使用 admin\activation_admin.py 生成激活码
    echo 4. 将激活码提供给用户
) else (
    echo ✗ EXE文件未生成！
)

echo.
pause