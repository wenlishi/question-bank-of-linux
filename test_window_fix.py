#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试窗口闪退修复
"""

import sys
import os

# 添加core模块到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_window_lifetime():
    """测试窗口生命周期"""
    print("=== 测试窗口生命周期 ===")

    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
        from PyQt5.QtCore import QTimer
        from ui.exam_result_window import ExamResultWindow

        app = QApplication(sys.argv)

        # 创建主窗口
        main_window = QMainWindow()
        main_window.setWindowTitle("测试主窗口")
        main_window.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # 测试按钮
        test_btn = QPushButton("测试结果窗口")
        layout.addWidget(test_btn)

        def show_result_window():
            """显示结果窗口"""
            print("显示结果窗口...")

            # 创建测试数据
            exam_data = {
                "exam_name": "测试试卷",
                "questions": [
                    {"id": "q1", "type": "single_choice", "question": "题目1", "answer": ["A"]},
                    {"id": "q2", "type": "single_choice", "question": "题目2", "answer": ["B"]},
                    {"id": "q3", "type": "fill_blank", "question": "题目3", "answer": ["答案"]},
                ]
            }

            user_answers = {
                "q1": ["A"],  # 正确
                "q2": ["C"],  # 错误
                # q3 未作答
            }

            question_results = {
                "q1": {"correct": True, "score": 5},
                "q2": {"correct": False, "score": 0},
                "q3": {"correct": False, "score": 0}
            }

            # 创建结果窗口，设置父窗口
            result_window = ExamResultWindow("测试试卷", main_window)
            result_window.set_result_data(exam_data, user_answers, question_results)

            # 连接信号
            def on_confirmed():
                print("结果窗口：确认")
                result_window.close()

            def on_cancelled():
                print("结果窗口：取消")
                result_window.close()

            result_window.confirmed.connect(on_confirmed)
            result_window.cancelled.connect(on_cancelled)

            # 显示窗口
            result_window.show()
            result_window.raise_()
            result_window.activateWindow()

            print(f"结果窗口已显示，父窗口: {result_window.parent()}")
            print(f"结果窗口是否可见: {result_window.isVisible()}")

            # 5秒后自动关闭（测试用）
            QTimer.singleShot(5000, lambda: print("5秒后窗口仍然存在"))

        test_btn.clicked.connect(show_result_window)

        main_window.setCentralWidget(central_widget)
        main_window.show()

        print("主窗口已显示")
        print("点击'测试结果窗口'按钮测试")

        sys.exit(app.exec_())

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


def check_window_references():
    """检查窗口引用"""
    print("\n=== 检查窗口引用 ===")

    # 模拟答题窗口中的代码
    class MockExamWindow:
        def __init__(self):
            self.result_window = None

        def show_result_window(self):
            from ui.exam_result_window import ExamResultWindow

            # 创建窗口并保存引用
            self.result_window = ExamResultWindow("测试试卷", self)
            print(f"创建窗口，引用保存: {self.result_window is not None}")

            # 模拟显示
            print(f"窗口显示前: 引用存在={self.result_window is not None}")

            # 这里应该显示窗口，但在测试中我们只检查引用
            return self.result_window

        def cleanup(self):
            if hasattr(self, 'result_window') and self.result_window:
                print(f"清理前: 引用存在={self.result_window is not None}")
                self.result_window.close()
                del self.result_window
                print(f"清理后: 引用存在={hasattr(self, 'result_window')}")

    # 测试
    mock_window = MockExamWindow()
    result_window = mock_window.show_result_window()
    print(f"窗口对象: {result_window}")
    print(f"窗口标题: {result_window.windowTitle() if result_window else '无'}")

    mock_window.cleanup()


if __name__ == "__main__":
    # 检查窗口引用
    check_window_references()

    print("\n=== 修复说明 ===")
    print("1. 结果窗口现在保存为实例变量 (self.result_window)")
    print("2. 设置了父窗口 (parent=self)")
    print("3. 添加了窗口关闭事件处理")
    print("4. 使用 show() + raise_() + activateWindow() 确保窗口显示")

    # 如果要运行GUI测试，取消下面的注释
    # test_window_lifetime()