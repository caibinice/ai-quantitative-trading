import { ArrowUpRight, Database, FileSearch, LineChart, Newspaper, Sparkles } from 'lucide-react'
import ReactECharts from 'echarts-for-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, formatNumber } from '../api'
import { PageHeader } from '../components/PageHeader'
import { ErrorPanel, Loading } from '../components/StatePanel'

interface Summary {
  counts: { stocks: number; price_rows: number; news: number; analyzed: number }
  latest_score_date: string | null
  top_scores: Array<{
    symbol: string
    name: string
    total_score: number
    sentiment_score: number
  }>
  sentiment_stats: Record<string, number>
  latest_job: null | {
    job_type: string
    status: string
    message: string
    started_at: string
  }
}

export function Dashboard() {
  const [data, setData] = useState<Summary | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api<Summary>('/dashboard/summary').then(setData).catch((err: Error) => setError(err.message))
  }, [])

  if (error) return <ErrorPanel message={error} />
  if (!data) return <Loading />

  const sentimentOption = {
    tooltip: { trigger: 'item' },
    color: ['#32d6a0', '#77869c', '#ff6b78'],
    series: [{
      type: 'pie',
      radius: ['64%', '84%'],
      center: ['50%', '52%'],
      label: { show: false },
      data: [
        { name: '利好', value: data.sentiment_stats['利好'] ?? 0 },
        { name: '中性', value: data.sentiment_stats['中性'] ?? 0 },
        { name: '利空', value: data.sentiment_stats['利空'] ?? 0 },
      ],
    }],
    graphic: [{
      type: 'text',
      left: 'center',
      top: '43%',
      style: {
        text: `${data.counts.analyzed}\n已分析`,
        textAlign: 'center',
        fill: '#eaf3ff',
        fontSize: 18,
        lineHeight: 25,
        fontWeight: 700,
      },
    }],
  }

  const stats = [
    { label: '股票池', value: data.counts.stocks, suffix: '只', icon: Database, tone: 'cyan' },
    { label: '日线记录', value: data.counts.price_rows, suffix: '条', icon: LineChart, tone: 'violet' },
    { label: '新闻与公告', value: data.counts.news, suffix: '条', icon: Newspaper, tone: 'amber' },
    { label: 'AI 已分析', value: data.counts.analyzed, suffix: '条', icon: Sparkles, tone: 'green' },
  ]

  return (
    <>
      <PageHeader
        eyebrow="Research overview"
        title="今天，从数据而不是感觉出发"
        description="把行情、财务、舆情和回测汇总到一个可追溯的研究工作台。"
        actions={<Link className="button primary" to="/strategy">开始一次策略实验 <ArrowUpRight size={16} /></Link>}
      />

      <section className="stat-grid">
        {stats.map(({ label, value, suffix, icon: Icon, tone }) => (
          <article className="stat-card" key={label}>
            <div className={`icon-box ${tone}`}><Icon size={20} /></div>
            <span>{label}</span>
            <strong>{formatNumber(value, 0)}<small>{suffix}</small></strong>
            <div className="stat-rule" />
          </article>
        ))}
      </section>

      <section className="dashboard-grid">
        <article className="panel span-2">
          <div className="panel-head">
            <div><span className="section-kicker">AI SCOREBOARD</span><h2>综合评分领先</h2></div>
            <Link to="/rankings">查看完整排名 <ArrowUpRight size={15} /></Link>
          </div>
          {data.top_scores.length ? (
            <div className="leader-list">
              {data.top_scores.map((item, index) => (
                <div className="leader-row" key={item.symbol}>
                  <span className={`rank rank-${index + 1}`}>{String(index + 1).padStart(2, '0')}</span>
                  <div className="stock-name"><strong>{item.name}</strong><span>{item.symbol}</span></div>
                  <div className="score-track"><i style={{ width: `${item.total_score}%` }} /></div>
                  <div className="score-number"><strong>{item.total_score.toFixed(1)}</strong><span>综合分</span></div>
                  <span className={`mini-signal ${item.sentiment_score >= 50 ? 'positive' : 'negative'}`}>
                    情绪 {item.sentiment_score.toFixed(0)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-block"><FileSearch /><strong>还没有评分数据</strong><span>前往策略实验室生成演示数据或同步真实数据。</span></div>
          )}
        </article>

        <article className="panel sentiment-card">
          <div className="panel-head"><div><span className="section-kicker">SENTIMENT</span><h2>舆情温度</h2></div></div>
          <ReactECharts option={sentimentOption} style={{ height: 220 }} />
          <div className="legend-row">
            <span><i className="dot green" />利好 {data.sentiment_stats['利好'] ?? 0}</span>
            <span><i className="dot gray" />中性 {data.sentiment_stats['中性'] ?? 0}</span>
            <span><i className="dot red" />利空 {data.sentiment_stats['利空'] ?? 0}</span>
          </div>
        </article>
      </section>

      <section className="panel pipeline-strip">
        <div>
          <span className="section-kicker">PIPELINE STATUS</span>
          <h2>研究流水线</h2>
        </div>
        <div className="pipeline-steps">
          {['采集行情', '抓取新闻公告', '大模型情绪分析', '因子评分', '策略回测'].map((label, index) => (
            <div className="pipeline-step" key={label}>
              <span>{index + 1}</span><strong>{label}</strong>{index < 4 && <i />}
            </div>
          ))}
        </div>
        <div className={`job-pill ${data.latest_job?.status ?? 'idle'}`}>
          {data.latest_job ? `${data.latest_job.message} · ${data.latest_job.status}` : '等待首次运行'}
        </div>
      </section>
    </>
  )
}
