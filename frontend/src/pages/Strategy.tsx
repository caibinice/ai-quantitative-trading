import { Brain, DatabaseZap, FlaskConical, Play, Save, Sparkles } from 'lucide-react'
import ReactECharts from 'echarts-for-react'
import { useEffect, useMemo, useState } from 'react'
import { api, formatNumber, formatPercent } from '../api'
import { PageHeader } from '../components/PageHeader'
import { ErrorPanel, Loading } from '../components/StatePanel'
import type { BacktestResult, StrategyConfig, StrategyParameters } from '../types'

type Action = 'save' | 'sync' | 'analyze' | 'score' | 'backtest' | ''

export function Strategy() {
  const [config, setConfig] = useState<StrategyConfig | null>(null)
  const [watchlistText, setWatchlistText] = useState('')
  const [startDate, setStartDate] = useState(() => yearAgo())
  const [endDate, setEndDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [result, setResult] = useState<BacktestResult | null>(null)
  const [activeAction, setActiveAction] = useState<Action>('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api<StrategyConfig>('/strategy').then((data) => { setConfig(data); setWatchlistText(data.watchlist.join(', ')) }).catch((err: Error) => setError(err.message))
  }, [])

  const execute = async (action: Action) => {
    if (!config) return
    setActiveAction(action); setError(''); setMessage('')
    const watchlist = watchlistText.split(/[,，\s]+/).map((item) => item.trim()).filter(Boolean)
    try {
      if (action === 'save') {
        const saved = await api<StrategyConfig>('/strategy', { method: 'PUT', body: JSON.stringify({ ...config, watchlist }) })
        setConfig(saved); setMessage('策略配置已保存。')
      } else if (action === 'sync') {
        const response = await api<Record<string, number>>('/pipeline/sync', { method: 'POST', body: JSON.stringify({ symbols: watchlist, start_date: startDate, end_date: endDate }) })
        setMessage(`数据同步完成：行情 ${response.prices ?? 0} 条，新闻 ${response.news ?? 0} 条。`)
      } else if (action === 'analyze') {
        const response = await api<{ analyzed: number }>('/pipeline/analyze', { method: 'POST', body: JSON.stringify({ limit: 200 }) })
        setMessage(`情绪分析完成：处理 ${response.analyzed} 条事件。`)
      } else if (action === 'score') {
        const response = await api<{ count: number }>('/rankings/recompute', { method: 'POST', body: JSON.stringify({ symbols: watchlist }) })
        setMessage(`因子评分完成：生成 ${response.count} 个标的评分。`)
      } else if (action === 'backtest') {
        const response = await api<BacktestResult>('/backtests', { method: 'POST', body: JSON.stringify({ name: config.name, symbols: watchlist, start_date: startDate, end_date: endDate, parameters: config.parameters }) })
        setResult(response); setMessage('回测完成。信号已强制延迟一个交易日执行。')
      }
    } catch (err) { setError((err as Error).message) }
    finally { setActiveAction('') }
  }

  const updateParameter = (key: keyof StrategyParameters, value: number) => {
    if (!config) return
    setConfig({ ...config, parameters: { ...config.parameters, [key]: value } })
  }
  const weightTotal = config ? config.parameters.momentum_weight + config.parameters.quality_weight + config.parameters.sentiment_weight : 0
  const chartOption = useMemo(() => ({
    tooltip: { trigger: 'axis' },
    legend: { data: ['双因子策略', '等权基准'], textStyle: { color: '#8fa2b7' }, top: 0 },
    grid: { left: 60, right: 24, top: 48, bottom: 40 },
    xAxis: { type: 'category', boundaryGap: false, data: result?.equity_curve.map((row) => row.date) ?? [], axisLabel: { color: '#718096' }, axisLine: { lineStyle: { color: '#2a3b50' } } },
    yAxis: { type: 'value', scale: true, axisLabel: { color: '#718096' }, splitLine: { lineStyle: { color: '#1a2a3c' } } },
    dataZoom: [{ type: 'inside' }],
    series: [{ name: '双因子策略', type: 'line', showSymbol: false, smooth: 0.2, data: result?.equity_curve.map((row) => row.equity) ?? [], lineStyle: { width: 2, color: '#37c6e7' }, areaStyle: { color: '#37c6e718' } }, { name: '等权基准', type: 'line', showSymbol: false, data: result?.equity_curve.map((row) => row.benchmark) ?? [], lineStyle: { width: 1.5, color: '#77869c', type: 'dashed' } }],
  }), [result])

  if (error && !config) return <ErrorPanel message={error} />
  if (!config) return <Loading />

  const p = config.parameters
  return (
    <>
      <PageHeader eyebrow="Strategy laboratory" title="把研究假设变成可配置实验" description="调整因子、成本和股票池；每次回测都保存参数与资金曲线，避免“只记住最好结果”。" actions={<button className="button primary" onClick={() => execute('save')} disabled={!!activeAction}><Save size={16} />{activeAction === 'save' ? '保存中' : '保存配置'}</button>} />
      {(error || message) && <div className={`inline-alert ${error ? '' : 'success'}`}>{error || message}</div>}
      <section className="strategy-layout">
        <div className="strategy-column">
          <article className="panel config-panel">
            <div className="panel-head"><div><span className="section-kicker">UNIVERSE</span><h2>股票池与样本期</h2></div><DatabaseZap size={21} /></div>
            <label className="field"><span>股票代码（逗号分隔）</span><textarea value={watchlistText} onChange={(event) => setWatchlistText(event.target.value)} rows={3} /></label>
            <div className="field-row"><label className="field"><span>回测开始</span><input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} /></label><label className="field"><span>回测结束</span><input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} /></label></div>
          </article>
          <article className="panel config-panel">
            <div className="panel-head"><div><span className="section-kicker">FACTOR MIX</span><h2>因子权重</h2></div><span className={`weight-total ${Math.abs(weightTotal - 1) < 0.001 ? 'valid' : 'invalid'}`}>合计 {(weightTotal * 100).toFixed(0)}%</span></div>
            <RangeField label="行情动量" value={p.momentum_weight} min={0} max={1} step={0.05} onChange={(value) => updateParameter('momentum_weight', value)} color="cyan" />
            <RangeField label="财务质量" value={p.quality_weight} min={0} max={1} step={0.05} onChange={(value) => updateParameter('quality_weight', value)} color="violet" />
            <RangeField label="舆情情绪" value={p.sentiment_weight} min={0} max={1} step={0.05} onChange={(value) => updateParameter('sentiment_weight', value)} color="green" />
            <p className="small-note">排名使用三因子；历史回测为避免财务披露时点泄漏，仅将行情与舆情权重重新归一化后使用。</p>
          </article>
          <article className="panel config-panel">
            <div className="panel-head"><div><span className="section-kicker">EXECUTION</span><h2>信号与成本</h2></div><FlaskConical size={21} /></div>
            <div className="compact-grid"><NumberField label="动量窗口（交易日）" value={p.momentum_window} step={1} onChange={(value) => updateParameter('momentum_window', value)} /><NumberField label="舆情回看（日）" value={p.sentiment_lookback_days} step={1} onChange={(value) => updateParameter('sentiment_lookback_days', value)} /><NumberField label="持仓数量" value={p.top_n} step={1} onChange={(value) => updateParameter('top_n', value)} /><NumberField label="舆情门槛" value={p.sentiment_threshold} step={0.05} onChange={(value) => updateParameter('sentiment_threshold', value)} /><NumberField label="手续费率" value={p.fee_rate} step={0.0001} onChange={(value) => updateParameter('fee_rate', value)} /><NumberField label="滑点率" value={p.slippage_rate} step={0.0001} onChange={(value) => updateParameter('slippage_rate', value)} /></div>
          </article>
        </div>
        <aside className="strategy-column">
          <article className="panel workflow-panel"><div className="panel-head"><div><span className="section-kicker">RESEARCH PIPELINE</span><h2>分步运行</h2></div><Sparkles size={21} /></div><p>真实采集可能受源站限流影响。建议先同步少量股票，再逐步扩大股票池。</p><div className="workflow-actions"><ActionButton icon={<DatabaseZap />} label="1. 同步 AKShare 数据" detail="日线、财务、新闻与公告" active={activeAction === 'sync'} disabled={!!activeAction} onClick={() => execute('sync')} /><ActionButton icon={<Brain />} label="2. 大模型情绪分析" detail="结构化标签、分数和理由" active={activeAction === 'analyze'} disabled={!!activeAction} onClick={() => execute('analyze')} /><ActionButton icon={<Sparkles />} label="3. 生成 AI 评分" detail="动量 + 质量 + 情绪" active={activeAction === 'score'} disabled={!!activeAction} onClick={() => execute('score')} /><ActionButton icon={<Play />} label="4. 运行历史回测" detail="延迟信号 + 手续费 + 滑点" active={activeAction === 'backtest'} disabled={!!activeAction} onClick={() => execute('backtest')} accent /></div></article>
          <article className="panel guardrail-panel"><span>研究护栏</span><ul><li>信号在下一交易日才生效</li><li>新闻只在发布时间之后进入因子</li><li>回测扣除双边换仓成本</li><li>系统不包含券商与真实下单接口</li></ul></article>
        </aside>
      </section>
      {result && <section className="panel result-panel"><div className="panel-head"><div><span className="section-kicker">BACKTEST RESULT #{result.id}</span><h2>策略资金曲线</h2></div><span className="source-chip">{result.start_date} → {result.end_date}</span></div><div className="result-metrics">{[['累计收益', formatPercent(result.metrics.total_return)], ['年化收益', formatPercent(result.metrics.annualized_return)], ['最大回撤', formatPercent(result.metrics.max_drawdown)], ['夏普比率', formatNumber(result.metrics.sharpe_ratio)], ['换手率', formatNumber(result.metrics.turnover)], ['交易日', formatNumber(result.metrics.bars, 0)]].map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div><ReactECharts option={chartOption} style={{ height: 390 }} /></section>}
    </>
  )
}

function RangeField({ label, value, min, max, step, onChange, color }: { label: string; value: number; min: number; max: number; step: number; onChange: (value: number) => void; color: string }) {
  return <label className={`range-field ${color}`}><span><strong>{label}</strong><b>{(value * 100).toFixed(0)}%</b></span><input type="range" value={value} min={min} max={max} step={step} onChange={(event) => onChange(Number(event.target.value))} style={{ '--range-progress': `${value * 100}%` } as React.CSSProperties} /></label>
}

function NumberField({ label, value, step, onChange }: { label: string; value: number; step: number; onChange: (value: number) => void }) {
  return <label className="field"><span>{label}</span><input type="number" value={value} step={step} onChange={(event) => onChange(Number(event.target.value))} /></label>
}

function ActionButton({ icon, label, detail, active, disabled, onClick, accent = false }: { icon: React.ReactNode; label: string; detail: string; active: boolean; disabled: boolean; onClick: () => void; accent?: boolean }) {
  return <button className={`workflow-button ${accent ? 'accent' : ''}`} onClick={onClick} disabled={disabled}><span className={active ? 'spin' : ''}>{icon}</span><div><strong>{active ? '正在执行…' : label}</strong><small>{detail}</small></div></button>
}

function yearAgo() {
  const value = new Date(); value.setFullYear(value.getFullYear() - 1); return value.toISOString().slice(0, 10)
}
