import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { I18nProvider } from './components/I18nProvider'
import { LocalizedApplication } from './components/LocalizedApplication'
import './styles.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <I18nProvider>
      <LocalizedApplication />
    </I18nProvider>
  </StrictMode>,
)
