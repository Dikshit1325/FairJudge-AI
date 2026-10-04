import type { EvaluationCriterion } from '../types/evaluation'
import EvidenceList from './EvidenceList'
import MissingEvidence from './MissingEvidence'
import ScoreCard from './ScoreCard'

export default function CriterionCard({ item }: { item: EvaluationCriterion }) {
  return <article className="criterion-card"><div className="criterion-head"><div><span className="eyebrow">Criterion</span><h3>{item.criterion}</h3></div><ScoreCard score={item.score} max={item.max_score} label="Score"/></div><div className="criterion-columns"><section><h4>Supporting evidence</h4><EvidenceList items={item.evidence}/></section><section><h4>Missing evidence</h4><MissingEvidence items={item.missing_evidence}/></section></div><div className="reasoning"><h4>Reasoning</h4><p>{item.reasoning}</p>{item.confidence !== undefined && <span className="confidence">Confidence {Math.round(item.confidence * 100)}%</span>}</div></article>
}
