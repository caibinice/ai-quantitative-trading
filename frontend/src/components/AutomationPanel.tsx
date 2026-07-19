import { Bot, CheckCircle2, Clock3, Save, TimerReset } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api } from '../api'

interface AutomationSettings {
  news_analysis_enabled: boolean
  news_analysis_interval_hours: number
  next_run_at: string | null
  model: string
  thinking_enabled: boolean
  reasoning_effort: string
  backup_key_configured: boolean
  updated_at: string | null
}

export function AutomationPanel({ location }: { location: 'sentiment' | 'tasks' }) {
  const [settings, setSettings] = useState<AutomationSettings | null>(null)
  const [interval, setIntervalHours] = useState(6)
  const [enabled, setEnabled] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api<AutomationSettings>('/automation/settings')
      .then((value) => {
        setSettings(value)
        setIntervalHours(value.news_analysis_interval_hours)
        setEnabled(value.news_analysis_enabled)
      })
      .catch((reason: Error) => setError(reason.message))
  }, [])

  const save = async () => {
    setSaving(true)
    setError('')
    setMessage('')
    try {
      const value = await api<AutomationSettings>('/automation/settings', {
        method: 'PUT',
        body: JSON.stringify({
          news_analysis_enabled: enabled,
          news_analysis_interval_hours: interval,
        }),
      })
      setSettings(value)
      setMessage('配置已保存，调度器已自动重新排期。')
    } catch (reason) {
      setError((reason as Error).message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className={`panel automation-panel automation-panel-${location}`}>
      <div className="automation-copy">
        <span className="section-kicker">AUTOMATED SENTIMENT PIPELINE</span>
        <h2><TimerReset size={19} /> 自动舆情流水线</h2>
        <p>按固定间隔依次抓取新闻与公告，再分析尚未处理的事件。保存后无需重启服务。</p>
      </div>
      <label className="automation-toggle">
        <input
          type="checkbox"
          checked={enabled}
          onChange={(event) => setEnabled(event.target.checked)}
        />
        <span>{enabled ? '已启用' : '已暂停'}</span>
      </label>
      <label className="automation-interval">
        <span>运行间隔</span>
        <div>
          <input
            type="number"
            min={1}
            max={48}
            value={interval}
            onChange={(event) => setIntervalHours(Math.min(48, Math.max(1, Number(event.target.value) || 1)))}
          />
          <small>小时</small>
        </div>
      </label>
      <div className="automation-model">
        <Bot size={17} />
        <div><span>分析模型</span><strong>{settings?.model ?? '读取中…'}</strong></div>
        <small>
          {settings?.thinking_enabled ? `Thinking · ${settings.reasoning_effort}` : '标准模式'}
          {' · '}
          {settings?.backup_key_configured ? '备用 Key 就绪' : '单 Key'}
        </small>
      </div>
      <div className="automation-next">
        <Clock3 size={17} />
        <div>
          <span>下次自动运行</span>
          <strong>{formatNextRun(settings?.next_run_at, enabled)}</strong>
        </div>
      </div>
      <button className="button primary automation-save" disabled={saving} onClick={save}>
        <Save size={15} /> {saving ? '保存中…' : '保存并立即生效'}
      </button>
      {(message || error) && (
        <div className={`automation-feedback ${error ? 'error' : ''}`}>
          {!error && <CheckCircle2 size={14} />}
          {error || message}
        </div>
      )}
    </section>
  )
}

function formatNextRun(value: string | null | undefined, enabled: boolean): string {
  if (!enabled) return '已暂停'
  if (!value) return '等待调度器'
  return new Date(value).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}
