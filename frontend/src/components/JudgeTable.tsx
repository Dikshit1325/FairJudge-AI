import type { DisagreementResponse } from '../types/evaluation'

export default function JudgeTable({ data }: { data: DisagreementResponse }) {
  return <div className="table-wrap" role="region" aria-label="Judge score comparison" tabIndex={0}><table><thead><tr><th scope="col">Criterion</th>{data.judge_totals.map(j => <th scope="col" key={j.judge_id}>{j.judge_name || j.judge_id}</th>)}</tr></thead><tbody>{data.criteria.map(c => <tr key={c.criterion}><th scope="row">{c.criterion}</th>{data.judge_totals.map(j => { const score = c.scores.find(s => s.judge_id === j.judge_id); return <td key={j.judge_id}>{score?.score ?? '—'} <span className="table-max">/ {c.max_score}</span></td> })}</tr>)}<tr className="total-row"><th scope="row">Total</th>{data.judge_totals.map(j => <td key={j.judge_id}>{j.total_score} <span className="table-max">/ {j.max_score}</span></td>)}</tr></tbody></table></div>
}
