#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
【明文入口】仅负责引导，不包含核心逻辑
"""
import sys
import os

# 导入核心逻辑模块
# 这个模块之后会被 PyArmor 加密，PyInstaller 能分析到这个导入
try:
    from core import app_entry
except ImportError as e:
    # 防止黑客删除核心文件
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, f"核心组件丢失: {e}", "启动错误", 0x10)
    sys.exit(1)

if __name__ == "__main__":
    # 将控制权移交给加密模块
    app_entry.run_application()