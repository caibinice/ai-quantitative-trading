import { AlertTriangle, LoaderCircle } from 'lucide-react'
import { tr } from '../i18n'

export function Loading({ label = tr('载入研究数据…') }: { label?: string }) {
  return <div className="state-panel"><LoaderCircle className="spin" />{label}</div>
}

export function ErrorPanel({ message }: { message: string }) {
  return <div className="state-panel error"><AlertTriangle />{tr(message)}</div>
}
