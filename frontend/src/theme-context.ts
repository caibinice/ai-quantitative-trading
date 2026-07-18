import { createContext, useContext } from 'react'

export type Theme = 'dark' | 'light'

export interface ThemeContextValue {
  theme: Theme
  toggleTheme: () => void
}

export const ThemeContext = createContext<ThemeContextValue | null>(null)

export function useTheme(): ThemeContextValue {
  const value = useContext(ThemeContext)
  if (!value) throw new Error('useTheme 必须在 ThemeProvider 内使用')
  return value
}

export function chartPalette(theme: Theme) {
  const light = theme === 'light'
  return {
    text: light ? '#53657a' : '#8fa2b7',
    muted: light ? '#718096' : '#718096',
    strong: light ? '#172033' : '#eaf3ff',
    line: light ? '#cdd8e5' : '#2a3b50',
    split: light ? '#e6edf5' : '#1a2a3c',
    track: light ? '#edf2f7' : '#1b2d40',
  }
}
