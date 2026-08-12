import {
  clearActionAuthorization,
  getActionAuthorization,
} from './actionAuth'

const APP_BASE = import.meta.env.BASE_URL.replace(/\/$/, '')
const API_BASE = import.meta.env.VITE_API_BASE ?? `${APP_BASE}/api`

export function apiUrl(path: string): string {
  return `${API_BASE}${path}`
}

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const method = (options?.method ?? 'GET').toUpperCase()
  const requiresActionAuth = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)
    && !path.startsWith('/learning/')
    && !path.startsWith('/action-auth/')
  const headers = new Headers(options?.headers)
  headers.set('Content-Type', 'application/json')
  if (requiresActionAuth) {
    headers.set('Authorization', await getActionAuthorization())
  }
  const response = await fetch(apiUrl(path), {
    ...options,
    headers,
  })
  if (response.status === 401 && requiresActionAuth) clearActionAuthorization()
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }))
    const detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    throw new Error(detail || `请求失败 (${response.status})`)
  }
  return response.json() as Promise<T>
}

export function formatPercent(value?: number | null, digits = 2): string {
  if (value === undefined || value === null || Number.isNaN(value)) return '—'
  return `${(value * 100).toFixed(digits)}%`
}

export function formatNumber(value?: number | null, digits = 2): string {
  if (value === undefined || value === null || Number.isNaN(value)) return '—'
  return new Intl.NumberFormat('zh-CN', { maximumFractionDigits: digits }).format(value)
}
