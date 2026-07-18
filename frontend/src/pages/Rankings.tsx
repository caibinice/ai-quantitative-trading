import { Bot, Info, RefreshCcw } from 'lucide-react'
import ReactECharts from 'echarts-for-react'
import { useEffect, useState } from 'react'
import { api } from '../api'
import { PageHeader } from '../components/PageHeader'
import { ErrorPanel, Loading } from '../components/StatePanel'
import { chartPalette, useTheme } from '../theme-context'
import type { RankingItem } from '../types'

export function Rankings() {
  const { theme } = useTheme()
  const chart = chartPalette(theme)
  const [items, setItems] = useState<RankingItem[]>([])
  const [scoreDate, setScoreDate] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    api<{ score_date: string | null; items: RankingItem[] }>('/rankings').then((data) => {
      setItems(data.items); setScoreDate(data.score_date); setLoading(false)
    }).catch((err: Error) => { setError(err.message); setLoading(false) })
  }
  useEffect(load, [])

  const recompute = async () => {
    setRunning(true); setError('')
    try { await api('/rankings/recompute', { method: 'POST', body: JSON.stringify({}) }); load() }
    catch (err) { setError((err as Error).message) }
    finally { setRunning(false) }
  }

  const chartOption = {
    grid: { left: 90, right: 30, top: 10, bottom: 30 },
    xAxis: { type: 'value', min: 0, max: 100, splitLine: { lineStyle: { color: chart.split } }, axisLabel: { color: chart.muted } },
    yAxis: { type: 'category', inverse: true, data: items.slice(0, 8).map((item) => item.name), axisLine: { show: false }, axisLabel: { color: chart.text } },
    tooltip: { trigger: 'axis' },
    series: [{ type: 'bar', data: items.slice(0, 8).map((item) => item.total_score), barWidth: 10, itemStyle: { color: '#37c6e7', borderRadius: 8 }, showBackground: true, backgroundStyle: { color: chart.track, borderRadius: 8 } }],
  }

  if (error && !items.length) return <ErrorPanel message={error} />
  if (loading && !items.length) return <Loading />

  return (
    <>
      <PageHeader eyebrow="AI factor ranking" title="可解释的 AI 选股排名" description="不是让模型猜股价，而是把动量、财务质量和已发布舆情转换为可检查的分项评分。" actions={<button className="button primary" onClick={recompute} disabled={running}><RefreshCcw size={16} className={running ? 'spin' : ''} />{running ? '计算中' : '重新评分'}</button>} />
      {error && <div className="inline-alert">{error}</div>}
      <div className="info-banner"><Info size={18} /><span>评分日：{scoreDate ?? '尚未生成'}。总分仅用于研究排序，不能直接解释为预期收益或买入概率。</span></div>
      <section className="ranking-layout">
        <article className="panel ranking-chart"><div className="panel-head"><div><span className="section-kicker">TOP SIGNALS</span><h2>综合得分</h2></div></div>{items.length ? <ReactECharts key={theme} option={chartOption} style={{ height: 330 }} /> : <div className="empty-inline">暂无评分</div>}</article>
        <article className="panel score-method"><Bot size={25} /><span className="section-kicker">SCORING MODEL</span><h2>三类证据，一个结论</h2><p>动量衡量价格趋势并扣除波动惩罚；质量来自最新可得财务指标；情绪按置信度与时间衰减聚合。</p><div className="method-weights"><span><i style={{ width: '55%' }} />行情 55%</span><span><i style={{ width: '15%' }} />财务 15%</span><span><i style={{ width: '30%' }} />舆情 30%</span></div></article>
      </section>
      <section className="panel table-panel">
        <div className="panel-head"><div><span className="section-kicker">FULL RANKING</span><h2>股票池评分明细</h2></div><span>{items.length} 个标的</span></div>
        <div className="table-scroll"><table><thead><tr><th>排名</th><th>股票</th><th>行情动量</th><th>财务质量</th><th>舆情情绪</th><th>综合分</th><th>信号状态</th></tr></thead><tbody>{items.map((item) => (
          <tr key={item.symbol}><td><span className={`table-rank rank-${item.rank}`}>{String(item.rank).padStart(2, '0')}</span></td><td><div className="stock-name"><strong>{item.name}</strong><span>{item.symbol}</span></div></td><td><Score value={item.momentum_score} /></td><td><Score value={item.quality_score} /></td><td><Score value={item.sentiment_score} /></td><td><strong className="total-score">{item.total_score.toFixed(1)}</strong></td><td><span className={`signal-tag ${item.total_score >= 60 ? 'positive' : item.total_score < 45 ? 'negative' : 'neutral'}`}>{item.total_score >= 60 ? '关注' : item.total_score < 45 ? '偏弱' : '观察'}</span></td></tr>
        ))}</tbody></table></div>
      </section>
    </>
  )
}

function Score({ value }: { value: number }) {
  return <div className="cell-score"><span>{value.toFixed(1)}</span><i><b style={{ width: `${value}%` }} /></i></div>
}
