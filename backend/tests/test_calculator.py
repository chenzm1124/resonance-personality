"""
九色人格计算引擎单元测试
覆盖场景:
  1. 正常计算 — 随机答案
  2. 边界测试 — 全0分
  3. 边界测试 — 全10分（同分优先级验证）
  4. 边界测试 — 极端偏向单一人格
  5. 参数校验 — 答案数量不正确
  6. 参数校验 — 分数超出范围
  7. 九分数总和验证
  8. 主人格+辅人格判定验证
"""

import pytest
from app.core.calculator import (
    calculate_personality,
    PERSONALITY_NAMES,
    PERSONALITY_PRIORITY,
)


class TestCalculatePersonality:
    """计算引擎核心测试"""

    def test_normal_calculation(self):
        """正常随机答案应返回有效的九色人格结果"""
        import random
        random.seed(42)
        answers = [random.randint(0, 10) for _ in range(63)]

        result = calculate_personality(answers)

        assert len(result["nine_scores"]) == 9
        assert 0 <= result["master_personality"] <= 8
        assert len(result["sub_personalities"]) == 2
        # 所有分数应在 0-10 之间
        for score in result["nine_scores"]:
            assert 0 <= score <= 10

    def test_all_zeros(self):
        """全0分 — 所有人格得0分，主人格应为英雄(优先级最高)"""
        answers = [0] * 63
        result = calculate_personality(answers)

        assert result["nine_scores"] == [0.0] * 9
        assert result["master_personality"] == 0  # 英雄
        assert result["sub_personalities"] == [1, 2]  # 军师, 德鲁伊

    def test_all_tens(self):
        """全10分 — 所有人格得10分（AC-16边界测试），主人格应为英雄"""
        answers = [10] * 63
        result = calculate_personality(answers)

        assert result["nine_scores"] == [10.0] * 9
        # 同分优先级：英雄(0) > 军师(1) > 德鲁伊(2) > ...
        assert result["master_personality"] == 0  # 英雄
        assert result["sub_personalities"] == [1, 2]  # 军师, 德鲁伊

    def test_single_personality_dominant(self):
        """极端偏向单一人格 — 只有人格3(梦想家)在所有维度中得高分"""
        answers = [0] * 63
        # 每个维度的第4题(索引3)设为10分，其他为0分
        for d in range(7):
            answers[d * 9 + 3] = 10  # 人格3(梦想家)

        result = calculate_personality(answers)

        assert result["master_personality"] == 3  # 梦想家
        assert result["nine_scores"][3] == 10.0
        # 其他人格应为0分
        for i in range(9):
            if i != 3:
                assert result["nine_scores"][i] == 0.0

    def test_specific_personality_dominant(self):
        """偏向人格8(将军) — 验证非默认优先级"""
        answers = [0] * 63
        # 每个维度的第9题(索引8)设为高分
        for d in range(7):
            answers[d * 9 + 8] = 10  # 将军
            answers[d * 9 + 0] = 5   # 英雄也得5分

        result = calculate_personality(answers)

        assert result["master_personality"] == 8  # 将军
        assert result["nine_scores"][8] == 10.0
        assert result["nine_scores"][0] == 5.0

    def test_wrong_answer_count(self):
        """答案数量不为63时应抛出ValueError"""
        with pytest.raises(ValueError, match="答案数量应为63题"):
            calculate_personality([5] * 62)

        with pytest.raises(ValueError, match="答案数量应为63题"):
            calculate_personality([5] * 64)

    def test_score_out_of_range(self):
        """分数超出0-10范围应抛出ValueError"""
        answers = [5] * 63
        answers[0] = 11  # 超出上限

        with pytest.raises(ValueError, match="超出0-10范围"):
            calculate_personality(answers)

        answers[0] = -1  # 低于下限
        with pytest.raises(ValueError, match="超出0-10范围"):
            calculate_personality(answers)

    def test_score_precision(self):
        """九分数精度应为2位小数"""
        answers = [i % 11 for i in range(63)]
        result = calculate_personality(answers)

        for score in result["nine_scores"]:
            # 检查小数位不超过2位
            assert score == round(score, 2)

    def test_sub_personalities_are_distinct(self):
        """辅人格应与主人格不同，且互不相同"""
        import random
        random.seed(123)
        answers = [random.randint(0, 10) for _ in range(63)]
        result = calculate_personality(answers)

        master = result["master_personality"]
        subs = result["sub_personalities"]

        assert master not in subs
        assert subs[0] != subs[1]

    def test_all_personality_names_defined(self):
        """应有9种人格名称"""
        assert len(PERSONALITY_NAMES) == 9
        assert PERSONALITY_NAMES[0] == "英雄"
        assert PERSONALITY_NAMES[8] == "将军"

    def test_priority_order(self):
        """优先级索引应为0-8"""
        assert PERSONALITY_PRIORITY == list(range(9))


class TestEdgeCases:
    """边界情况测试"""

    def test_min_max_scores(self):
        """混合最低和最高分"""
        answers = []
        for d in range(7):
            for q in range(9):
                answers.append(0 if q % 2 == 0 else 10)

        result = calculate_personality(answers)

        # 奇数题(人格1,3,5,7)应得10分
        for i in [1, 3, 5, 7]:
            assert result["nine_scores"][i] == 10.0
        # 偶数题(人格0,2,4,6,8)应得0分
        for i in [0, 2, 4, 6, 8]:
            assert result["nine_scores"][i] == 0.0

    def test_gradual_increase(self):
        """分数递增 — 人格8应得分最高"""
        answers = []
        for d in range(7):
            for q in range(9):
                answers.append(q + 1)  # 每题1-9分

        result = calculate_personality(answers)

        # 人格8(第9题=9分)应为最高
        assert result["master_personality"] == 8
        assert result["nine_scores"][8] == 9.0
        assert result["nine_scores"][0] == 1.0
