import { Beaker, CalendarRange, Play, RefreshCcw } from 'lucide-react'
import ReactECharts from 'echarts-for-react'
import { useEffect, useMemo, useState } from 'react'
import { api, formatNumber, formatPercent } from '../api'
import { PageHeader } from '../components/PageHeader'
import { ErrorPanel, Loading } from '../components/StatePanel'
import { beijingDateInput } from '../dateTime'
import { chartPalette, useTheme } from '../theme-context'
import type { ResearchTask, StrategyConfig, WalkForwardRun } from '../types'
import { localize, tr } from '../i18n'

export function WalkForward() {
  const { theme } = useTheme()
  const chart = chartPalette(theme)
  const [strategy, setStrategy] = useState<StrategyConfig | null>(null)
  const [runs, setRuns] = useState<WalkForwardRun[]>([])
  const [selected, setSelected] = useState<WalkForwardRun | null>(null)
  const [startDate, setStartDate] = useState(() => dateOffset(-450))
  const [endDate, setEndDate] = useState(() => dateOffset(0))
  const [trainDays, setTrainDays] = useState(126)
  const [testDays, setTestDays] = useState(42)
  const [momentumGrid, setMomentumGrid] = useState('10, 20, 40')
  const [sentimentGrid, setSentimentGrid] = useState('-0.2, 0, 0.2')
  const [task, setTask] = useState<ResearchTask | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadRuns = async () => {
    const rows = await api<WalkForwardRun[]>('/walk-forward')
    setRuns(rows)
    if (rows[0] && !selected) {
      const detail = await api<WalkForwardRun>(`/walk-forward/${rows[0].id}`)
      setSelected(detail)
    }
  }

  useEffect(() => {
    Promise.all([api<StrategyConfig>('/strategy'), api<WalkForwardRun[]>('/walk-forward')]).then(async ([config, rows]) => {
      setStrategy(config); setRuns(rows)
      if (rows[0]) setSelected(await api<WalkForwardRun>(`/walk-forward/${rows[0].id}`))
      setLoading(false)
    }).catch((err: Error) => { setError(err.message); setLoading(false) })
  }, [])

  useEffect(() => {
    if (!task || !['queued', 'running'].includes(task.status)) return
    const timer = window.setInterval(async () => {
      const fresh = await api<ResearchTask>(`/tasks/${task.id}`)
      setTask(fresh)
      if (fresh.status === 'success') {
        window.clearInterval(timer)
        const runId = Number(fresh.result.run_id)
        if (runId) setSelected(await api<WalkForwardRun>(`/walk-forward/${runId}`))
        await loadRuns()
      } else if (fresh.status === 'failed') {
        window.clearInterval(timer); setError(fresh.error)
      }
    }, 1500)
    return () => window.clearInterval(timer)
  }, [task?.id, task?.status])

  const run = async () => {
    if (!strategy) return
    setError('')
    try {
      const response = await api<{ task_id: number }>('/walk-forward', { method: 'POST', body: JSON.stringify({ name: tr('Walk-forward 样本外验证'), symbols: strategy.watchlist, start_date: startDate, end_date: endDate, train_days: trainDays, test_days: testDays, momentum_windows: parseNumbers(momentumGrid), sentiment_thresholds: parseNumbers(sentimentGrid), parameters: strategy.parameters }) })
      setTask(await api<ResearchTask>(`/tasks/${response.task_id}`))
    } catch (err) { setError((err as Error).message) }
  }

  const openRun = async (id: number) => setSelected(await api<WalkForwardRun>(`/walk-forward/${id}`))
  const chartOption = useMemo(() => ({ tooltip: { trigger: 'axis' }, legend: { data: [tr('样本外策略'), tr('指数基准')], textStyle: { color: chart.text } }, grid: { left: 62, right: 24, top: 45, bottom: 42 }, xAxis: { type: 'category', boundaryGap: false, data: selected?.equity_curve?.map((row) => row.date) ?? [], axisLabel: { color: chart.muted }, axisLine: { lineStyle: { color: chart.line } } }, yAxis: { type: 'value', scale: true, axisLabel: { color: chart.muted }, splitLine: { lineStyle: { color: chart.split } } }, dataZoom: [{ type: 'inside' }], series: [{ name: tr('样本外策略'), type: 'line', showSymbol: false, data: selected?.equity_curve?.map((row) => row.equity) ?? [], lineStyle: { color: '#37c6e7', width: 2 }, areaStyle: { color: '#37c6e715' } }, { name: tr('指数基准'), type: 'line', showSymbol: false, data: selected?.equity_curve?.map((row) => row.benchmark) ?? [], lineStyle: { color: '#a989ff', type: 'dashed' } }] }), [selected, chart.line, chart.muted, chart.split, chart.text])

  if (error && !strategy) return <ErrorPanel message={error} />
  if (loading || !strategy) return <Loading label={tr("载入样本外实验…")} />
  const busy = task && ['queued', 'running'].includes(task.status)

  return <>
    <PageHeader eyebrow="Walk-forward validation" title={tr("滚动样本外验证")} description={tr("每个窗口只在过去训练区间选择参数，再把固定参数应用到下一段未见数据；最终曲线只拼接样本外收益。")} actions={<button className="button primary" onClick={run} disabled={!!busy}>{busy ? <RefreshCcw className="spin" size={16} /> : <Play size={16} />}{busy ? localize({ 'zh-CN': `任务 #${task.id} ${(task.progress * 100).toFixed(0)}%`, en: `Task #${task.id} ${(task.progress * 100).toFixed(0)}%`, ja: `タスク #${task.id} ${(task.progress * 100).toFixed(0)}%` }) : tr('开始样本外实验')}</button>} />
    {error && <div className="inline-alert">{error}</div>}
    <section className="wf-layout"><article className="panel wf-config"><div className="panel-head"><div><span className="section-kicker">ROLLING WINDOWS</span><h2>{tr("实验设置")}</h2></div><CalendarRange size={20} /></div><div className="field-row"><label className="field"><span>{tr("开始日期")}</span><input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} /></label><label className="field"><span>{tr("结束日期")}</span><input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} /></label></div><div className="field-row"><label className="field"><span>{tr("训练窗口（交易日）")}</span><input type="number" value={trainDays} min={60} onChange={(event) => setTrainDays(Number(event.target.value))} /></label><label className="field"><span>{tr("测试窗口（交易日）")}</span><input type="number" value={testDays} min={20} onChange={(event) => setTestDays(Number(event.target.value))} /></label></div><label className="field"><span>{tr("候选动量窗口")}</span><input value={momentumGrid} onChange={(event) => setMomentumGrid(event.target.value)} /></label><label className="field"><span>{tr("候选舆情门槛")}</span><input value={sentimentGrid} onChange={(event) => setSentimentGrid(event.target.value)} /></label><div className="wf-rule"><Beaker size={17} /><span>{tr("参数优选目标 = 训练期夏普 + 年化收益 − 0.25 × 最大回撤；测试期不会参与参数选择。")}</span></div></article><aside className="panel run-history"><div className="panel-head"><div><span className="section-kicker">EXPERIMENTS</span><h2>{tr("历史实验")}</h2></div><span>{runs.length} {tr("次")}</span></div><div className="run-list">{runs.length ? runs.map((item) => <button className={selected?.id === item.id ? 'active' : ''} key={item.id} onClick={() => openRun(item.id)}><span>#{item.id}</span><div><strong>{tr(item.name)}</strong><small>{item.start_date} → {item.end_date}</small></div><b>{formatPercent(item.metrics.total_return)}</b></button>) : <div className="empty-inline">{tr("尚未运行样本外实验")}</div>}</div></aside></section>
    {selected && <><section className="panel wf-result"><div className="panel-head"><div><span className="section-kicker">OUT-OF-SAMPLE ONLY</span><h2>{tr("样本外资金曲线")}</h2></div><span className="source-chip">{tr("基准")} {selected.benchmark_symbol}</span></div><div className="result-metrics">{[['样本外收益', formatPercent(selected.metrics.total_return)], ['年化收益', formatPercent(selected.metrics.annualized_return)], ['最大回撤', formatPercent(selected.metrics.max_drawdown)], ['夏普比率', formatNumber(selected.metrics.sharpe_ratio)], ['基准收益', formatPercent(selected.metrics.benchmark_return)], ['滚动窗口', String(selected.windows.length)]].map(([label, value]) => <div key={label}><span>{tr(label)}</span><strong>{value}</strong></div>)}</div><ReactECharts key={theme} option={chartOption} style={{ height: 380 }} /></section><section className="panel table-panel wf-windows"><div className="panel-head"><div><span className="section-kicker">WINDOW AUDIT</span><h2>{tr("每个窗口的参数选择")}</h2></div></div><div className="table-scroll"><table><thead><tr><th>{tr("训练区间")}</th><th>{tr("样本外区间")}</th><th>{tr("动量窗口")}</th><th>{tr("情绪门槛")}</th><th>{tr("训练夏普")}</th><th>{tr("测试收益")}</th><th>{tr("测试回撤")}</th></tr></thead><tbody>{selected.windows.map((window) => <tr key={window.test_start}><td>{window.train_start} → {window.train_end}</td><td>{window.test_start} → {window.test_end}</td><td>{window.selected_momentum_window} {tr("日")}</td><td>{window.selected_sentiment_threshold.toFixed(2)}</td><td>{formatNumber(window.train_metrics.sharpe_ratio)}</td><td>{formatPercent(window.test_metrics.total_return)}</td><td>{formatPercent(window.test_metrics.max_drawdown)}</td></tr>)}</tbody></table></div></section></>}
  </>
}

function parseNumbers(value: string) { return value.split(/[,，\s]+/).map(Number).filter((item) => Number.isFinite(item)) }
function dateOffset(days: number) { return beijingDateInput(days) }
