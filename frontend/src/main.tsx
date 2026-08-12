import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { ActionAuthProvider } from './components/ActionAuthProvider'
import { ThemeProvider } from './components/ThemeProvider'
import './styles.css'

const basename = import.meta.env.BASE_URL.replace(/\/$/, '') || '/'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <ActionAuthProvider>
        <BrowserRouter basename={basename}>
          <App />
        </BrowserRouter>
      </ActionAuthProvider>
    </ThemeProvider>
  </StrictMode>,
)
