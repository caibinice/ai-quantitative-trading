import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Check,
  CheckCircle2,
  Clock3,
  ExternalLink,
  FileCode2,
  FlaskConical,
  HelpCircle,
  ListChecks,
  Target,
  TerminalSquare,
} from 'lucide-react'
import { useState } from 'react'
import { Link, Navigate, useParams } from 'react-router-dom'
import {
  chapterById,
  learningChapters,
  learningStages,
  type LearningChapter as LearningChapterType,
} from '../learning/curriculum'
import { checklistKey, useLearningProgress } from '../learning/useLearningProgress'

export function LearningChapter() {
  const { chapterId = '' } = useParams()
  const chapter = chapterById[chapterId]
  if (!chapter) return <Navigate to="/learn" replace />
  return <ChapterContent chapter={chapter} key={chapter.id} />
}

function ChapterContent({ chapter }: { chapter: LearningChapterType }) {
  const {
    progress,
    chapterCompleted,
    toggleChecklist,
    saveQuizScore,
    syncState,
  } = useLearningProgress()
  const [answers, setAnswers] = useState<Record<number, number>>({})
  const [submitted, setSubmitted] = useState(false)
  const stage = learningStages.find((item) => item.id === chapter.stage)
  const previous = learningChapters[chapter.order - 2]
  const next = learningChapters[chapter.order]
  const completed = chapterCompleted(chapter.id)
  const chapterPercent = Math.round((completed / chapter.checklist.length) * 100)
  const allAnswered = Object.keys(answers).length === chapter.quiz.length
  const currentScore = chapter.quiz.reduce(
    (score, question, index) => score + (answers[index] === question.answer ? 1 : 0),
    0,
  )

  const submitQuiz = () => {
    if (!allAnswered) return
    setSubmitted(true)
    saveQuizScore(chapter.id, currentScore)
  }

  return (
    <div className="chapter-page">
      <aside className="chapter-nav panel">
        <Link className="chapter-home-link" to="/learn"><ArrowLeft size={14} /> 学习学院</Link>
        <div className="chapter-nav-progress">
          <span>总体章节</span>
          <strong>{chapter.order} / {learningChapters.length}</strong>
        </div>
        <nav>
          {learningStages.map((learningStage) => (
            <div className="chapter-nav-stage" key={learningStage.id}>
              <span>阶段 {learningStage.id} · {learningStage.title}</span>
              {learningChapters.filter((item) => item.stage === learningStage.id).map((item) => {
                const done = chapterCompleted(item.id)
                return (
                  <Link className={item.id === chapter.id ? 'active' : ''} to={`/learn/${item.id}`} key={item.id}>
                    <i>{done === item.checklist.length ? <Check size={11} /> : item.order}</i>
                    <div><strong>{item.title}</strong><small>{done}/{item.checklist.length}</small></div>
                  </Link>
                )
              })}
            </div>
          ))}
        </nav>
      </aside>

      <main className="chapter-content">
        <header className="chapter-hero panel">
          <div className="chapter-breadcrumb">阶段 {chapter.stage} / 第 {chapter.order} 章</div>
          <div className="chapter-hero-main">
            <div>
              <span className="section-kicker">{stage?.subtitle}</span>
              <h1>{chapter.title}</h1>
              <p>{chapter.subtitle}</p>
            </div>
            <div className="chapter-meta">
              <span><Clock3 size={14} /> {chapter.duration}</span>
              <span><Target size={14} /> {chapter.level}</span>
            </div>
          </div>
          <div className="chapter-progress-line">
            <i style={{ width: `${chapterPercent}%` }} />
          </div>
          <small>
            {completed}/{chapter.checklist.length} 项完成 · {chapterPercent}%
            {' · '}
            {syncState === 'synced' ? '云端已同步' : syncState === 'offline' ? '离线缓存' : '同步中'}
          </small>
        </header>

        <section className="chapter-objective panel">
          <Target size={20} />
          <div><span>本章目标</span><p>{chapter.objective}</p></div>
        </section>

        <section className="chapter-section">
          <div className="chapter-section-title">
            <BookOpen size={18} />
            <div><span>KNOWLEDGE MAP</span><h2>知识梗概</h2></div>
          </div>
          <div className="concept-grid">
            {chapter.concepts.map((concept, index) => (
              <article className="panel concept-card" key={concept.title}>
                <span>{String(index + 1).padStart(2, '0')}</span>
                <h3>{concept.title}</h3>
                <p>{concept.summary}</p>
                <ul>{concept.points.map((point) => <li key={point}>{point}</li>)}</ul>
              </article>
            ))}
          </div>
        </section>

        <section className="chapter-two-column">
          <article className="panel chapter-outcomes">
            <div className="panel-head">
              <div><span className="section-kicker">LEARNING OUTCOMES</span><h2>学完你应该能做到</h2></div>
            </div>
            <div>
              {chapter.outcomes.map((outcome) => (
                <p key={outcome}><CheckCircle2 size={14} /> {outcome}</p>
              ))}
            </div>
          </article>

          <article className="panel project-map">
            <div className="panel-head">
              <div><span className="section-kicker">READ THE PROJECT</span><h2>对应项目文件</h2></div>
            </div>
            <div>
              {chapter.projectFiles.map((file) => (
                <div key={file.path}>
                  <FileCode2 size={15} />
                  <p><code>{file.path}</code><span>{file.reason}</span></p>
                </div>
              ))}
            </div>
          </article>
        </section>

        <section className="panel demo-panel">
          <div className="demo-copy">
            <span className="section-kicker">RUNNABLE LAB</span>
            <h2><FlaskConical size={18} /> 本章动手实验</h2>
            <p>{chapter.demo.summary}</p>
            <div className="demo-file"><FileCode2 size={14} /> {chapter.demo.file}</div>
            <div className="demo-command"><TerminalSquare size={15} /><code>{chapter.demo.command}</code></div>
          </div>
          <pre><code>{chapter.demo.snippet}</code></pre>
        </section>

        <section className="chapter-section">
          <div className="chapter-section-title">
            <ListChecks size={18} />
            <div><span>ACTION CHECKLIST</span><h2>本章完成清单</h2></div>
          </div>
          <div className="checklist-panel panel">
            {chapter.checklist.map((item, index) => {
              const checked = progress.completed.includes(checklistKey(chapter.id, index))
              return (
                <button
                  className={checked ? 'checked' : ''}
                  role="checkbox"
                  aria-checked={checked}
                  onClick={() => toggleChecklist(chapter.id, index)}
                  key={item}
                >
                  <i>{checked && <Check size={13} />}</i>
                  <span>{item}</span>
                  <small>{String(index + 1).padStart(2, '0')}</small>
                </button>
              )
            })}
          </div>
        </section>

        <section className="quiz-panel panel">
          <div className="quiz-head">
            <HelpCircle size={21} />
            <div><span className="section-kicker">QUICK CHECK</span><h2>本章小测验</h2></div>
            {submitted && (
              <strong className={currentScore >= 2 ? 'passed' : 'retry'}>
                {currentScore}/{chapter.quiz.length} · {currentScore >= 2 ? '通过' : '再复习一下'}
              </strong>
            )}
          </div>
          <div className="quiz-questions">
            {chapter.quiz.map((question, questionIndex) => (
              <article key={question.question}>
                <h3><span>{questionIndex + 1}</span>{question.question}</h3>
                <div className="quiz-options">
                  {question.options.map((option, optionIndex) => {
                    const selected = answers[questionIndex] === optionIndex
                    const answerClass = submitted
                      ? optionIndex === question.answer
                        ? 'correct'
                        : selected
                          ? 'wrong'
                          : ''
                      : ''
                    return (
                      <label className={`${selected ? 'selected' : ''} ${answerClass}`} key={option}>
                        <input
                          type="radio"
                          name={`question-${questionIndex}`}
                          checked={selected}
                          disabled={submitted}
                          onChange={() => setAnswers({ ...answers, [questionIndex]: optionIndex })}
                        />
                        <i />
                        <span>{option}</span>
                      </label>
                    )
                  })}
                </div>
                {submitted && <p className="quiz-explanation">{question.explanation}</p>}
              </article>
            ))}
          </div>
          <button className="button primary quiz-submit" disabled={!allAnswered || submitted} onClick={submitQuiz}>
            <CheckCircle2 size={15} /> {submitted ? '测验已提交' : '提交答案'}
          </button>
        </section>

        <section className="panel resource-panel">
          <div className="panel-head">
            <div><span className="section-kicker">CURATED REFERENCES</span><h2>延伸课程与官方资料</h2></div>
          </div>
          <div className="resource-list">
            {chapter.resources.map((resource) => (
              <a href={resource.url} target="_blank" rel="noreferrer" key={resource.url}>
                <BookOpen size={16} />
                <div><strong>{resource.title}</strong><span>{resource.provider} · {resource.note}</span></div>
                <ExternalLink size={14} />
              </a>
            ))}
          </div>
        </section>

        <footer className="chapter-pager">
          {previous
            ? <Link className="button" to={`/learn/${previous.id}`}><ArrowLeft size={15} /> 上一章：{previous.title}</Link>
            : <Link className="button" to="/learn"><ArrowLeft size={15} /> 返回路线图</Link>}
          {next
            ? <Link className="button primary" to={`/learn/${next.id}`}>下一章：{next.title} <ArrowRight size={15} /></Link>
            : <Link className="button primary" to="/strategy">开始毕业实验 <ArrowRight size={15} /></Link>}
        </footer>
      </main>
    </div>
  )
}
