"""九色人格计算引擎 — 服务端双校验"""

from typing import TypedDict

# 9种人格名称（索引0-8对应题号1-9）
PERSONALITY_NAMES = ["英雄", "军师", "德鲁伊", "梦想家", "圣人", "天真者", "普通人", "王者", "将军"]

# 同分优先级（索引越小优先级越高）
PERSONALITY_PRIORITY = list(range(9))  # 英雄(0) > 军师(1) > ... > 将军(8)


class PersonalityResult(TypedDict):
    nine_scores: list[float]       # 9个人格得分
    master_personality: int        # 主人格索引 (0-8)
    sub_personalities: list[int]   # 2个辅人格索引


def calculate_personality(answers: list[int]) -> PersonalityResult:
    """
    计算九色人格得分。

    参数:
        answers: 63题答案列表，每题0-10分。
                 索引0-8 = 维度1(亲密关系)题1-9
                 索引9-17 = 维度2(亲子关系)题1-9
                 ...
                 索引54-62 = 维度7(原生家庭)题1-9

    返回:
        PersonalityResult 包含 nine_scores, master_personality, sub_personalities
    """
    if len(answers) != 63:
        raise ValueError(f"答案数量应为63题，实际收到{len(answers)}题")

    for i, score in enumerate(answers):
        if not (0 <= score <= 10):
            raise ValueError(f"第{i+1}题得分{score}超出0-10范围")

    # 步骤1: 数据归集 — 7维度 × 9题
    # dimensions[d][q] = 维度d中题号q的分数
    dimensions: list[list[int]] = []
    for d in range(7):
        start = d * 9
        dimensions.append(answers[start:start + 9])

    # 步骤2: 交叉计算 — 人格N得分 = 7个维度中第N题的平均分
    nine_scores: list[float] = []
    for q in range(9):
        total = sum(dimensions[d][q] for d in range(7))
        nine_scores.append(round(total / 7, 2))

    # 步骤3: 排序与判定
    # 创建 (得分, 优先级索引, 人格索引) 元组列表
    scored = [(nine_scores[i], PERSONALITY_PRIORITY[i], i) for i in range(9)]
    # 按得分降序，同分时按优先级升序（索引越小越优先）
    scored.sort(key=lambda x: (-x[0], x[1]))

    master_personality = scored[0][2]
    sub_personalities = [scored[1][2], scored[2][2]]

    return PersonalityResult(
        nine_scores=nine_scores,
        master_personality=master_personality,
        sub_personalities=sub_personalities,
    )
