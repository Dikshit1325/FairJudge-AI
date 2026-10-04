export default function ScoreCard({ score, max, label = 'AI-assisted score' }: { score: number; max: number; label?: string }) {
  return <div className="score-card"><span className="eyebrow">{label}</span><div className="score-number">{score}<span> / {max}</span></div><div className="score-track" role="img" aria-label={`${score} out of ${max} points`}><span style={{ width: `${max ? Math.min(score / max * 100, 100) : 0}%` }}/></div></div>
}
