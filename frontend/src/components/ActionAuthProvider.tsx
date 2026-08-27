import { FormEvent, ReactNode, useCallback, useEffect, useRef, useState } from 'react'

import {
  setActionTokenRequester,
  storeActionToken,
} from '../actionAuth'
import { tr } from '../i18n'

type ResolveToken = (authorization: string) => void
type RejectToken = (error: Error) => void

function verifyUrl(): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '')
  const apiBase = import.meta.env.VITE_API_BASE ?? `${base}/api`
  return `${apiBase}/action-auth/verify`
}

export function ActionAuthProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [verifying, setVerifying] = useState(false)
  const pending = useRef<{ resolve: ResolveToken; reject: RejectToken } | null>(null)

  const requestToken = useCallback(() => {
    setPassword('')
    setError('')
    setOpen(true)
    return new Promise<string>((resolve, reject) => {
      pending.current = { resolve, reject }
    })
  }, [])

  useEffect(() => {
    setActionTokenRequester(requestToken)
    return () => {
      setActionTokenRequester(null)
    }
  }, [requestToken])

  const close = () => {
    if (verifying) return
    setOpen(false)
    pending.current?.reject(new Error(tr('已取消操作验证')))
    pending.current = null
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setVerifying(true)
    setError('')
    try {
      const response = await fetch(verifyUrl(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      })
      const body = await response.json().catch(() => ({}))
      if (!response.ok || typeof body.token !== 'string') {
        throw new Error(body.detail || tr('操作密码验证失败'))
      }
      setOpen(false)
      pending.current?.resolve(storeActionToken(body.token))
      pending.current = null
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : tr('操作密码验证失败'))
    } finally {
      setVerifying(false)
    }
  }

  return (
    <>
      {children}
      {open && (
        <div className="action-auth-backdrop" role="presentation" onMouseDown={close}>
          <form
            className="action-auth-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="action-auth-title"
            onSubmit={submit}
            onMouseDown={(event) => event.stopPropagation()}
          >
            <span className="section-kicker">PROTECTED ACTION</span>
            <h2 id="action-auth-title">{tr("验证敏感操作")}</h2>
            <p>{tr("采集、AI 分析、回测和配置修改需要操作密码。验证结果仅在当前标签页短期有效。")}</p>
            <label className="field">
              <span>{tr("操作密码")}</span>
              <input
                autoFocus
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            {error && <div className="inline-alert">{error}</div>}
            <div className="action-auth-actions">
              <button className="button" type="button" onClick={close} disabled={verifying}>{tr("取消")}</button>
              <button className="button primary" type="submit" disabled={verifying || !password}>
                {tr(verifying ? '验证中…' : '验证并继续')}
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  )
}
