import { useMemo, useState } from 'react'
import { learningChapters, totalChecklistItems } from './curriculum'

interface StoredProgress {
  completed: string[]
  quizScores: Record<string, number>
}

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

  const update = (next: StoredProgress) => {
    setProgress(next)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  }

  const toggleChecklist = (chapterId: string, index: number) => {
    const key = checklistKey(chapterId, index)
    const completed = progress.completed.includes(key)
      ? progress.completed.filter((item) => item !== key)
      : [...progress.completed, key]
    update({ ...progress, completed })
  }

  const saveQuizScore = (chapterId: string, score: number) => {
    update({
      ...progress,
      quizScores: { ...progress.quizScores, [chapterId]: score },
    })
  }

  const resetProgress = () => update({ completed: [], quizScores: {} })

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
  }
}
