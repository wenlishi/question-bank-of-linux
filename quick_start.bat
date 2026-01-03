@echo off
echo ========================================
echo   题库刷题软件 - 快速启动菜单
echo ========================================
echo.

echo 请选择要启动的程序:
echo.
echo [1] 用户版本 (给客户使用)
echo [2] 激活码管理后台 (生成和管理激活码)
echo [3] 试卷导入工具 (导入6套试卷，需要密码)
echo [4] 测试完整系统
echo [5] 退出
echo.

set /p choice="请输入选项 (1-5): "

if "%choice%"=="1" goto user_version
if "%choice%"=="2" goto activation_admin
if "%choice%"=="3" goto paper_importer
if "%choice%"=="4" goto test_system
if "%choice%"=="5" goto exit

echo 无效选项
pause
goto :eof

:user_version
echo.
echo 启动用户版本...
echo 注意：首次使用需要激活码
python user_version_main.py
pause
goto :eof

:activation_admin
echo.
echo 启动激活码管理后台...
echo 功能：生成、管理、查看激活码
python admin\activation_admin.py
pause
goto :eof

:paper_importer
echo.
echo 启动试卷导入工具...
echo 默认密码：admin123
echo 功能：导入6套试卷，管理试卷数据
python admin\paper_importer.py
pause
goto :eof

:test_system
echo.
echo 测试完整系统...
echo 这将测试所有功能模块
python -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.activation import ActivationManager
    from core.paper_manager import PaperManager

    print('=== 系统测试 ===')
    print('1. 测试激活码系统...')
    manager = ActivationManager()
    test_code = manager.generate_activation_code(days=7, max_uses=1)
    print(f'   生成测试激活码: {test_code}')

    print('2. 测试试卷系统...')
    paper_manager = PaperManager()
    stats = paper_manager.get_statistics()
    print(f'   题目总数: {stats[\"total_questions\"]}')
    print(f'   试卷总数: {stats[\"total_papers\"]}')

    print('✅ 系统测试通过')
    print(f'测试激活码: {test_code}')
    print('有效期: 7天')

except Exception as e:
    print(f'❌ 测试失败: {e}')
"
pause
goto :eof

:exit
echo.
echo 再见！
pause