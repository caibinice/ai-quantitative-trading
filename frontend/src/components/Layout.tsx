import {
  Activity,
  BarChart3,
  BrainCircuit,
  CandlestickChart,
  FlaskConical,
  Menu,
  Newspaper,
  Settings2,
  X,
} from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: '研究总览', icon: BarChart3 },
  { to: '/market', label: '行情财务', icon: CandlestickChart },
  { to: '/rankings', label: 'AI 选股', icon: BrainCircuit },
  { to: '/sentiment', label: '舆情雷达', icon: Newspaper },
  { to: '/strategy', label: '策略实验室', icon: FlaskConical },
]

export function Layout({ children }: { children: ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileOpen ? 'mobile-open' : ''}`}>
        <div className="brand">
          <div className="brand-mark"><Activity size={22} /></div>
          <div>
            <strong>QUANT LAB</strong>
            <span>AI 量化研究舱</span>
          </div>
          <button className="mobile-close" onClick={() => setMobileOpen(false)} aria-label="关闭菜单">
            <X size={20} />
          </button>
        </div>
        <nav>
          <div className="nav-label">研究工作台</div>
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              <Icon size={19} strokeWidth={1.8} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-foot">
          <Settings2 size={17} />
          <div>
            <strong>研究模式</strong>
            <span>不连接券商 · 不真实下单</span>
          </div>
        </div>
      </aside>
      {mobileOpen && <button className="sidebar-scrim" onClick={() => setMobileOpen(false)} />}
      <main className="main-area">
        <header className="topbar">
          <button className="menu-trigger" onClick={() => setMobileOpen(true)} aria-label="打开菜单">
            <Menu size={21} />
          </button>
          <div className="market-status"><span /> A 股研究数据</div>
          <div className="topbar-note">数据可能延迟 · 仅供学习研究</div>
        </header>
        <div className="content">{children}</div>
      </main>
    </div>
  )
}
