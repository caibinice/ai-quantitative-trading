import { Brain, Database, ExternalLink, Filter, RefreshCcw, ShieldAlert } from 'lucide-react'
import ReactECharts from 'echarts-for-react'
import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { PageHeader } from '../components/PageHeader'
import { formatBeijingDate, formatBeijingTime } from '../dateTime'
import { ErrorPanel, Loading } from '../components/StatePanel'
import { chartPalette, useTheme } from '../theme-context'
import type { NewsItem, SentimentSource, Stock } from '../types'

export function Sentiment() {
  const { theme } = useTheme()
  const chart = chartPalette(theme)
  const [items, setItems] = useState<NewsItem[]>([])
  const [stocks, setStocks] = useState<Stock[]>([])
  const [sources, setSources] = useState<SentimentSource[]>([])
  const [symbol, setSymbol] = useState('')
  const [kind, setKind] = useState('')
  const [label, setLabel] = useState('')
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    const query = new URLSearchParams({ ...(symbol && { symbol }), ...(kind && { kind }), ...(label && { label }) })
    Promise.all([
      api<NewsItem[]>(`/sentiment/news?${query}`),
      api<Stock[]>('/stocks'),
      api<SentimentSource[]>('/sentiment/sources'),
    ])
      .then(([news, stockRows, sourceRows]) => {
        setItems(news); setStocks(stockRows); setSources(sourceRows); setLoading(false)
      })
      .catch((err: Error) => { setError(err.message); setLoading(false) })
  }
  useEffect(load, [symbol, kind, label])

  const analyze = async () => {
    setAnalyzing(true); setError('')
    try { await api('/pipeline/analyze', { method: 'POST', body: JSON.stringify({ limit: 100 }) }); load() }
    catch (err) { setError((err as Error).message) }
    finally { setAnalyzing(false) }
  }

  const counts = useMemo(() => items.reduce<Record<string, number>>((result, item) => {
    result[item.label] = (result[item.label] ?? 0) + 1
    return result
  }, {}), [items])
  const analyzed = items.filter((item) => item.score !== null)
  const average = analyzed.length ? analyzed.reduce((sum, item) => sum + (item.score ?? 0), 0) / analyzed.length : 0
  const gaugeOption = {
    series: [{ type: 'gauge', startAngle: 210, endAngle: -30, min: -1, max: 1, splitNumber: 4, radius: '95%', center: ['50%', '58%'], progress: { show: true, width: 12, itemStyle: { color: average >= 0 ? '#32d6a0' : '#ff6b78' } }, axisLine: { lineStyle: { width: 12, color: [[1, chart.track]] } }, axisTick: { show: false }, splitLine: { show: false }, axisLabel: { color: chart.muted, distance: -38, fontSize: 10 }, pointer: { show: false }, detail: { valueAnimation: true, offsetCenter: [0, '10%'], formatter: (value: number) => value.toFixed(2), color: chart.strong, fontSize: 30, fontWeight: 700 }, title: { offsetCenter: [0, '42%'], color: chart.muted, fontSize: 12 }, data: [{ value: average, name: '平均情绪分' }] }],
  }

  if (error && !items.length) return <ErrorPanel message={error} />

  return (
    <>
      <PageHeader eyebrow="Sentiment intelligence" title="舆情与公告事件雷达" description="定时采集公开新闻和公告，再由大模型输出结构化利好/中性/利空、置信度与理由。" actions={<button className="button primary" onClick={analyze} disabled={analyzing}><Brain size={17} />{analyzing ? 'AI 分析中…' : '分析待处理事件'}</button>} />
      {error && <div className="inline-alert">{error}</div>}
      <section className="panel sentiment-source-panel">
        <div className="panel-head">
          <div><span className="section-kicker">SOURCE CATALOG</span><h2>舆情与公告数据源</h2></div>
          <span>当前启用 {sources.filter((source) => source.status === 'active').length} 个</span>
        </div>
        <p>新闻用于发现事件，法定公告用于核对事实。公开接口可能限流或改版，重要结论应点击原文交叉验证。</p>
        <div className="sentiment-source-grid">
          {sources.map((source) => (
            <article key={source.id}>
              <Database size={17} />
              <div>
                <span>{source.kind} · {source.registration}</span>
                <strong>{source.name}</strong>
                <small>{source.access}</small>
                <p>{source.note}</p>
              </div>
              <i className={source.status}>{source.status === 'active' ? '已接入' : source.status === 'optional' ? '需授权' : '待评估'}</i>
            </article>
          ))}
        </div>
      </section>
      <section className="sentiment-overview">
        <article className="panel sentiment-gauge"><div><span className="section-kicker">MARKET MOOD</span><h2>当前股票池情绪</h2><p>统计基于当前筛选列表，不等同于全市场情绪。</p></div><ReactECharts key={theme} option={gaugeOption} style={{ height: 210, width: 260 }} /></article>
        <article className="panel mood-stats"><div className="mood-cell positive"><span>利好事件</span><strong>{counts['利好'] ?? 0}</strong><small>模型判断偏正向</small></div><div className="mood-cell neutral"><span>中性事件</span><strong>{counts['中性'] ?? 0}</strong><small>影响暂不明确</small></div><div className="mood-cell negative"><span>利空事件</span><strong>{counts['利空'] ?? 0}</strong><small>模型判断偏负向</small></div><div className="mood-cell pending"><span>待分析</span><strong>{counts['待分析'] ?? 0}</strong><small>等待模型流水线</small></div></article>
      </section>
      <section className="panel news-panel">
        <div className="filterbar"><div className="filter-title"><Filter size={17} />筛选事件</div><select value={symbol} onChange={(event) => setSymbol(event.target.value)}><option value="">全部股票</option>{stocks.map((stock) => <option key={stock.symbol} value={stock.symbol}>{stock.symbol} · {stock.name}</option>)}</select><select value={kind} onChange={(event) => setKind(event.target.value)}><option value="">新闻 + 公告</option><option value="news">新闻</option><option value="notice">公告</option></select><select value={label} onChange={(event) => setLabel(event.target.value)}><option value="">全部标签</option><option value="利好">利好</option><option value="中性">中性</option><option value="利空">利空</option><option value="待分析">待分析</option></select><button className="icon-button" onClick={load} aria-label="刷新"><RefreshCcw size={17} /></button></div>
        {!symbol && <div className="dedup-note">全部股票视图已按相同标题合并为一个事件；同一新闻对不同股票仍会独立研判，选择单只股票可查看对应结论。</div>}
        {loading ? <Loading label="载入舆情事件…" /> : items.length ? <div className="news-list">{items.map((item) => {
          const relatedSymbols = item.related_symbols?.length ? item.related_symbols : [item.symbol]
          const symbolText = relatedSymbols.length > 1
            ? `影响 ${relatedSymbols.length} 只：${relatedSymbols.slice(0, 4).join('、')}${relatedSymbols.length > 4 ? '…' : ''}`
            : item.symbol
          return <article className="news-item" key={item.id}>
            <div className="news-time"><strong>{formatBeijingDate(item.published_at)}</strong><span>{formatBeijingTime(item.published_at)} 北京时间</span></div>
            <div className={`sentiment-marker ${labelClass(item.label)}`}><i /></div>
            <div className="news-copy"><div className="news-meta"><span className="symbol-chip related-symbols" title={relatedSymbols.join('、')}>{symbolText}</span><span>{item.kind === 'notice' ? '公司公告' : item.source}</span><span>{item.model || '等待分析'}</span></div><h3>{item.source_url ? <a href={item.source_url} target="_blank" rel="noreferrer">{item.title}<ExternalLink size={13} /></a> : item.title}</h3><p>{item.summary || '尚未生成摘要'}</p>{item.rationale && <div className="ai-rationale"><Brain size={14} />{item.rationale}</div>}</div>
            <div className={`sentiment-result ${labelClass(item.label)}`}><strong>{item.label}</strong><span>{item.score === null ? '—' : `${item.score > 0 ? '+' : ''}${item.score.toFixed(2)}`}</span><small>置信度 {item.confidence === null ? '—' : `${(item.confidence * 100).toFixed(0)}%`}</small></div>
          </article>
        })}</div> : <div className="empty-block"><ShieldAlert /><strong>当前筛选没有事件</strong><span>请同步新闻公告数据，或调整筛选条件。</span></div>}
      </section>
    </>
  )
}

function labelClass(label: string) {
  return label === '利好' ? 'positive' : label === '利空' ? 'negative' : label === '待分析' ? 'pending' : 'neutral'
}
