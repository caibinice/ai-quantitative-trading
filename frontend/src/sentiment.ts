import type { NewsItem } from './types'

export const SENTIMENT_LOOKBACK_DAYS = 7
export const SENTIMENT_HALF_LIFE_DAYS = 7

export interface RecentSentiment {
  score: number
  analyzedCount: number
  counts: Record<string, number>
}

/**
 * Aggregate only recent events. Confidence and a true exponential half-life
 * determine each event's weight; sparse or stale evidence shrinks to neutral.
 */
export function aggregateRecentSentiment(
  items: NewsItem[],
  now = new Date(),
  lookbackDays = SENTIMENT_LOOKBACK_DAYS,
  halfLifeDays = SENTIMENT_HALF_LIFE_DAYS,
): RecentSentiment {
  let weighted = 0
  let weights = 0
  let analyzedCount = 0
  const counts: Record<string, number> = {}

  for (const item of items) {
    const publishedAt = new Date(item.published_at)
    const ageDays = Math.max(0, (now.getTime() - publishedAt.getTime()) / 86_400_000)
    if (!Number.isFinite(ageDays) || ageDays > lookbackDays) continue

    counts[item.label] = (counts[item.label] ?? 0) + 1
    if (item.score === null) continue

    const confidence = Math.max(0.05, Math.min(1, item.confidence ?? 0.5))
    const decay = 0.5 ** (ageDays / halfLifeDays)
    const weight = confidence * decay
    weighted += Math.max(-1, Math.min(1, item.score)) * weight
    weights += weight
    analyzedCount += 1
  }

  return {
    score: weights ? weighted / Math.max(1, weights) : 0,
    analyzedCount,
    counts,
  }
}
