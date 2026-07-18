import { CalendarCheck2, DatabaseZap, RefreshCcw, ShieldAlert, ShieldCheck } from 'lucide-react'
import ReactECharts from 'echarts-for-react'
import { useEffect, useMemo, useState } from 'react'
import { api, formatNumber } from '../api'
import { PageHeader } from '../components/PageHeader'
import { ErrorPanel, Loading } from '../components/StatePanel'
import { chartPalette, useTheme } from '../theme-context'
import type { DataQualityIssue, InfrastructureSummary, PitFinancial, Stock } from '../types'

interface QualitySummary { active_by_severity: Record<string, number>; latest_run: null | { id: number; checks_count: number; issues_count: number; finished_at: string; details: Record<string, unknown> } }
interface BenchmarkBar { date: string; close: number; source: string }

export function DataQuality() {
  const { theme } = useTheme()
  const chart = chartPalette(theme)
  const [infrastructure, setInfrastructure] = useState<InfrastructureSummary | null>(null)
  const [quality, setQuality] = useState<QualitySummary | null>(null)
  const [issues, setIssues] = useState<DataQualityIssue[]>([])
  const [stocks, setStocks] = useState<Stock[]>([])
  const [symbol, setSymbol] = useState('')
  const [pit, setPit] = useState<PitFinancial[]>([])
  const [benchmark, setBenchmark] = useState<BenchmarkBar[]>([])
  const [loading, setLoading] = useState(true)
  const [action, setAction] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const load = async () => {
    try {
      const [infra, qualityData, issueRows, stockRows, benchmarkRows] = await Promise.all([api<InfrastructureSummary>('/infrastructure/summary'), api<QualitySummary>('/data-quality/summary'), api<DataQualityIssue[]>('/data-quality/issues'), api<Stock[]>('/stocks'), api<BenchmarkBar[]>('/benchmarks/000300/prices')])
      setInfrastructure(infra); setQuality(qualityData); setIssues(issueRows); setStocks(stockRows); setBenchmark(benchmarkRows)
      if (!symbol && stockRows[0]) setSymbol(stockRows[0].symbol)
      setLoading(false)
    } catch (err) { setError((err as Error).message); setLoading(false) }
  }
  useEffect(() => { load() }, [])
  useEffect(() => { if (symbol) api<PitFinancial[]>(`/financials/pit/${symbol}`).then(setPit).catch((err: Error) => setError(err.message)) }, [symbol])

  const enqueue = async (type: 'sync' | 'quality') => {
    setAction(type); setError(''); setMessage('')
    try {
      const endpoint = type === 'sync' ? '/infrastructure/sync' : '/data-quality/run'
      const response = await api<{ task_id: number }>(endpoint, { method: 'POST', body: JSON.stringify(type === 'sync' ? { symbols: stocks.map((item) => item.symbol), benchmark_symbol: '000300' } : { symbols: stocks.map((item) => item.symbol), benchmark_symbol: '000300' }) })
      setMessage(`任务 #${response.task_id} 已进入队列，可到“任务中心”查看进度。`)
    } catch (err) { setError((err as Error).message) }
    finally { setAction('') }
  }
  const resolve = async (id: number) => { await api(`/data-quality/issues/${id}/resolve`, { method: 'POST' }); load() }

  const benchmarkOption = useMemo(() => ({ tooltip: { trigger: 'axis' }, grid: { left: 58, right: 18, top: 20, bottom: 34 }, xAxis: { type: 'category', boundaryGap: false, data: benchmark.map((item) => item.date), axisLabel: { color: chart.muted }, axisLine: { lineStyle: { color: chart.line } } }, yAxis: { type: 'value', scale: true, axisLabel: { color: chart.muted }, splitLine: { lineStyle: { color: chart.split } } }, dataZoom: [{ type: 'inside', start: Math.max(0, 100 - 12000 / Math.max(1, benchmark.length)), end: 100 }], series: [{ type: 'line', showSymbol: false, data: benchmark.map((item) => item.close), lineStyle: { color: '#a989ff', width: 2 }, areaStyle: { color: '#a989ff12' } }] }), [benchmark, chart.line, chart.muted, chart.split])

  if (error && !infrastructure) return <ErrorPanel message={error} />
  if (loading || !infrastructure || !quality) return <Loading label="载入数据治理信息…" />

  return <>
    <PageHeader eyebrow="Data observability" title="数据治理与研究底座" description="统一查看交易日历、点时财务、指数基准和质量告警；任何缺口先被发现，再进入研究。" actions={<><button className="button" onClick={() => enqueue('sync')} disabled={!!action}><DatabaseZap size={16} />{action === 'sync' ? '入队中' : '同步基础数据'}</button><button className="button primary" onClick={() => enqueue('quality')} disabled={!!action}><ShieldCheck size={16} />{action === 'quality' ? '入队中' : '运行质量检查'}</button></>} />
    {(error || message) && <div className={`inline-alert ${message ? 'success' : ''}`}>{error || message}</div>}
    <section className="governance-stats"><article className="panel governance-card"><CalendarCheck2 /><span>交易日历</span><strong>{formatNumber(infrastructure.calendar.count, 0)}</strong><small>{infrastructure.calendar.first_date} → {infrastructure.calendar.last_date}</small></article><article className="panel governance-card"><DatabaseZap /><span>点时财务观测</span><strong>{formatNumber(infrastructure.pit_financials.count, 0)}</strong><small>最新可得日 {infrastructure.pit_financials.latest_available_at ?? '—'}</small></article><article className="panel governance-card"><ShieldAlert /><span>活跃严重告警</span><strong className="danger-text">{quality.active_by_severity.critical ?? 0}</strong><small>警告 {quality.active_by_severity.warning ?? 0} · 最近检查 #{quality.latest_run?.id ?? '—'}</small></article><article className="panel governance-card"><ShieldCheck /><span>最近规则检查</span><strong>{quality.latest_run?.checks_count ?? 0}</strong><small>发现 {quality.latest_run?.issues_count ?? 0} 个问题</small></article></section>
    <section className="governance-grid"><article className="panel benchmark-panel"><div className="panel-head"><div><span className="section-kicker">INDEX BENCHMARK</span><h2>沪深 300 基准行情</h2></div><span className="source-chip">{infrastructure.benchmarks[0]?.latest_date ?? '待同步'}</span></div>{benchmark.length ? <ReactECharts key={theme} option={benchmarkOption} style={{ height: 320 }} /> : <div className="empty-inline">暂无指数数据</div>}</article><article className="panel pit-panel"><div className="panel-head"><div><span className="section-kicker">POINT-IN-TIME</span><h2>指定时点可得财务</h2></div><select value={symbol} onChange={(event) => setSymbol(event.target.value)}>{stocks.map((item) => <option key={item.symbol} value={item.symbol}>{item.symbol} · {item.name}</option>)}</select></div><p>只返回公告日期不晚于今天的数据，报告期与真正可得日期分开保存。</p><div className="pit-list">{pit.slice(0, 8).map((item) => <div key={`${item.report_date}-${item.available_at}-${item.metric_name}`}><span>{item.metric_name}<small>报告期 {item.report_date} · 可得 {item.available_at}</small></span><strong>{formatNumber(item.metric_value)}</strong></div>)}</div></article></section>
    <section className="panel table-panel issue-panel"><div className="panel-head"><div><span className="section-kicker">ACTIVE ALERTS</span><h2>数据质量告警</h2></div><button className="icon-button" onClick={load}><RefreshCcw size={16} /></button></div><div className="table-scroll"><table><thead><tr><th>级别</th><th>对象</th><th>分类</th><th>问题</th><th>最近发现</th><th>详情</th><th>操作</th></tr></thead><tbody>{issues.length ? issues.map((issue) => <tr key={issue.id}><td><span className={`severity ${issue.severity}`}>{issue.severity === 'critical' ? '严重' : issue.severity === 'warning' ? '警告' : '提示'}</span></td><td>{issue.entity_id}</td><td>{issue.category}</td><td><strong>{issue.title}</strong></td><td>{new Date(issue.last_seen_at).toLocaleString('zh-CN')}</td><td className="issue-detail">{JSON.stringify(issue.detail)}</td><td><button className="text-button" onClick={() => resolve(issue.id)}>标记解决</button></td></tr>) : <tr><td colSpan={7}><div className="empty-inline">当前没有活跃告警</div></td></tr>}</tbody></table></div></section>
  </>
}
