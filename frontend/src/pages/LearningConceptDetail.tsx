import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Beaker,
  BookOpen,
  Braces,
  CheckCircle2,
  CircleHelp,
  Database,
  Download,
  ExternalLink,
  FileCode2,
  GitBranch,
  Lightbulb,
  ListChecks,
  PlayCircle,
  Quote,
  Target,
} from 'lucide-react'
import { Link, Navigate, useParams } from 'react-router-dom'
import { apiUrl } from '../api'
import { conceptLessons as sourceConceptLessons, lessonKey } from '../learning/conceptLessons'
import { beginnerWorkbooks as sourceBeginnerWorkbooks } from '../learning/beginnerWorkbooks'
import { chapterById as sourceChapterById } from '../learning/curriculum'
import { chapterGuides as sourceChapterGuides } from '../learning/chapterGuides'
import { localizeLearning, localizeLearningText } from '../learning/localizeLearning'
import { localize, tr } from '../i18n'

export function LearningConceptDetail() {
  const conceptLessons = localizeLearning(sourceConceptLessons)
  const beginnerWorkbooks = localizeLearning(sourceBeginnerWorkbooks)
  const chapterById = localizeLearning(sourceChapterById)
  const chapterGuides = localizeLearning(sourceChapterGuides)
  const { chapterId = '', conceptIndex = '' } = useParams()
  const chapter = chapterById[chapterId]
  const index = Number(conceptIndex)
  const concept = chapter?.concepts[index]
  const lesson = conceptLessons[lessonKey(chapterId, index)]
  const guide = chapterGuides[chapterId]
  const workbook = beginnerWorkbooks[chapterId]
  const coach = workbook?.concepts[index]

  if (!chapter || !concept || !lesson || !Number.isInteger(index)) {
    return <Navigate to={chapter ? `/learn/${chapter.id}` : '/learn'} replace />
  }

  const previous = index > 0 ? index - 1 : null
  const next = index < chapter.concepts.length - 1 ? index + 1 : null

  return (
    <div className="concept-detail-page">
      <aside className="panel concept-detail-nav">
        <Link className="chapter-home-link" to={`/learn/${chapter.id}`}>
          <ArrowLeft size={14} /> {localize({
            en: 'Back to Chapter {order}',
            'zh-CN': '返回第 {order} 章',
            ja: '第{order}章に戻る',
          }, { order: chapter.order })}
        </Link>
        <div className="concept-detail-nav-title">
          <span>{tr("本章知识点")}</span>
          <strong>{chapter.title}</strong>
        </div>
        <nav>
          {chapter.concepts.map((item, itemIndex) => (
            <Link
              className={itemIndex === index ? 'active' : ''}
              to={`/learn/${chapter.id}/concepts/${itemIndex}`}
              key={item.title}
            >
              <i>{String(itemIndex + 1).padStart(2, '0')}</i>
              <span>{item.title}</span>
              <ArrowRight size={13} />
            </Link>
          ))}
        </nav>
        <div className="concept-nav-tip">
          <Lightbulb size={16} />
          <span>{tr("先读心智模型，再沿流程图理解信息怎样在系统中流动。")}</span>
        </div>
      </aside>

      <main className="concept-detail-content">
        <header className="panel concept-detail-hero">
          <div className="chapter-breadcrumb">
            {localize({
              en: 'Learning Academy / Chapter {chapter} / Concept {concept}',
              'zh-CN': '学习学院 / 第 {chapter} 章 / 知识点 {concept}',
              ja: '学習アカデミー / 第{chapter}章 / 知識ポイント{concept}',
            }, { chapter: chapter.order, concept: index + 1 })}
          </div>
          <span className="section-kicker">DEEP DIVE LESSON</span>
          <h1>{concept.title}</h1>
          <p>{concept.summary}</p>
          <div className="concept-hero-tags">
            <span><BookOpen size={14} /> {tr("详解")}</span>
            <span><GitBranch size={14} /> {tr("项目映射")}</span>
            <span><Beaker size={14} /> {tr("动手练习")}</span>
          </div>
        </header>

        <section className="panel mental-model">
          <Lightbulb size={22} />
          <div><span>{tr("先建立心智模型")}</span><p>{lesson.mentalModel}</p></div>
        </section>

        {workbook && coach && (
          <section className="panel beginner-compass">
            <div className="beginner-compass-intro">
              <CircleHelp size={21} />
              <div>
                <span className="section-kicker">BEGINNER TRANSLATION</span>
                <h2>{tr("这一页到底要学会什么")}</h2>
                <p>{workbook.beginnerNote}</p>
                <strong><Target size={15} /> {tr("本知识点重点：")}{coach.focus}</strong>
              </div>
            </div>
            <div className="plain-word-grid">
              {workbook.plainWords.map((item) => (
                <article key={item.term}>
                  <strong>{item.term}</strong>
                  <p>{item.translation}</p>
                  <small>{tr("在本项目中：")}{item.projectUse}</small>
                </article>
              ))}
            </div>
          </section>
        )}

        {guide && (
          <section className="panel concept-glossary">
            <div className="panel-head">
              <div><span className="section-kicker">{localize({ en: 'TERMS IN PLAIN LANGUAGE', 'zh-CN': '通俗术语解释', ja: 'やさしい用語解説' })}</span><h2>{tr("遇到名词先看这里")}</h2></div>
            </div>
            <div>
              {guide.terms.map((item) => (
                <article key={item.term}>
                  <strong>{item.term}</strong>
                  <p>{item.meaning}</p>
                  <small>{tr("例：")}{item.example}</small>
                </article>
              ))}
            </div>
          </section>
        )}

        <section className="concept-reading-grid">
          <article className="panel concept-prose">
            <span className="section-kicker">CORE EXPLANATION</span>
            <h2>{tr("把概念讲透")}</h2>
            {lesson.deepDive.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
            <div className="concept-key-points">
              <strong>{tr("读完先记住")}</strong>
              {concept.points.map((point) => (
                <span key={point}><CheckCircle2 size={15} /> {point}</span>
              ))}
            </div>
          </article>

          <article className="panel concept-visual-panel">
            <span className="section-kicker">VISUAL MAP</span>
            <h2>{lesson.visualTitle}</h2>
            <div className="concept-flow">
              {lesson.flow.map((node, nodeIndex) => (
                <div className="concept-flow-node" key={node.title}>
                  <i>{String(nodeIndex + 1).padStart(2, '0')}</i>
                  <div><strong>{node.title}</strong><span>{node.detail}</span></div>
                  {nodeIndex < lesson.flow.length - 1 && <ArrowRight size={16} />}
                </div>
              ))}
            </div>
          </article>
        </section>

        <section className="panel concept-example">
          <div className="concept-example-copy">
            <span className="section-kicker">PROJECT EXAMPLE</span>
            <h2><GitBranch size={19} /> {lesson.exampleTitle}</h2>
            <p>{lesson.example}</p>
          </div>
          {lesson.code && <pre><code>{lesson.code}</code></pre>}
        </section>

        <section className="concept-reading-grid compact expanded-learning-grid">
          <article className="panel concept-list-card pitfall">
            <div className="panel-head">
              <div><span className="section-kicker">COMMON PITFALLS</span><h2>{tr("常见误区")}</h2></div>
              <AlertTriangle size={20} />
            </div>
            {lesson.pitfalls.map((item, itemIndex) => {
              const detail = coach?.pitfallDetails[itemIndex]
              return (
                <article className="pitfall-detail" key={item}>
                  <header><span>{tr("误区")} {itemIndex + 1}</span><strong>{item}</strong></header>
                  <div><b>{tr("为什么会错")}</b><p>{detail?.why ?? localizeLearningText('它省略了必要的前提、时间和验证步骤，可能让偶然结果看起来像稳定规律。')}</p></div>
                  <div><b>{tr("正确做法")}</b><p>{detail?.correction ?? localizeLearningText('把说法改成可计算规则，保留数据来源，并用样本外结果和测试验证。')}</p></div>
                  <div className="pitfall-check"><b>{tr("用这个问题自查")}</b><p>{detail?.selfCheck ?? localize({
                    en: 'Can you explain without relying on “gut feeling” why “{item}” is unreliable, and provide verifiable evidence?',
                    'zh-CN': '你能不用“感觉”解释为什么“{item}”不可靠，并给出可验证证据吗？',
                    ja: '「感覚」に頼らず、「{item}」が信頼できない理由を説明し、検証可能な根拠を示せますか？',
                  }, { item })}</p></div>
                </article>
              )
            })}
          </article>
          <article className="panel concept-list-card practice">
            <div className="panel-head">
              <div><span className="section-kicker">PRACTICE</span><h2>{tr("马上动手")}</h2></div>
              <ListChecks size={20} />
            </div>
            <div className="practice-goal"><Target size={17} /><p><strong>{tr("完成证据")}</strong>{coach?.practiceEvidence ?? localizeLearningText('留下可重复运行的代码、输出和解释。')}</p></div>
            {lesson.practice.map((item, itemIndex) => (
              <div className="practice-task" key={item}>
                <span>{itemIndex + 1}</span>
                <div><strong>{item}</strong><p>{localizeLearningText(itemIndex === 0 ? '先不改参数完成一次，把操作和结果记在研究日志。' : '再用自己的话解释结果；如果解释不了，就回到上面的术语和流程图。')}</p></div>
              </div>
            ))}
            <div className="practice-challenge">
              <Braces size={17} />
              <p><strong>{tr("只改一个变量")}</strong>{coach?.challenge ?? localizeLearningText('修改一个输入，运行后比较前后差异。')}</p>
            </div>
          </article>
        </section>

        {workbook && (
          <section className="panel guided-lab">
            <div className="guided-lab-head">
              <div><span className="section-kicker">GUIDED LAB</span><h2><PlayCircle size={20} /> {workbook.lab.title}</h2><p>{workbook.lab.goal}</p></div>
              <div className="lab-downloads">
                <a className="button" href={downloadUrl(workbook.lab.datasetPath)} download><Database size={15} /> {tr("下载练习数据")}</a>
                <a className="button primary" href={downloadUrl(workbook.lab.scriptPath)} download><FileCode2 size={15} /> {tr("下载跟练脚本")}</a>
              </div>
            </div>

            <div className="lab-material-note">
              <Database size={18} />
              <div><strong>{workbook.lab.datasetPath}</strong><p>{workbook.lab.datasetDescription}</p></div>
            </div>

            <div className="guided-lab-section">
              <h3>{tr("照着做：每一步都告诉你应看到什么")}</h3>
              <div className="guided-lab-steps">
                {workbook.lab.steps.map((step, stepIndex) => (
                  <article className="guided-lab-step" key={step.title}>
                    <i>{stepIndex + 1}</i>
                    <div><strong>{step.title}</strong><p><b>{tr("怎么做：")}</b>{step.action}</p><p className="expected"><b>{tr("预期：")}</b>{step.expected}</p></div>
                  </article>
                ))}
              </div>
              <div className="lab-command"><span>{tr("在项目根目录运行")}</span><code>{workbook.lab.command}</code></div>
            </div>

            <div className="guided-lab-section">
              <h3>{tr("代码逐段解读：不是复制粘贴就结束")}</h3>
              <div className="code-walkthrough">
                {workbook.lab.codeWalkthrough.map((item, itemIndex) => (
                  <article key={item.code}>
                    <span>{tr("代码")} {itemIndex + 1}</span>
                    <code>{item.code}</code>
                    <p>{item.explanation}</p>
                  </article>
                ))}
              </div>
            </div>

            <div className="lab-result-grid">
              <article>
                <h3>{tr("预期输出")}</h3>
                <pre>{workbook.lab.expectedOutput.join('\n')}</pre>
              </article>
              <article>
                <h3>{tr("怎样确认自己真的学会了")}</h3>
                {workbook.lab.verification.map((item) => <p key={item}><CheckCircle2 size={15} />{item}</p>)}
              </article>
            </div>
          </section>
        )}

        {workbook && (
          <section className="panel public-reading-panel">
            <div className="panel-head">
              <div><span className="section-kicker">PUBLIC SOURCES & PRACTITIONER NOTES</span><h2><Quote size={19} /> {tr("公开教程、论文与从业经验")}</h2></div>
            </div>
            <p className="source-disclaimer">{tr("以下内容只做原文观点摘要，并提供可追溯链接；从业者经验不是事实定律，更不是荐股或收益承诺。")}</p>
            <div className="public-reading-grid">
              {workbook.readings.map((item) => (
                <a href={item.url} target="_blank" rel="noreferrer" key={item.url}>
                  <span>{item.kind}</span>
                  <strong>{item.title}</strong>
                  <small>{item.provider}</small>
                  <p>{item.takeaway}</p>
                  <i>{tr("打开原文")} <ExternalLink size={13} /></i>
                </a>
              ))}
            </div>
          </section>
        )}

        <section className="concept-reading-grid compact">
          <article className="panel project-map concept-downloads">
            <div className="panel-head">
              <div><span className="section-kicker">DOWNLOAD SOURCE</span><h2>{tr("下载对应项目文件")}</h2></div>
              <Download size={19} />
            </div>
            <div>
              {chapter.projectFiles.map((file) => (
                <a href={downloadUrl(file.path)} download key={file.path}>
                  <FileCode2 size={15} />
                  <p><code>{file.path}</code><span>{file.reason}</span></p>
                  <Download size={14} />
                </a>
              ))}
              <a href={downloadUrl(chapter.demo.file)} download>
                <Beaker size={15} />
                <p><code>{chapter.demo.file}</code><span>{tr("本章可直接运行的教学 Demo")}</span></p>
                <Download size={14} />
              </a>
            </div>
          </article>

          <article className="panel resource-panel concept-resources">
            <div className="panel-head">
              <div><span className="section-kicker">OFFICIAL REFERENCES</span><h2>{tr("继续阅读")}</h2></div>
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
          </article>
        </section>

        <footer className="chapter-pager concept-pager">
          {previous !== null
            ? <Link className="button" to={`/learn/${chapter.id}/concepts/${previous}`}><ArrowLeft size={15} /> {tr("上一个知识点")}</Link>
            : <Link className="button" to={`/learn/${chapter.id}`}><ArrowLeft size={15} /> {tr("返回章节")}</Link>}
          {next !== null
            ? <Link className="button primary" to={`/learn/${chapter.id}/concepts/${next}`}>{tr("下一个知识点")} <ArrowRight size={15} /></Link>
            : <Link className="button primary" to={`/learn/${chapter.id}`}>{tr("回到清单与测验")} <ArrowRight size={15} /></Link>}
        </footer>
      </main>
    </div>
  )
}

function downloadUrl(path: string): string {
  const encoded = path.split('/').map(encodeURIComponent).join('/')
  return apiUrl(`/learning/files/${encoded}`)
}
