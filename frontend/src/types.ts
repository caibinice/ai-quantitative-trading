export interface Stock {
  symbol: string
  name: string
  market: string
  industry?: string
}

export interface PriceBar {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
  turnover_rate?: number
}

export interface FinancialMetric {
  report_date: string
  report_period: string
  metric_name: string
  metric_value: number | null
  yoy: number | null
}

export interface RankingItem {
  rank: number
  symbol: string
  name: string
  momentum_score: number
  quality_score: number
  sentiment_score: number
  total_score: number
  explanation: Record<string, unknown>
}

export interface NewsItem {
  id: number
  symbol: string
  kind: string
  title: string
  source: string
  source_url: string
  published_at: string
  label: string
  score: number | null
  confidence: number | null
  summary: string
  rationale: string
  model: string
}

export interface StrategyParameters {
  momentum_window: number
  sentiment_lookback_days: number
  sentiment_threshold: number
  minimum_momentum: number
  top_n: number
  momentum_weight: number
  quality_weight: number
  sentiment_weight: number
  fee_rate: number
  slippage_rate: number
  initial_capital: number
}

export interface StrategyConfig {
  id?: number
  name: string
  description: string
  enabled: boolean
  watchlist: string[]
  parameters: StrategyParameters
  updated_at?: string
}

export interface BacktestResult {
  id: number
  name: string
  start_date: string
  end_date: string
  metrics: Record<string, number>
  equity_curve: Array<{
    date: string
    equity: number
    benchmark: number
    drawdown: number
  }>
}
