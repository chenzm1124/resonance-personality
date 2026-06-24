/**
 * 博主推荐 API 封装
 */

export interface CreatorVideo {
  title: string
  description: string
  url: string
}

export interface CreatorInfo {
  name: string
  platform: string
  style_tags: string[]
  followers: string
  reason: string
  shooting_direction: string
  videos: CreatorVideo[]
}

export interface RecommendResponse {
  creators: CreatorInfo[]
  cached: boolean
  master_name: string
  sub_names: string[]
}

/**
 * 获取博主推荐
 * @param personalityResult 人格测评结果
 */
export async function getCreatorRecommendations(
  personalityResult: {
    nineScores: number[]
    masterPersonality: number
    subPersonalities: number[]
  }
): Promise<RecommendResponse | null> {
  try {
    // LLM 调用可能需要较长时间，使用自定义超时
    const res = await new Promise<any>((resolve, reject) => {
      uni.request({
        url: 'http://localhost:8000/api/v1/recommend/creators',
        method: 'POST',
        data: personalityResult,
        header: { 'Content-Type': 'application/json' },
        timeout: 60000, // 60秒超时（LLM响应较慢）
        success: (r: any) => {
          if (r.statusCode === 200 && r.data) {
            resolve(r.data)
          } else {
            reject(new Error(`HTTP ${r.statusCode}`))
          }
        },
        fail: (err: any) => reject(err),
      })
    })

    if (res.code === 0 && res.data) {
      return res.data
    }
    return null
  } catch (e) {
    console.error('获取博主推荐失败', e)
    return null
  }
}
