type TokenRequester = () => Promise<string>

const TOKEN_KEY = 'quant-action-token'
let tokenRequester: TokenRequester | null = null

function storedAuthorization(): string | null {
  const token = sessionStorage.getItem(TOKEN_KEY)
  if (!token) return null
  const expiresAt = Number(token.split('.', 1)[0])
  if (!Number.isFinite(expiresAt) || expiresAt * 1000 <= Date.now()) {
    sessionStorage.removeItem(TOKEN_KEY)
    return null
  }
  return `Bearer ${token}`
}

export function setActionTokenRequester(requester: TokenRequester | null): void {
  tokenRequester = requester
}

export function storeActionToken(token: string): string {
  sessionStorage.setItem(TOKEN_KEY, token)
  return `Bearer ${token}`
}

export function clearActionAuthorization(): void {
  sessionStorage.removeItem(TOKEN_KEY)
}

export async function getActionAuthorization(): Promise<string> {
  const existing = storedAuthorization()
  if (existing) return existing
  if (!tokenRequester) throw new Error('操作验证界面尚未就绪')
  return tokenRequester()
}
