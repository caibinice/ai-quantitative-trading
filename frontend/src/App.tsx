import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Loading } from './components/StatePanel'

const Dashboard = lazy(() => import('./pages/Dashboard').then((module) => ({ default: module.Dashboard })))
const Market = lazy(() => import('./pages/Market').then((module) => ({ default: module.Market })))
const Rankings = lazy(() => import('./pages/Rankings').then((module) => ({ default: module.Rankings })))
const Sentiment = lazy(() => import('./pages/Sentiment').then((module) => ({ default: module.Sentiment })))
const Strategy = lazy(() => import('./pages/Strategy').then((module) => ({ default: module.Strategy })))

export default function App() {
  return <Layout><Suspense fallback={<Loading label="加载研究模块…" />}><Routes><Route path="/" element={<Dashboard />} /><Route path="/market" element={<Market />} /><Route path="/rankings" element={<Rankings />} /><Route path="/sentiment" element={<Sentiment />} /><Route path="/strategy" element={<Strategy />} /></Routes></Suspense></Layout>
}
