/**
 * 九色人格计算引擎 — 前端版
 * 与后端 calculator.py 保持算法一致
 */

export interface PersonalityResult {
  nineScores: number[]       // 9个人格得分
  masterPersonality: number  // 主人格索引 (0-8)
  subPersonalities: number[] // 2个辅人格索引
}

// 9种人格名称
export const PERSONALITY_NAMES = ['英雄', '军师', '德鲁伊', '梦想家', '圣人', '天真者', '普通人', '王者', '将军']

// 9种人格对应色值
export const PERSONALITY_COLORS = ['#C0392B', '#2C3E50', '#27AE60', '#E67E22', '#17202A', '#ECF0F1', '#7F8C8D', '#8E44AD', '#F1C40F']

// 同分优先级（索引越小优先级越高）
const PRIORITY = [0, 1, 2, 3, 4, 5, 6, 7, 8]

/**
 * 计算九色人格得分
 * @param answers 63题答案数组，每题0-10分
 *   索引0-8 = 维度1(亲密关系)题1-9
 *   索引9-17 = 维度2(亲子关系)题1-9
 *   ...
 *   索引54-62 = 维度7(原生家庭)题1-9
 */
export function calculatePersonality(answers: number[]): PersonalityResult {
  if (answers.length !== 63) {
    throw new Error(`答案数量应为63题，实际收到${answers.length}题`)
  }

  // 步骤1: 数据归集 — 7维度 × 9题
  const dimensions: number[][] = []
  for (let d = 0; d < 7; d++) {
    const start = d * 9
    dimensions.push(answers.slice(start, start + 9))
  }

  // 步骤2: 交叉计算 — 人格N得分 = 7个维度中第N题的平均分
  const nineScores: number[] = []
  for (let q = 0; q < 9; q++) {
    let total = 0
    for (let d = 0; d < 7; d++) {
      total += dimensions[d][q]
    }
    nineScores.push(Math.round((total / 7) * 100) / 100) // 保留2位小数
  }

  // 步骤3: 排序与判定
  const scored = nineScores.map((score, idx) => ({
    score,
    priority: PRIORITY[idx],
    index: idx,
  }))

  // 按得分降序，同分时按优先级升序
  scored.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score
    return a.priority - b.priority
  })

  const masterPersonality = scored[0].index
  const subPersonalities = [scored[1].index, scored[2].index]

  return {
    nineScores,
    masterPersonality,
    subPersonalities,
  }
}
