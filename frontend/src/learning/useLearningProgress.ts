import { useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../api'
import { learningChapters, totalChecklistItems } from './curriculum'

interface StoredProgress {
  completed: string[]
  quizScores: Record<string, number>
}

interface RemoteProgress {
  completed: string[]
  quiz_scores: Record<string, number>
  updated_at: string | null
}

export type ProgressSyncState = 'loading' | 'synced' | 'saving' | 'offline'

const STORAGE_KEY = 'quant-learning-progress-v1'

function readProgress(): StoredProgress {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { completed: [], quizScores: {} }
    const parsed = JSON.parse(raw) as Partial<StoredProgress>
    return {
      completed: Array.isArray(parsed.completed) ? parsed.completed : [],
      quizScores: parsed.quizScores ?? {},
    }
  } catch {
    return { completed: [], quizScores: {} }
  }
}

export function checklistKey(chapterId: string, index: number) {
  return `${chapterId}:${index}`
}

export function useLearningProgress() {
  const [progress, setProgress] = useState<StoredProgress>(readProgress)
  const [syncState, setSyncState] = useState<ProgressSyncState>('loading')
  const progressRef = useRef(progress)
  const changedBeforeLoadRef = useRef(false)
  const loadedRef = useRef(false)
  const saveQueueRef = useRef<Promise<void>>(Promise.resolve())

  const cache = (next: StoredProgress) => {
    progressRef.current = next
    setProgress(next)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  }

  const queueRemoteSave = (next: StoredProgress, reset = false) => {
    setSyncState('saving')
    saveQueueRef.current = saveQueueRef.current
      .catch(() => undefined)
      .then(async () => {
        const remote = await api<RemoteProgress>('/learning/progress', reset
          ? { method: 'DELETE' }
          : {
              method: 'PUT',
              body: JSON.stringify({
                completed: next.completed,
                quiz_scores: next.quizScores,
              }),
            })
        if (progressRef.current === next) {
          cache({
            completed: remote.completed,
            quizScores: remote.quiz_scores,
          })
        }
        setSyncState('synced')
      })
      .catch(() => {
        setSyncState('offline')
      })
  }

  useEffect(() => {
    let cancelled = false
    api<RemoteProgress>('/learning/progress')
      .then((remote) => {
        if (cancelled) return
        const local = progressRef.current
        if (changedBeforeLoadRef.current) {
          loadedRef.current = true
          queueRemoteSave(local)
          return
        }

        if (remote.updated_at === null) {
          cache(local)
          loadedRef.current = true
          queueRemoteSave(local)
          return
        }

        cache({
          completed: remote.completed,
          quizScores: remote.quiz_scores,
        })
        loadedRef.current = true
        setSyncState('synced')
      })
      .catch(() => {
        if (!cancelled) {
          loadedRef.current = true
          setSyncState('offline')
        }
      })
    return () => {
      cancelled = true
    }
  }, [])

  const update = (build: (current: StoredProgress) => StoredProgress, reset = false) => {
    const next = build(progressRef.current)
    if (!loadedRef.current) changedBeforeLoadRef.current = true
    cache(next)
    queueRemoteSave(next, reset)
  }

  const toggleChecklist = (chapterId: string, index: number) => {
    const key = checklistKey(chapterId, index)
    update((current) => {
      const completed = current.completed.includes(key)
        ? current.completed.filter((item) => item !== key)
        : [...current.completed, key]
      return { ...current, completed }
    })
  }

  const saveQuizScore = (chapterId: string, score: number) => {
    update((current) => ({
      ...current,
      quizScores: {
        ...current.quizScores,
        [chapterId]: Math.max(current.quizScores[chapterId] ?? 0, score),
      },
    }))
  }

  const resetProgress = () => update(() => ({ completed: [], quizScores: {} }), true)

  const chapterCompleted = (chapterId: string) => {
    const chapter = learningChapters.find((item) => item.id === chapterId)
    if (!chapter) return 0
    return chapter.checklist.filter((_, index) => (
      progress.completed.includes(checklistKey(chapterId, index))
    )).length
  }

  const summary = useMemo(() => {
    const completedChecklist = progress.completed.length
    const passedQuizzes = Object.values(progress.quizScores).filter((score) => score >= 2).length
    return {
      completedChecklist,
      passedQuizzes,
      percent: Math.round((completedChecklist / totalChecklistItems) * 100),
    }
  }, [progress])

  return {
    progress,
    summary,
    chapterCompleted,
    toggleChecklist,
    saveQuizScore,
    resetProgress,
    syncState,
  }
}
