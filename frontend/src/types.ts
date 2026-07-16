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
  benchmark_symbol: string
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

export interface ResearchTask {
  id: number
  task_type: string
  status: 'queued' | 'running' | 'success' | 'failed' | 'cancelled'
  priority: number
  payload: Record<string, unknown>
  result: Record<string, unknown>
  error: string
  progress: number
  attempts: number
  max_attempts: number
  worker_id: string | null
  created_at: string
  started_at: string | null
  finished_at: string | null
}

export interface InfrastructureSummary {
  calendar: { count: number; first_date: string | null; last_date: string | null }
  benchmarks: Array<{
    symbol: string
    name: string
    count: number
    latest_date: string | null
  }>
  pit_financials: { count: number; latest_available_at: string | null }
}

export interface PitFinancial {
  report_date: string
  available_at: string
  metric_name: string
  metric_value: number
  source: string
  is_estimated: boolean
}

export interface DataQualityIssue {
  id: number
  category: string
  severity: 'critical' | 'warning' | 'info'
  entity_type: string
  entity_id: string
  title: string
  detail: Record<string, unknown>
  first_seen_at: string
  last_seen_at: string
  resolved_at: string | null
}

export interface WalkForwardRun {
  id: number
  name: string
  start_date: string
  end_date: string
  benchmark_symbol: string
  parameters: Record<string, unknown>
  windows: Array<{
    train_start: string
    train_end: string
    test_start: string
    test_end: string
    selected_momentum_window: number
    selected_sentiment_threshold: number
    selection_score: number
    train_metrics: Record<string, number>
    test_metrics: Record<string, number>
  }>
  metrics: Record<string, number>
  equity_curve?: Array<{
    date: string
    equity: number
    benchmark: number
    drawdown: number
  }>
  created_at: string
}
