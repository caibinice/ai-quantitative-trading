import { CalendarDays, Search, TrendingUp } from 'lucide-react'
import ReactECharts from 'echarts-for-react'
import { useEffect, useMemo, useState } from 'react'
import { api, formatNumber } from '../api'
import { PageHeader } from '../components/PageHeader'
import { ErrorPanel, Loading } from '../components/StatePanel'
import { chartPalette, useTheme } from '../theme-context'
import type { FinancialMetric, PriceBar, Stock } from '../types'

export function Market() {
  const { theme } = useTheme()
  const chart = chartPalette(theme)
  const [stocks, setStocks] = useState<Stock[]>([])
  const [symbol, setSymbol] = useState('')
  const [prices, setPrices] = useState<PriceBar[]>([])
  const [financials, setFinancials] = useState<FinancialMetric[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api<Stock[]>('/stocks').then((items) => {
      setStocks(items)
      setSymbol(items[0]?.symbol ?? '')
      if (!items.length) setLoading(false)
    }).catch((err: Error) => { setError(err.message); setLoading(false) })
  }, [])

  useEffect(() => {
    if (!symbol) return
    setLoading(true)
    Promise.all([
      api<PriceBar[]>(`/market/${symbol}/prices`),
      api<FinancialMetric[]>(`/market/${symbol}/financials`),
    ]).then(([priceRows, metricRows]) => {
      setPrices(priceRows)
      setFinancials(metricRows)
      setLoading(false)
    }).catch((err: Error) => { setError(err.message); setLoading(false) })
  }, [symbol])

  const selected = stocks.find((item) => item.symbol === symbol)
  const latest = prices.at(-1)
  const previous = prices.at(-2)
  const change = latest && previous ? latest.close / previous.close - 1 : 0
  const latestReport = financials[0]?.report_date
  const latestMetrics = financials.filter((item) => item.report_date === latestReport).slice(0, 12)

  const chartOption = useMemo(() => ({
    animation: false,
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    axisPointer: { link: [{ xAxisIndex: 'all' }] },
    grid: [{ left: 54, right: 18, top: 24, height: '58%' }, { left: 54, right: 18, top: '73%', height: '15%' }],
    xAxis: [
      { type: 'category', data: prices.map((row) => row.date), boundaryGap: true, axisLine: { lineStyle: { color: chart.line } }, axisLabel: { color: chart.muted, show: false } },
      { type: 'category', gridIndex: 1, data: prices.map((row) => row.date), boundaryGap: true, axisLine: { lineStyle: { color: chart.line } }, axisLabel: { color: chart.muted } },
    ],
    yAxis: [
      { scale: true, splitLine: { lineStyle: { color: chart.split } }, axisLabel: { color: chart.muted } },
      { scale: true, gridIndex: 1, splitNumber: 2, splitLine: { show: false }, axisLabel: { color: chart.muted } },
    ],
    dataZoom: [{ type: 'inside', xAxisIndex: [0, 1], start: Math.max(0, 100 - 12000 / Math.max(1, prices.length)), end: 100 }],
    series: [
      {
        name: '日 K', type: 'candlestick',
        data: prices.map((row) => [row.open, row.close, row.low, row.high]),
        itemStyle: { color: '#ff5b6e', color0: '#26d6a0', borderColor: '#ff5b6e', borderColor0: '#26d6a0' },
      },
      {
        name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1,
        data: prices.map((row) => ({ value: row.volume, itemStyle: { color: row.close >= row.open ? '#ff5b6e88' : '#26d6a088' } })),
      },
    ],
  }), [prices, chart.line, chart.muted, chart.split])

  if (error) return <ErrorPanel message={error} />

  return (
    <>
      <PageHeader eyebrow="Market & fundamentals" title="行情与财务显微镜" description="日线采用前复权价格；财务数据按报告期保留，便于核对来源与变化。" />
      <section className="market-toolbar panel">
        <label className="select-wrap"><Search size={17} /><select value={symbol} onChange={(event) => setSymbol(event.target.value)}>
          {stocks.map((stock) => <option value={stock.symbol} key={stock.symbol}>{stock.symbol} · {stock.name}</option>)}
        </select></label>
        {selected && <div className="symbol-title"><strong>{selected.name}</strong><span>{selected.symbol} · {selected.market} 股</span></div>}
        {latest && <div className="quote"><strong>{latest.close.toFixed(2)}</strong><span className={change >= 0 ? 'up' : 'down'}>{change >= 0 ? '+' : ''}{(change * 100).toFixed(2)}%</span></div>}
        <div className="data-tag"><CalendarDays size={15} />更新至 {latest?.date ?? '—'}</div>
      </section>
      {loading ? <Loading /> : !prices.length ? (
        <div className="empty-block tall"><TrendingUp /><strong>暂无行情数据</strong><span>到“策略实验室”同步 AKShare 数据或运行演示数据脚本。</span></div>
      ) : (
        <section className="market-grid">
          <article className="panel price-panel"><div className="panel-head"><div><span className="section-kicker">PRICE ACTION</span><h2>历史行情</h2></div><span className="source-chip">AKShare · 前复权</span></div><ReactECharts key={theme} option={chartOption} style={{ height: 460 }} /></article>
          <aside className="panel quote-panel">
            <div className="panel-head"><div><span className="section-kicker">SNAPSHOT</span><h2>当日切片</h2></div></div>
            <div className="quote-grid">
              {[['开盘', latest?.open], ['最高', latest?.high], ['最低', latest?.low], ['收盘', latest?.close], ['成交量', latest?.volume], ['换手率', latest?.turnover_rate]].map(([label, value]) => (
                <div key={String(label)}><span>{label}</span><strong>{formatNumber(value as number, label === '成交量' ? 0 : 2)}</strong></div>
              ))}
            </div>
            <p className="small-note">前复权用于保持价格序列连续。网页数据存在延迟或源站调整风险，重要研究请交叉验证。</p>
          </aside>
        </section>
      )}
      <section className="panel financial-panel">
        <div className="panel-head"><div><span className="section-kicker">FUNDAMENTALS</span><h2>最新财务指标</h2></div><span className="source-chip">报告期 {latestReport ?? '—'}</span></div>
        {latestMetrics.length ? <div className="metric-grid">{latestMetrics.map((metric) => (
          <div className="metric-item" key={metric.metric_name}><span>{metric.metric_name}</span><strong>{formatNumber(metric.metric_value)}</strong><small className={(metric.yoy ?? 0) >= 0 ? 'up' : 'down'}>{metric.yoy === null ? '同比 —' : `同比 ${metric.yoy > 0 ? '+' : ''}${metric.yoy.toFixed(2)}%`}</small></div>
        ))}</div> : <div className="empty-inline">暂无财务数据</div>}
      </section>
    </>
  )
}
