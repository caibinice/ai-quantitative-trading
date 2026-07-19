import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Beaker,
  BookOpen,
  CheckCircle2,
  Download,
  ExternalLink,
  FileCode2,
  GitBranch,
  Lightbulb,
  ListChecks,
} from 'lucide-react'
import { Link, Navigate, useParams } from 'react-router-dom'
import { apiUrl } from '../api'
import { conceptLessons, lessonKey } from '../learning/conceptLessons'
import { chapterById } from '../learning/curriculum'

export function LearningConceptDetail() {
  const { chapterId = '', conceptIndex = '' } = useParams()
  const chapter = chapterById[chapterId]
  const index = Number(conceptIndex)
  const concept = chapter?.concepts[index]
  const lesson = conceptLessons[lessonKey(chapterId, index)]

  if (!chapter || !concept || !lesson || !Number.isInteger(index)) {
    return <Navigate to={chapter ? `/learn/${chapter.id}` : '/learn'} replace />
  }

  const previous = index > 0 ? index - 1 : null
  const next = index < chapter.concepts.length - 1 ? index + 1 : null

  return (
    <div className="concept-detail-page">
      <aside className="panel concept-detail-nav">
        <Link className="chapter-home-link" to={`/learn/${chapter.id}`}>
          <ArrowLeft size={14} /> 返回第 {chapter.order} 章
        </Link>
        <div className="concept-detail-nav-title">
          <span>本章知识点</span>
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
          <span>先读心智模型，再沿流程图理解信息怎样在系统中流动。</span>
        </div>
      </aside>

      <main className="concept-detail-content">
        <header className="panel concept-detail-hero">
          <div className="chapter-breadcrumb">
            学习学院 / 第 {chapter.order} 章 / 知识点 {index + 1}
          </div>
          <span className="section-kicker">DEEP DIVE LESSON</span>
          <h1>{concept.title}</h1>
          <p>{concept.summary}</p>
          <div className="concept-hero-tags">
            <span><BookOpen size={14} /> 详解</span>
            <span><GitBranch size={14} /> 项目映射</span>
            <span><Beaker size={14} /> 动手练习</span>
          </div>
        </header>

        <section className="panel mental-model">
          <Lightbulb size={22} />
          <div><span>先建立心智模型</span><p>{lesson.mentalModel}</p></div>
        </section>

        <section className="concept-reading-grid">
          <article className="panel concept-prose">
            <span className="section-kicker">CORE EXPLANATION</span>
            <h2>把概念讲透</h2>
            {lesson.deepDive.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
            <div className="concept-key-points">
              <strong>读完先记住</strong>
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

        <section className="concept-reading-grid compact">
          <article className="panel concept-list-card pitfall">
            <div className="panel-head">
              <div><span className="section-kicker">COMMON PITFALLS</span><h2>常见误区</h2></div>
              <AlertTriangle size={20} />
            </div>
            {lesson.pitfalls.map((item) => <p key={item}><span>!</span>{item}</p>)}
          </article>
          <article className="panel concept-list-card practice">
            <div className="panel-head">
              <div><span className="section-kicker">PRACTICE</span><h2>马上动手</h2></div>
              <ListChecks size={20} />
            </div>
            {lesson.practice.map((item, itemIndex) => (
              <p key={item}><span>{itemIndex + 1}</span>{item}</p>
            ))}
          </article>
        </section>

        <section className="concept-reading-grid compact">
          <article className="panel project-map concept-downloads">
            <div className="panel-head">
              <div><span className="section-kicker">DOWNLOAD SOURCE</span><h2>下载对应项目文件</h2></div>
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
                <p><code>{chapter.demo.file}</code><span>本章可直接运行的教学 Demo</span></p>
                <Download size={14} />
              </a>
            </div>
          </article>

          <article className="panel resource-panel concept-resources">
            <div className="panel-head">
              <div><span className="section-kicker">OFFICIAL REFERENCES</span><h2>继续阅读</h2></div>
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
            ? <Link className="button" to={`/learn/${chapter.id}/concepts/${previous}`}><ArrowLeft size={15} /> 上一个知识点</Link>
            : <Link className="button" to={`/learn/${chapter.id}`}><ArrowLeft size={15} /> 返回章节</Link>}
          {next !== null
            ? <Link className="button primary" to={`/learn/${chapter.id}/concepts/${next}`}>下一个知识点 <ArrowRight size={15} /></Link>
            : <Link className="button primary" to={`/learn/${chapter.id}`}>回到清单与测验 <ArrowRight size={15} /></Link>}
        </footer>
      </main>
    </div>
  )
}

function downloadUrl(path: string): string {
  const encoded = path.split('/').map(encodeURIComponent).join('/')
  return apiUrl(`/learning/files/${encoded}`)
}
