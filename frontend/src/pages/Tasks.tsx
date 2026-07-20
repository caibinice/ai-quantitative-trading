import { AlertCircle, CheckCircle2, Clock3, ListTodo, Play, RefreshCcw, RotateCcw, XCircle } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { AutomationPanel } from '../components/AutomationPanel'
import { PageHeader } from '../components/PageHeader'
import { ErrorPanel, Loading } from '../components/StatePanel'
import { formatBeijingDateTime } from '../dateTime'
import type { ResearchTask } from '../types'

const taskNames: Record<string, string> = {
  market_sync: '行情与舆情同步',
  infrastructure_sync: '研究基础数据同步',
  sentiment_analysis: '大模型情绪分析',
  factor_scoring: '点时因子评分',
  backtest: '历史回测',
  walk_forward: 'Walk-forward 验证',
  data_quality: '数据质量检查',
}

export function Tasks() {
  const [tasks, setTasks] = useState<ResearchTask[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [creating, setCreating] = useState('')

  const load = useCallback(() => {
    api<ResearchTask[]>('/tasks').then((rows) => { setTasks(rows); setLoading(false) }).catch((err: Error) => { setError(err.message); setLoading(false) })
  }, [])

  useEffect(() => {
    load()
    const timer = window.setInterval(load, 3000)
    return () => window.clearInterval(timer)
  }, [load])

  const counts = useMemo(() => tasks.reduce<Record<string, number>>((result, task) => {
    result[task.status] = (result[task.status] ?? 0) + 1
    return result
  }, {}), [tasks])

  const create = async (taskType: string) => {
    setCreating(taskType); setError('')
    try {
      await api('/tasks', { method: 'POST', body: JSON.stringify({ task_type: taskType, payload: {} }) })
      load()
    } catch (err) { setError((err as Error).message) }
    finally { setCreating('') }
  }

  const mutate = async (task: ResearchTask, action: 'retry' | 'cancel') => {
    try { await api(`/tasks/${task.id}/${action}`, { method: 'POST' }); load() }
    catch (err) { setError((err as Error).message) }
  }

  if (error && !tasks.length) return <ErrorPanel message={error} />
  if (loading) return <Loading label="载入任务队列…" />

  const statItems = [
    { key: 'queued', label: '排队中', icon: Clock3, tone: 'amber' },
    { key: 'running', label: '执行中', icon: RefreshCcw, tone: 'cyan' },
    { key: 'success', label: '已完成', icon: CheckCircle2, tone: 'green' },
    { key: 'failed', label: '失败', icon: AlertCircle, tone: 'red' },
  ]

  return <>
    <PageHeader eyebrow="Persistent task queue" title="研究任务中心" description="耗时采集、AI 分析和样本外实验进入 MySQL 持久化队列，由独立 Worker 执行；API 不再长时间阻塞。" actions={<button className="button" onClick={load}><RefreshCcw size={16} />刷新</button>} />
    {error && <div className="inline-alert">{error}</div>}
    <AutomationPanel location="tasks" />
    <section className="stat-grid task-stats">{statItems.map(({ key, label, icon: Icon, tone }) => <article className="stat-card" key={key}><div className={`icon-box ${tone}`}><Icon size={20} className={key === 'running' && counts[key] ? 'spin' : ''} /></div><span>{label}</span><strong>{counts[key] ?? 0}<small>项</small></strong><div className="stat-rule" /></article>)}</section>
    <section className="panel quick-task-panel"><div className="panel-head"><div><span className="section-kicker">QUICK ACTIONS</span><h2>常用队列任务</h2></div><ListTodo size={20} /></div><div className="quick-task-grid">{[
      ['infrastructure_sync', '同步研究基础数据', '交易日历、沪深300、点时财务'],
      ['data_quality', '运行质量检查', '缺口、过期、异常值与覆盖率'],
      ['factor_scoring', '刷新点时评分', '只使用评分日之前可得财务'],
      ['sentiment_analysis', '分析待处理舆情', '调用大模型并保存结构化结果'],
    ].map(([type, label, detail]) => <button key={type} onClick={() => create(type)} disabled={!!creating}><span><Play size={15} /></span><div><strong>{creating === type ? '正在入队…' : label}</strong><small>{detail}</small></div></button>)}</div></section>
    <section className="panel table-panel task-table"><div className="panel-head"><div><span className="section-kicker">QUEUE HISTORY</span><h2>任务执行记录</h2></div><span>{tasks.length} 条</span></div><div className="table-scroll"><table><thead><tr><th>ID</th><th>任务</th><th>状态</th><th>进度</th><th>尝试</th><th>创建时间（北京时间）</th><th>结果 / 错误</th><th>操作</th></tr></thead><tbody>{tasks.map((task) => <tr key={task.id}><td>#{task.id}</td><td><strong>{taskNames[task.task_type] ?? task.task_type}</strong></td><td><span className={`task-status ${task.status}`}>{statusLabel(task.status)}</span></td><td><div className="task-progress"><i><b style={{ width: `${task.progress * 100}%` }} /></i><span>{(task.progress * 100).toFixed(0)}%</span></div></td><td>{task.attempts}/{task.max_attempts}</td><td>{formatBeijingDateTime(task.created_at)}</td><td className="task-message">{task.error || String(task.result.message ?? (task.status === 'success' ? '执行完成' : '—'))}</td><td><div className="row-actions">{task.status === 'queued' && <button title="取消" onClick={() => mutate(task, 'cancel')}><XCircle size={15} /></button>}{(task.status === 'failed' || task.status === 'cancelled') && <button title="重试" onClick={() => mutate(task, 'retry')}><RotateCcw size={15} /></button>}</div></td></tr>)}</tbody></table></div></section>
  </>
}

function statusLabel(status: ResearchTask['status']) {
  return { queued: '排队中', running: '执行中', success: '已完成', failed: '失败', cancelled: '已取消' }[status]
}
