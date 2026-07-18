import {
  ArrowRight,
  BookOpenCheck,
  CheckCircle2,
  Clock3,
  Code2,
  FlaskConical,
  GraduationCap,
  RotateCcw,
  Route,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { PageHeader } from '../components/PageHeader'
import {
  learningChapters,
  learningStages,
  totalChecklistItems,
} from '../learning/curriculum'
import { useLearningProgress } from '../learning/useLearningProgress'

const glossary = [
  {
    term: '量化研究',
    definition: '把投资假设写成数据、规则和实验，用可重复证据判断它是否值得继续。',
  },
  {
    term: 'AI 量化',
    definition: '用 AI 辅助开发、处理文本或建模；AI 是工具和因子来源，不是收益保证。',
  },
  {
    term: 'Web3',
    definition: '围绕区块链、链上资产和去中心化协议的技术生态，与量化是不同维度。',
  },
  {
    term: '可信回测',
    definition: '严格遵守信息可得时间、执行延迟、成本和独立样本外验证的历史模拟。',
  },
]

export function LearningHome() {
  const {
    summary,
    chapterCompleted,
    resetProgress,
  } = useLearningProgress()

  const handleReset = () => {
    if (window.confirm('确定清空全部学习 Checklist 和测验成绩吗？')) {
      resetProgress()
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Quant learning academy"
        title="从工程师到量化研究者"
        description="为有 Java、JavaScript 和科研计算背景的开发者设计：五个阶段、十个章节，从 Python 时间序列到舆情因子、可信回测和毕业研究。"
        actions={(
          <>
            <button className="button" onClick={handleReset}>
              <RotateCcw size={15} /> 重置进度
            </button>
            <Link className="button primary" to={`/learn/${learningChapters[0].id}`}>
              开始第一章 <ArrowRight size={15} />
            </Link>
          </>
        )}
      />

      <section className="learning-hero panel">
        <div className="learning-hero-copy">
          <span className="section-kicker">YOUR STARTING POINT</span>
          <h2>你不是编程小白，需要补的是科学 Python 与量化研究范式</h2>
          <p>
            九年 Java / JS 经验让你已经具备架构、测试和工程能力；物理海洋学训练则对应时间序列、
            数值计算和科研方法。本路线会快速略过通用编程常识，重点解决 pandas 对齐、信息时点、
            回测偏差、舆情结构化和样本外验证。
          </p>
          <div className="persona-tags">
            <span>Java → FastAPI / SQLAlchemy</span>
            <span>JavaScript → React 已熟悉</span>
            <span>MATLAB → NumPy / pandas</span>
            <span>科研训练 → 可证伪实验</span>
          </div>
        </div>
        <div className="learning-progress-orbit">
          <div className="progress-ring" style={{ '--progress': `${summary.percent * 3.6}deg` } as React.CSSProperties}>
            <div><strong>{summary.percent}%</strong><span>总进度</span></div>
          </div>
          <div className="learning-progress-meta">
            <span><b>{summary.completedChecklist}</b> / {totalChecklistItems} Checklist</span>
            <span><b>{summary.passedQuizzes}</b> / {learningChapters.length} 测验通过</span>
          </div>
        </div>
      </section>

      <section className="learning-stat-grid">
        {[
          { icon: Route, label: '学习阶段', value: '5', note: '基础到成果' },
          { icon: BookOpenCheck, label: '核心章节', value: '10', note: '每章独立子页面' },
          { icon: CheckCircle2, label: '行动清单', value: String(totalChecklistItems), note: '本地保存进度' },
          { icon: Clock3, label: '建议节奏', value: '8–10', note: '周 · 每周 5–8 小时' },
        ].map(({ icon: Icon, label, value, note }) => (
          <article className="panel learning-stat" key={label}>
            <Icon size={19} />
            <span>{label}</span>
            <strong>{value}</strong>
            <small>{note}</small>
          </article>
        ))}
      </section>

      <section className="learning-section-head">
        <div>
          <span className="section-kicker">FIVE-STAGE ROADMAP</span>
          <h2>进阶训练 1 → 2 → 3 → 4 → 5</h2>
        </div>
        <p>每阶段两章。先建立概念与数据基础，再做策略，最后加入 AI 和工程化。</p>
      </section>

      <section className="stage-roadmap">
        {learningStages.map((stage) => {
          const chapters = learningChapters.filter((chapter) => chapter.stage === stage.id)
          const stageTotal = chapters.reduce((total, chapter) => total + chapter.checklist.length, 0)
          const stageDone = chapters.reduce(
            (total, chapter) => total + chapterCompleted(chapter.id),
            0,
          )
          const stagePercent = Math.round((stageDone / stageTotal) * 100)
          return (
            <article className="stage-card panel" key={stage.id}>
              <div className="stage-number">{String(stage.id).padStart(2, '0')}</div>
              <div className="stage-card-head">
                <span>阶段 {stage.id}</span>
                <b>{stagePercent}%</b>
              </div>
              <h3>{stage.title}</h3>
              <strong>{stage.subtitle}</strong>
              <p>{stage.goal}</p>
              <div className="stage-progress"><i style={{ width: `${stagePercent}%` }} /></div>
              <div className="stage-chapters">
                {chapters.map((chapter) => {
                  const done = chapterCompleted(chapter.id)
                  return (
                    <Link to={`/learn/${chapter.id}`} key={chapter.id}>
                      <span>{String(chapter.order).padStart(2, '0')}</span>
                      <div><strong>{chapter.title}</strong><small>{done}/{chapter.checklist.length} 已完成</small></div>
                      <ArrowRight size={14} />
                    </Link>
                  )
                })}
              </div>
            </article>
          )
        })}
      </section>

      <section className="learning-bottom-grid">
        <article className="panel glossary-panel">
          <div className="panel-head">
            <div><span className="section-kicker">FIRST PRINCIPLES</span><h2>开始前先分清四个词</h2></div>
          </div>
          <div className="glossary-grid">
            {glossary.map((item) => (
              <div key={item.term}><strong>{item.term}</strong><p>{item.definition}</p></div>
            ))}
          </div>
        </article>

        <article className="panel outcome-panel">
          <GraduationCap size={27} />
          <span className="section-kicker">FINAL OUTCOME</span>
          <h2>最终成果：一份可信的双因子研究</h2>
          <p>
            用真实日历、点时财务、指数基准和新闻情绪完成策略；扣除成本，运行 Walk-forward，
            写出能复现、能被否定、明确列出局限的研究报告。
          </p>
          <div className="outcome-actions">
            <Link className="button" to="/learn/capstone"><FlaskConical size={15} /> 查看毕业要求</Link>
            <code><Code2 size={13} /> pwsh -File scripts\check.ps1</code>
          </div>
        </article>
      </section>
    </>
  )
}
