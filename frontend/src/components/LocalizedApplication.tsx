import { BrowserRouter } from 'react-router-dom'
import App from '../App'
import { useI18n } from '../i18n'
import { ActionAuthProvider } from './ActionAuthProvider'
import { ThemeProvider } from './ThemeProvider'

const basename = import.meta.env.BASE_URL.replace(/\/$/, '') || '/'

export function LocalizedApplication() {
  const { language } = useI18n()
  return (
    <ThemeProvider>
      <ActionAuthProvider>
        <BrowserRouter basename={basename}>
          <App key={language} />
        </BrowserRouter>
      </ActionAuthProvider>
    </ThemeProvider>
  )
}
