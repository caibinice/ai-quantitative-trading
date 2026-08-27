import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Check,
  CheckCircle2,
  Clock3,
  Download,
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
import { apiUrl } from '../api'
import {
  chapterById as sourceChapterById,
  learningChapters as sourceLearningChapters,
  learningStages as sourceLearningStages,
  type LearningChapter as LearningChapterType,
} from '../learning/curriculum'
import { checklistKey, useLearningProgress } from '../learning/useLearningProgress'
import { chapterGuides as sourceChapterGuides } from '../learning/chapterGuides'
import { localizeLearning } from '../learning/localizeLearning'
import { localize, tr } from '../i18n'

export function LearningChapter() {
  const { chapterId = '' } = useParams()
  const chapter = sourceChapterById[chapterId]
  if (!chapter) return <Navigate to="/learn" replace />
  return <ChapterContent chapter={localizeLearning(chapter)} key={chapter.id} />
}

function ChapterContent({ chapter }: { chapter: LearningChapterType }) {
  const learningChapters = localizeLearning(sourceLearningChapters)
  const learningStages = localizeLearning(sourceLearningStages)
  const chapterGuides = localizeLearning(sourceChapterGuides)
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
  const guide = chapterGuides[chapter.id]
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
        <Link className="chapter-home-link" to="/learn"><ArrowLeft size={14} /> {tr("学习学院")}</Link>
        <div className="chapter-nav-progress">
          <span>{tr("总体章节")}</span>
          <strong>{chapter.order} / {learningChapters.length}</strong>
        </div>
        <nav>
          {learningStages.map((learningStage) => (
            <div className="chapter-nav-stage" key={learningStage.id}>
              <span>{tr("阶段")} {learningStage.id} · {learningStage.title}</span>
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
          <div className="chapter-breadcrumb">
            {localize({
              en: 'Stage {stage} / Chapter {order}',
              'zh-CN': '阶段 {stage} / 第 {order} 章',
              ja: 'ステージ {stage} / 第{order}章',
            }, { stage: chapter.stage, order: chapter.order })}
          </div>
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
          <small>{localize({
            en: '{completed}/{total} completed · {percent}% · {sync}',
            'zh-CN': '{completed}/{total} 项完成 · {percent}% · {sync}',
            ja: '{completed}/{total}件完了 · {percent}% · {sync}',
          }, {
            completed,
            total: chapter.checklist.length,
            percent: chapterPercent,
            sync: tr(syncState === 'synced' ? '云端已同步' : syncState === 'offline' ? '离线缓存' : '同步中'),
          })}</small>
        </header>

        <section className="chapter-objective panel">
          <Target size={20} />
          <div><span>{tr("本章目标")}</span><p>{chapter.objective}</p></div>
        </section>

        {guide && (
          <section className="chapter-textbook">
            <div className="chapter-section-title">
              <BookOpen size={18} />
              <div><span>FULL CHAPTER GUIDE</span><h2>{tr("本章教材正文")}</h2></div>
            </div>
            <article className="panel textbook-intro">
              <span>{tr("先用大白话说")}</span>
              <p>{guide.plainLanguage}</p>
            </article>
            {chapter.id === 'market-basics' && <KlinePrimer />}
            <div className="textbook-layout">
              <div className="textbook-sections">
                {guide.sections.map((section) => (
                  <article className="panel textbook-section" key={section.title}>
                    <h3>{section.title}</h3>
                    {section.paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
                    {section.bullets && <ul>{section.bullets.map((bullet) => <li key={bullet}>{bullet}</li>)}</ul>}
                  </article>
                ))}
              </div>
              <aside className="textbook-aside">
                <article className="panel guide-diagram">
                  <span className="section-kicker">PROCESS MAP</span>
                  <h3>{guide.diagram.title}</h3>
                  <div>
                    {guide.diagram.nodes.map((node, index) => (
                      <div key={node.title}>
                        <i>{index + 1}</i>
                        <p><strong>{node.title}</strong><span>{node.detail}</span></p>
                        {index < guide.diagram.nodes.length - 1 && <b>↓</b>}
                      </div>
                    ))}
                  </div>
                </article>
                <article className="panel guide-terms">
                  <span className="section-kicker">PLAIN GLOSSARY</span>
                  <h3>{tr("本章名词翻译")}</h3>
                  {guide.terms.map((item) => (
                    <div key={item.term}>
                      <strong>{item.term}</strong>
                      <p>{item.meaning}</p>
                      <small>{tr("例：")}{item.example}</small>
                    </div>
                  ))}
                </article>
              </aside>
            </div>
            <article className="panel worked-example">
              <div>
                <span className="section-kicker">WORKED EXAMPLE</span>
                <h3>{guide.workedExample.title}</h3>
                <p>{guide.workedExample.question}</p>
              </div>
              <ol>{guide.workedExample.steps.map((step) => <li key={step}>{step}</li>)}</ol>
              <strong>{guide.workedExample.conclusion}</strong>
            </article>
          </section>
        )}

        <section className="chapter-section">
          <div className="chapter-section-title">
            <BookOpen size={18} />
            <div><span>KNOWLEDGE MAP</span><h2>{tr("知识梗概")}</h2></div>
          </div>
          <div className="concept-grid">
            {chapter.concepts.map((concept, index) => (
              <Link className="panel concept-card" to={`/learn/${chapter.id}/concepts/${index}`} key={concept.title}>
                <span>{String(index + 1).padStart(2, '0')}</span>
                <h3>{concept.title}</h3>
                <p>{concept.summary}</p>
                <ul>{concept.points.map((point) => <li key={point}>{point}</li>)}</ul>
                <strong className="concept-enter">{tr("进入详情")} <ArrowRight size={13} /></strong>
              </Link>
            ))}
          </div>
        </section>

        <section className="chapter-two-column">
          <article className="panel chapter-outcomes">
            <div className="panel-head">
              <div><span className="section-kicker">LEARNING OUTCOMES</span><h2>{tr("学完你应该能做到")}</h2></div>
            </div>
            <div>
              {chapter.outcomes.map((outcome) => (
                <p key={outcome}><CheckCircle2 size={14} /> {outcome}</p>
              ))}
            </div>
          </article>

          <article className="panel project-map">
            <div className="panel-head">
              <div><span className="section-kicker">READ THE PROJECT</span><h2>{tr("对应项目文件")}</h2></div>
            </div>
            <div>
              {chapter.projectFiles.map((file) => (
                <a
                  href={downloadUrl(file.path)}
                  download
                  title={localize({
                    en: 'Download {path}',
                    'zh-CN': '下载 {path}',
                    ja: '{path} をダウンロード',
                  }, { path: file.path })}
                  key={file.path}
                >
                  <FileCode2 size={15} />
                  <p><code>{file.path}</code><span>{file.reason}</span></p>
                  <Download size={14} />
                </a>
              ))}
            </div>
          </article>
        </section>

        <section className="panel demo-panel">
          <div className="demo-copy">
            <span className="section-kicker">RUNNABLE LAB</span>
            <h2><FlaskConical size={18} /> {tr("本章动手实验")}</h2>
            <p>{chapter.demo.summary}</p>
            <a className="demo-file" href={downloadUrl(chapter.demo.file)} download>
              <FileCode2 size={14} /> {chapter.demo.file}<Download size={13} />
            </a>
            <div className="demo-command"><TerminalSquare size={15} /><code>{chapter.demo.command}</code></div>
          </div>
          <pre><code>{chapter.demo.snippet}</code></pre>
        </section>

        <section className="chapter-section">
          <div className="chapter-section-title">
            <ListChecks size={18} />
            <div><span>ACTION CHECKLIST</span><h2>{tr("本章完成清单")}</h2></div>
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
            <div><span className="section-kicker">QUICK CHECK</span><h2>{tr("本章小测验")}</h2></div>
            {submitted && (
              <strong className={currentScore >= 2 ? 'passed' : 'retry'}>
                {currentScore}/{chapter.quiz.length} · {tr(currentScore >= 2 ? '通过' : '再复习一下')}
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
            <CheckCircle2 size={15} /> {tr(submitted ? '测验已提交' : '提交答案')}
          </button>
        </section>

        <section className="panel resource-panel">
          <div className="panel-head">
            <div><span className="section-kicker">CURATED REFERENCES</span><h2>{tr("延伸课程与官方资料")}</h2></div>
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
            ? <Link className="button" to={`/learn/${previous.id}`}><ArrowLeft size={15} /> {tr("上一章：")}{previous.title}</Link>
            : <Link className="button" to="/learn"><ArrowLeft size={15} /> {tr("返回路线图")}</Link>}
          {next
            ? <Link className="button primary" to={`/learn/${next.id}`}>{tr("下一章：")}{next.title} <ArrowRight size={15} /></Link>
            : <Link className="button primary" to="/strategy">{tr("开始毕业实验")} <ArrowRight size={15} /></Link>}
        </footer>
      </main>
    </div>
  )
}

function KlinePrimer() {
  const candles = [
    { type: 'up', label: '上涨实体', high: '8%', low: '12%', bodyTop: '31%', bodyHeight: '38%' },
    { type: 'down', label: '下跌实体', high: '13%', low: '9%', bodyTop: '25%', bodyHeight: '44%' },
    { type: 'up', label: '长下影', high: '17%', low: '4%', bodyTop: '28%', bodyHeight: '22%' },
    { type: 'down', label: '长上影', high: '3%', low: '19%', bodyTop: '43%', bodyHeight: '23%' },
  ]
  return (
    <article className="panel kline-primer">
      <div className="kline-copy">
        <span className="section-kicker">CANDLESTICK ANATOMY</span>
        <h3>{tr("先把 K 线当成 OHLC 数据图，不背“形态口诀”")}</h3>
        <p>{tr("细线覆盖最低到最高，矩形实体覆盖开盘到收盘。右侧四根只是不同 OHLC 组合；它们描述已经发生的价格路径，不自动包含未来方向。")}</p>
        <div><span><i className="up" />{tr("收盘 ≥ 开盘")}</span><span><i className="down" />{tr("收盘 ＜ 开盘")}</span></div>
      </div>
      <div className="candlestick-board">
        <span className="price-label high">{tr("High 最高")}</span>
        <span className="price-label low">{tr("Low 最低")}</span>
        {candles.map((candle) => (
          <div className="teaching-candle" key={candle.label}>
            <i className={`wick ${candle.type}`} style={{ top: candle.high, bottom: candle.low }} />
            <b className={`body ${candle.type}`} style={{ top: candle.bodyTop, height: candle.bodyHeight }} />
            <span>{tr(candle.label)}</span>
          </div>
        ))}
      </div>
    </article>
  )
}

function downloadUrl(path: string): string {
  const encoded = path.split('/').map(encodeURIComponent).join('/')
  return apiUrl(`/learning/files/${encoded}`)
}
