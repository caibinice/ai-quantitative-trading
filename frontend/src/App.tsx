import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Loading } from './components/StatePanel'

const Dashboard = lazy(() => import('./pages/Dashboard').then((module) => ({ default: module.Dashboard })))
const Market = lazy(() => import('./pages/Market').then((module) => ({ default: module.Market })))
const Rankings = lazy(() => import('./pages/Rankings').then((module) => ({ default: module.Rankings })))
const Sentiment = lazy(() => import('./pages/Sentiment').then((module) => ({ default: module.Sentiment })))
const Strategy = lazy(() => import('./pages/Strategy').then((module) => ({ default: module.Strategy })))
const WalkForward = lazy(() => import('./pages/WalkForward').then((module) => ({ default: module.WalkForward })))
const Tasks = lazy(() => import('./pages/Tasks').then((module) => ({ default: module.Tasks })))
const DataQuality = lazy(() => import('./pages/DataQuality').then((module) => ({ default: module.DataQuality })))
const LearningHome = lazy(() => import('./pages/LearningHome').then((module) => ({ default: module.LearningHome })))
const LearningChapter = lazy(() => import('./pages/LearningChapter').then((module) => ({ default: module.LearningChapter })))

export default function App() {
  return <Layout><Suspense fallback={<Loading label="加载研究模块…" />}><Routes><Route path="/" element={<Dashboard />} /><Route path="/learn" element={<LearningHome />} /><Route path="/learn/:chapterId" element={<LearningChapter />} /><Route path="/market" element={<Market />} /><Route path="/rankings" element={<Rankings />} /><Route path="/sentiment" element={<Sentiment />} /><Route path="/strategy" element={<Strategy />} /><Route path="/walk-forward" element={<WalkForward />} /><Route path="/tasks" element={<Tasks />} /><Route path="/data-quality" element={<DataQuality />} /></Routes></Suspense></Layout>
}
