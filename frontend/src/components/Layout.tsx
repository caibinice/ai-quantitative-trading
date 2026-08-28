import {
  Activity,
  BarChart3,
  BrainCircuit,
  CandlestickChart,
  CalendarCheck2,
  ChevronDown,
  FlaskConical,
  Globe2,
  GraduationCap,
  ListTodo,
  Menu,
  Moon,
  Newspaper,
  Settings2,
  ShieldCheck,
  Sun,
  X,
} from 'lucide-react'
import { useEffect, useState, type ReactNode } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { useTheme } from '../theme-context'
import { languageOptions, tr, useI18n, type Language } from '../i18n'

const navItems = [
  { to: '/', label: '研究总览', icon: BarChart3 },
  { to: '/learn', label: '学习学院', icon: GraduationCap },
  { to: '/market', label: '行情财务', icon: CandlestickChart },
  { to: '/rankings', label: 'AI 选股', icon: BrainCircuit },
  { to: '/sentiment', label: '舆情雷达', icon: Newspaper },
  { to: '/strategy', label: '策略实验室', icon: FlaskConical },
  { to: '/walk-forward', label: '样本外验证', icon: CalendarCheck2 },
  { to: '/tasks', label: '任务中心', icon: ListTodo },
  { to: '/data-quality', label: '数据治理', icon: ShieldCheck },
]

export function Layout({ children }: { children: ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const { pathname } = useLocation()
  const { theme, toggleTheme } = useTheme()
  const { language, setLanguage } = useI18n()
  const activeItem = navItems.find(({ to }) => (
    to === '/' ? pathname === '/' : pathname === to || pathname.startsWith(`${to}/`)
  )) ?? navItems[0]
  const activeLabel = tr(activeItem.label)

  useEffect(() => {
    document.title = `${activeLabel} · ${tr('AI 量化研究舱')}`
  }, [activeLabel, language])

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileOpen ? 'mobile-open' : ''}`}>
        <div className="brand">
          <div className="brand-mark"><Activity size={22} /></div>
          <div>
            <strong>QUANT LAB</strong>
            <span>{tr("AI 量化研究舱")}</span>
          </div>
          <button className="mobile-close" onClick={() => setMobileOpen(false)} aria-label={tr("关闭菜单")}>
            <X size={20} />
          </button>
        </div>
        <nav>
          <div className="nav-label">{tr("研究工作台")}</div>
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              <Icon size={19} strokeWidth={1.8} />
              <span>{tr(label)}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-foot">
          <Settings2 size={17} />
          <div>
            <strong>{tr("研究模式")}</strong>
            <span>{tr("不连接券商 · 不真实下单")}</span>
          </div>
        </div>
      </aside>
      {mobileOpen && <button className="sidebar-scrim" onClick={() => setMobileOpen(false)} />}
      <main className="main-area">
        <header className="topbar">
          <button className="menu-trigger" onClick={() => setMobileOpen(true)} aria-label={tr("打开菜单")}>
            <Menu size={21} />
          </button>
          <div className="market-status"><span /><strong>{activeLabel}</strong><small>{tr("A 股研究数据")}</small></div>
          <div className="topbar-actions">
            <div className="topbar-note">{tr("数据可能延迟 · 仅供学习研究")}</div>
            <label className="language-switcher" title={tr('选择语言')}>
              <Globe2 size={16} />
              <select
                aria-label={tr('选择语言')}
                value={language}
                onChange={(event) => setLanguage(event.target.value as Language)}
              >
                {languageOptions.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
              <ChevronDown className="language-chevron" size={13} aria-hidden="true" />
            </label>
            <button className="theme-toggle" onClick={toggleTheme} aria-label={tr(theme === 'dark' ? '切换到明亮模式' : '切换到暗黑模式')} title={tr(theme === 'dark' ? '切换到明亮模式' : '切换到暗黑模式')}>
              {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
              <span>{tr(theme === 'dark' ? '明亮' : '暗黑')}</span>
            </button>
          </div>
        </header>
        <div className="content">{children}</div>
      </main>
    </div>
  )
}
