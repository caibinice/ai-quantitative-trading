import { AlertTriangle, LoaderCircle } from 'lucide-react'

export function Loading({ label = '载入研究数据…' }: { label?: string }) {
  return <div className="state-panel"><LoaderCircle className="spin" />{label}</div>
}

export function ErrorPanel({ message }: { message: string }) {
  return <div className="state-panel error"><AlertTriangle />{message}</div>
}
