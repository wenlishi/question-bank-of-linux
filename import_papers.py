#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试卷导入工具
用于导入6套试卷
"""

import json
import os
import sys
from datetime import datetime

# 添加core模块到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.paper_manager import PaperManager, QuestionType

    def create_sample_papers():
        """创建示例试卷数据"""
        print("=== 创建6套示例试卷 ===\n")

        # 创建试卷管理器
        manager = PaperManager()

        # 示例题目数据（你可以替换成你自己的题目）
        sample_questions = [
            # 试卷1: 数学基础
            {
                "type": QuestionType.SINGLE_CHOICE.value,
                "category": "数学",
                "question": "1 + 1 等于多少？",
                "options": ["1", "2", "3", "4"],
                "answer": ["2"],
                "explanation": "基本的加法运算。",
                "score": 5
            },
            {
                "type": QuestionType.SINGLE_CHOICE.value,
                "category": "数学",
                "question": "圆的周长公式是什么？",
                "options": ["πr", "2πr", "πr²", "4πr²"],
                "answer": ["2πr"],
                "explanation": "圆的周长公式是 2πr，其中 r 是半径。",
                "score": 5
            },
            {
                "type": QuestionType.FILL_BLANK.value,
                "category": "数学",
                "question": "三角形的内角和是______度。",
                "options": [],
                "answer": ["180"],
                "explanation": "三角形的内角和总是180度。",
                "score": 5
            },
            # 试卷2: 科学常识
            {
                "type": QuestionType.SINGLE_CHOICE.value,
                "category": "科学",
                "question": "水的化学式是什么？",
                "options": ["H2O", "CO2", "O2", "H2"],
                "answer": ["H2O"],
                "explanation": "水的化学式是 H₂O。",
                "score": 5
            },
            # 试卷3: 语文知识
            {
                "type": QuestionType.FILL_BLANK.value,
                "category": "语文",
                "question": "《静夜思》的作者是______。",
                "options": [],
                "answer": ["李白"],
                "explanation": "《静夜思》是唐代诗人李白的作品。",
                "score": 5
            },
            {
                "type": QuestionType.SINGLE_CHOICE.value,
                "category": "语文",
                "question": "以下哪个成语的意思是'形容非常危险'？",
                "options": ["一帆风顺", "千钧一发", "井井有条", "心旷神怡"],
                "answer": ["千钧一发"],
                "explanation": "千钧一发比喻情况万分危急。",
                "score": 5
            },
            # 试卷4: 英语测试
            {
                "type": QuestionType.SINGLE_CHOICE.value,
                "category": "英语",
                "question": "'Apple'的中文意思是什么？",
                "options": ["苹果", "香蕉", "橘子", "梨"],
                "answer": ["苹果"],
                "explanation": "Apple 是苹果的英文。",
                "score": 5
            },
            {
                "type": QuestionType.FILL_BLANK.value,
                "category": "英语",
                "question": "I ______ a student. (am/is/are)",
                "options": [],
                "answer": ["am"],
                "explanation": "第一人称单数用 am。",
                "score": 5
            },
            # 试卷5: 历史知识
            {
                "type": QuestionType.SINGLE_CHOICE.value,
                "category": "历史",
                "question": "中国的第一个封建王朝是？",
                "options": ["夏朝", "商朝", "周朝", "秦朝"],
                "answer": ["夏朝"],
                "explanation": "夏朝是中国史书中记载的第一个世袭制朝代。",
                "score": 5
            },
            # 试卷6: 地理知识
            {
                "type": QuestionType.SINGLE_CHOICE.value,
                "category": "地理",
                "question": "中国的首都是？",
                "options": ["上海", "北京", "广州", "深圳"],
                "answer": ["北京"],
                "explanation": "北京是中国的首都。",
                "score": 5
            }
        ]

        # 批量添加题目
        print("1. 添加题目...")
        question_ids = manager.batch_add_questions(sample_questions)
        print(f"   添加了 {len(question_ids)} 道题目")

        # 创建6套试卷
        papers = [
            {
                "title": "试卷一：数学基础测试",
                "description": "数学基础知识测试，包含基本运算和几何知识",
                "time_limit": 60,
                "total_score": 100,
                "question_ids": question_ids[0:3]  # 前3题
            },
            {
                "title": "试卷二：科学常识测试",
                "description": "科学常识测试，包含化学、物理等基础知识",
                "time_limit": 60,
                "total_score": 100,
                "question_ids": question_ids[3:6]  # 第4-6题
            },
            {
                "title": "试卷三：语文知识测试",
                "description": "语文知识测试，包含诗词、成语等",
                "time_limit": 60,
                "total_score": 100,
                "question_ids": question_ids[6:8]  # 第7-8题
            },
            {
                "title": "试卷四：英语基础测试",
                "description": "英语基础知识测试",
                "time_limit": 60,
                "total_score": 100,
                "question_ids": question_ids[8:10]  # 第9-10题
            },
            {
                "title": "试卷五：历史知识测试",
                "description": "中国历史知识测试",
                "time_limit": 60,
                "total_score": 100,
                "question_ids": question_ids[10:11]  # 第11题
            },
            {
                "title": "试卷六：地理知识测试",
                "description": "中国地理知识测试",
                "time_limit": 60,
                "total_score": 100,
                "question_ids": question_ids[11:13]  # 第12-13题
            }
        ]

        print("\n2. 创建试卷...")
        created_papers = []
        for i, paper_data in enumerate(papers, 1):
            paper_id = manager.create_paper(
                title=paper_data["title"],
                description=paper_data["description"],
                time_limit=paper_data["time_limit"],
                total_score=paper_data["total_score"]
            )

            # 添加题目到试卷
            for q_id in paper_data["question_ids"]:
                manager.add_question_to_paper(paper_id, q_id)

            created_papers.append(paper_id)
            print(f"   试卷{i}: {paper_data['title']} (ID: {paper_id})")

        # 显示统计信息
        print("\n3. 统计信息:")
        stats = manager.get_statistics()
        print(f"   题目总数: {stats['total_questions']}")
        print(f"   试卷总数: {stats['total_papers']}")
        print(f"   题目类型分布: {stats['question_types']}")
        print(f"   难度分布: {stats['difficulty_levels']}")

        # 导出数据文件（供参考）
        export_file = "data/sample_papers_export.json"
        manager.export_to_json(export_file)
        print(f"\n✅ 数据已导出到: {export_file}")

        print("\n=== 导入完成 ===")
        print("\n你的6套试卷已成功导入系统!")
        print("可以在软件中使用'试卷模式'进行练习。")

        return created_papers

    def import_from_file(json_file):
        """从JSON文件导入试卷"""
        print(f"=== 从文件导入: {json_file} ===\n")

        if not os.path.exists(json_file):
            print(f"❌ 文件不存在: {json_file}")
            return []

        manager = PaperManager()
        imported_count = manager.import_from_json(json_file)

        if imported_count > 0:
            stats = manager.get_statistics()
            print(f"✅ 导入成功!")
            print(f"   导入题目数: {imported_count}")
            print(f"   总题目数: {stats['total_questions']}")
            print(f"   总试卷数: {stats['total_papers']}")
        else:
            print("❌ 导入失败或没有数据")

        return imported_count

    def show_help():
        """显示帮助信息"""
        print("""
试卷导入工具 - 使用说明

命令:
  python import_papers.py create    创建6套示例试卷
  python import_papers.py import <文件>  从JSON文件导入
  python import_papers.py list      列出所有试卷
  python import_papers.py stats     显示统计信息
  python import_papers.py export    导出数据到文件

JSON文件格式示例:
{
  "questions": [
    {
      "type": "single_choice",
      "category": "数学",
      "difficulty": "easy",
      "question": "题目内容",
      "options": ["选项1", "选项2", "选项3", "选项4"],
      "answer": ["正确答案"],
      "explanation": "题目解析",
      "score": 5
    }
  ],
  "papers": [
    {
      "title": "试卷标题",
      "description": "试卷描述",
      "time_limit": 60,
      "total_score": 100,
      "question_ids": [1, 2, 3]
    }
  ]
}
        """)

    def list_papers():
        """列出所有试卷"""
        manager = PaperManager()
        papers = manager.list_papers()

        print("=== 所有试卷 ===\n")

        if not papers:
            print("暂无试卷")
            return

        for paper in papers:
            questions = manager.get_paper_questions(paper["id"])
            print(f"试卷ID: {paper['id']}")
            print(f"标题: {paper['title']}")
            print(f"描述: {paper.get('description', '')}")
            print(f"题目数量: {len(questions)}")
            print(f"时间限制: {paper.get('time_limit', 0)}分钟")
            print(f"总分: {paper.get('total_score', 0)}")
            print(f"状态: {paper.get('status', 'unknown')}")
            print("-" * 50)

    def show_stats():
        """显示统计信息"""
        manager = PaperManager()
        stats = manager.get_statistics()

        print("=== 统计信息 ===\n")
        print(f"题目总数: {stats['total_questions']}")
        print(f"试卷总数: {stats['total_papers']}")

        print("\n题目类型分布:")
        for q_type, count in stats['question_types'].items():
            type_name = {
                "single_choice": "单选题",
                "multiple_choice": "多选题",
                "true_false": "判断题",
                "fill_blank": "填空题"
            }.get(q_type, q_type)
            print(f"  {type_name}: {count}题")

        print("\n难度分布:")
        for difficulty, count in stats['difficulty_levels'].items():
            print(f"  {difficulty}: {count}题")

    def export_data():
        """导出数据"""
        export_file = f"data/papers_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        manager = PaperManager()
        count = manager.export_to_json(export_file, include_questions=True, include_papers=True)

        print(f"✅ 导出成功!")
        print(f"导出文件: {export_file}")
        print(f"导出记录: {count}条")

    # 主函数
    def main():
        if len(sys.argv) < 2:
            show_help()
            return

        command = sys.argv[1].lower()

        if command == "create":
            create_sample_papers()
        elif command == "import" and len(sys.argv) >= 3:
            import_from_file(sys.argv[2])
        elif command == "list":
            list_papers()
        elif command == "stats":
            show_stats()
        elif command == "export":
            export_data()
        else:
            show_help()

    if __name__ == "__main__":
        try:
            main()
        except KeyboardInterrupt:
            print("\n\n程序已退出")
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()

except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("\n请确保依赖已安装:")
    print("pip install PyQt5 pycryptodome")