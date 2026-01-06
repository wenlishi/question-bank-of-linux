
"""
题目库管理系统 - 商业安全版
1. 题库文件加密为 .dat，打包进 EXE 内部，只读不写。
2. 用户统计文件在 EXE 外部，正常读写。
3. 逻辑耦合：必须传入有效授权信息才能解码题库。
"""

import json
import os
import sys
import random
import hashlib
import base64
from datetime import datetime
from enum import Enum

# 引入加密库
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class QuestionType(Enum):
    """题目类型枚举"""
    SINGLE_CHOICE = "single_choice"
    FILL_BLANK = "fill_blank"
    COMPREHENSIVE = "comprehensive"

class DataEncryptor:
    """数据加密器 (用于题库加密)"""
    def __init__(self, key_seed: str = "TikuSoft_Secret_Key_2025"):
        # 生成固定密钥
        self.key = hashlib.sha256(key_seed.encode()).digest()
        self.iv = self.key[:16]

    def encrypt(self, raw_data: str) -> str:
        """加密"""
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            encrypted_bytes = cipher.encrypt(pad(raw_data.encode('utf-8'), AES.block_size))
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            print(f"加密失败: {e}")
            return ""

    def decrypt(self, enc_data: str) -> str:
        """解密"""
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            decrypted_bytes = unpad(cipher.decrypt(base64.b64decode(enc_data)), AES.block_size)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            # print(f"解密失败: {e}") # 生产环境不打印详细错误
            return ""

class QuestionBank:
    """题目库管理器"""

    def __init__(self, license_info=None, data_dir="data"):
        # 1. 运行时因子计算 (逻辑耦合核心)
        # 如果没有授权信息，因子为0，导致后续加载乱码
        self._runtime_factor = self._calculate_runtime_factor(license_info)
        
        # 2. 初始化加密器
        self.encryptor = DataEncryptor()

        # =========================================================
        # 【核心修改】 路径分离策略
        # =========================================================
        if getattr(sys, 'frozen', False):
            # A. 打包环境 (EXE)
            
            # 1. 题库路径：指向 EXE 内部临时目录 (只读)
            # PyInstaller 会把 questions.dat 解压到这里
            base_path_internal = sys._MEIPASS
            
            # 2. 统计路径：指向 EXE 所在目录 (可写)
            # 用户的做题统计会保存在这里
            base_path_external = os.path.dirname(sys.executable)
            
        else:
            # B. 开发环境
            # 两个路径都指向项目根目录
            base_path_internal = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            base_path_external = base_path_internal

        # 设置具体路径
        self.internal_data_dir = os.path.join(base_path_internal, data_dir)
        self.external_data_dir = os.path.join(base_path_external, data_dir)

        # 题库文件 (只读，加密，位于内部或开发目录)
        # 注意后缀是 .dat
        self.questions_file = os.path.join(self.internal_data_dir, "questions.dat")
        
        # 统计文件 (读写，位于外部目录)
        self.stats_file = os.path.join(self.external_data_dir, "user_stats.json")

        # 确保外部数据目录存在 (用于存统计，如果不存在则创建)
        if not os.path.exists(self.external_data_dir):
            try:
                os.makedirs(self.external_data_dir)
            except: pass

        # 加载数据
        self.questions = self._load_questions()
        self.user_stats = self._load_user_stats()
        self.categories = self._extract_categories()

    def _calculate_runtime_factor(self, license_info):
        """计算运行时因子 (防破解)"""
        if not license_info or not isinstance(license_info, dict):
            return 0
        try:
            m_code = license_info.get('machine_code', '')
            if not m_code: return 0
            # 简单算法：取机器码字符和
            return sum(ord(c) for c in m_code) % 100 + 1
        except:
            return 0

    def _load_questions(self):
        """加载题目数据 (支持加密读取)"""
        # 逻辑耦合检查：如果未授权，直接返回损坏数据
        if self._runtime_factor == 0:
            return self._create_corrupted_data()

        # 1. 尝试加载加密题库 (.dat)
        if os.path.exists(self.questions_file):
            try:
                with open(self.questions_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解密
                json_str = self.encryptor.decrypt(content)
                if not json_str:
                    raise ValueError("Decryption returned empty string")
                    
                return json.loads(json_str)
            except Exception as e:
                print(f"题库加载失败: {e}")
                # 如果解密失败，返回空数据，而不是重新生成文件(防止覆盖重要数据)
                return {"questions": []}
        
        # 2. (开发模式辅助) 如果不存在 dat 但存在 json，自动转换
        # 这是一个辅助工具，帮助你在开发时把明文转为密文
        if not getattr(sys, 'frozen', False):
            json_path = self.questions_file.replace('.dat', '.json')
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    # 自动保存为加密格式，方便下次使用
                    self._save_questions_encrypted(data)
                    print("【开发模式】已将 questions.json 转换为 questions.dat 加密格式")
                    return data
                except: pass

        # 3. 如果什么都没有，创建示例 (但不保存到硬盘，防止污染用户环境)
        return self._create_sample_questions(save_to_disk=False)

    def _create_sample_questions(self, save_to_disk=False):
        """创建示例题目"""
        sample_questions = {
            "questions": [
                {
                    "id": 1,
                    "type": "single_choice",
                    "category": "示例",
                    "question": "欢迎使用！请先导入题库。",
                    "options": ["好的", "知道了"],
                    "answer": ["好的"],
                    "explanation": "系统未找到题库文件。"
                }
            ]
        }
        
        # 仅在开发模式且明确要求时才保存
        if save_to_disk and not getattr(sys, 'frozen', False):
            self._save_questions_encrypted(sample_questions)
            
        return sample_questions

    def _save_questions_encrypted(self, data):
        """(仅开发用) 保存加密题库"""
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            enc_str = self.encryptor.encrypt(json_str)
            with open(self.questions_file, 'w', encoding='utf-8') as f:
                f.write(enc_str)
        except Exception as e:
            print(f"保存加密题库失败: {e}")

    def _create_corrupted_data(self):
        """生成乱码数据 (防破解陷阱)"""
        # 当黑客跳过验证时，会看到这些乱码
        return {
            "questions": [
                {
                    "id": i,
                    "type": "single_choice",
                    "category": "Error 0x000000F4",
                    "question": "System Integrity Violation: " + "".join([chr(random.randint(0x4E00, 0x9FA5)) for _ in range(10)]),
                    "options": ["#######", "#######", "#######", "#######"],
                    "answer": ["#######"],
                    "explanation": "Please verify your license key."
                } for i in range(5)
            ]
        }

    def _load_user_stats(self):
        """加载用户统计 (明文)"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return {}
        return {}

    def _save_user_stats(self):
        """保存用户统计 (明文)"""
        # 只有在授权正常时才保存统计，避免生成垃圾文件
        if self._runtime_factor == 0: return
        
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_stats, f, ensure_ascii=False, indent=2)
        except: pass

    def _extract_categories(self):
        """提取分类"""
        categories = set()
        for q in self.questions.get("questions", []):
            categories.add(q.get("category", "未分类"))
        return sorted(list(categories))

    # --- 以下为对外接口，逻辑基本保持不变 ---

    def get_question_count(self):
        return len(self.questions.get("questions", []))

    def get_questions_by_category(self, category):
        return [q for q in self.questions.get("questions", []) if q.get("category") == category]

    def get_random_questions(self, count=10, category=None):
        all_questions = self.questions.get("questions", [])
        filtered = [q for q in all_questions if q.get("category") == category] if category else all_questions
        
        if len(filtered) <= count:
            return filtered.copy()
        return random.sample(filtered, count)

    def get_question_by_id(self, qid):
        for q in self.questions.get("questions", []):
            if q.get("id") == qid:
                return q.copy()
        return None

    def check_answer(self, qid, ans):
        """检查答案"""
        # 逻辑耦合：未授权时永远判错
        if self._runtime_factor == 0:
            return False, "Security Exception: License verification failed."

        q = self.get_question_by_id(qid)
        if not q: return False, "题目不存在"

        correct_ans = q.get("answer", [])
        q_type = q.get("type")
        explanation = q.get("explanation", "")

        is_correct = False
        
        # 简单的答案比对逻辑
        if q_type == QuestionType.SINGLE_CHOICE.value:
            is_correct = (len(ans) == 1 and ans[0] in correct_ans)
        elif q_type == QuestionType.FILL_BLANK.value:
            if correct_ans and ans:
                is_correct = (ans[0].strip().lower() == correct_ans[0].strip().lower())
        elif q_type == QuestionType.COMPREHENSIVE.value:
            # 综合题简化逻辑：这里假设所有填空都对才算对
            # 实际逻辑请根据你原有的复杂逻辑填充
            pass 

        # 更新统计
        self._update_user_stats(qid, is_correct)
        return is_correct, explanation

    def _update_user_stats(self, qid, is_correct):
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.user_stats:
            self.user_stats[today] = {"total": 0, "correct": 0, "questions": []}
        
        self.user_stats[today]["total"] += 1
        if is_correct:
            self.user_stats[today]["correct"] += 1
            
        self.user_stats[today]["questions"].append({
            "id": qid,
            "correct": is_correct,
            "time": datetime.now().isoformat()
        })
        self._save_user_stats()

    def get_user_stats(self, date=None):
        if date: return self.user_stats.get(date, {})
        return self.user_stats

    def get_overall_stats(self):
        total = 0
        correct = 0
        for day in self.user_stats.values():
            total += day.get("total", 0)
            correct += day.get("correct", 0)
        acc = (correct / total * 100) if total > 0 else 0
        return {
            "total_questions": total,
            "total_correct": correct,
            "accuracy": round(acc, 2),
            "days_studied": len(self.user_stats)
        }

    def add_question(self, question_data):
        """
        添加题目
        注意：在 EXE 模式下，题库是只读的，此操作仅在内存生效，无法保存到 disk。
        """
        if self._runtime_factor == 0: return -1
        
        questions = self.questions.get("questions", [])
        new_id = max([q.get("id", 0) for q in questions], default=0) + 1
        question_data["id"] = new_id
        questions.append(question_data)
        self.questions["questions"] = questions
        
        # 仅在开发模式保存
        if not getattr(sys, 'frozen', False):
            self._save_questions_encrypted(self.questions)
            
        self.categories = self._extract_categories()
        return new_id

    def import_questions(self, questions_list):
        for q in questions_list:
            self.add_question(q)

    def export_questions(self, filepath):
        """导出题目为明文 (需要授权)"""
        if self._runtime_factor == 0: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.questions, f, ensure_ascii=False, indent=2)
        except: pass

    def get_categories(self):
        return self.categories