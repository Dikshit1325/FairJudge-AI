import { useState } from 'react'
import demoRequest from '../../../tests/fixtures/phase2_demo.json'
import { analyzeDisagreement } from '../lib/api'
import type { DisagreementRequest, DisagreementResponse } from '../types/evaluation'
import Disclaimer from '../components/Disclaimer'
import ReviewBanner from '../components/ReviewBanner'
import LoadingState from '../components/LoadingState'
import JudgeTable from '../components/JudgeTable'
import DisagreementCard from '../components/DisagreementCard'

const serializedDemo = JSON.stringify(demoRequest, null, 2)

export default function JudgeComparison() {
  const [input, setInput] = useState(serializedDemo)
  const [result, setResult] = useState<DisagreementResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [isDemo, setIsDemo] = useState(true)
  const run = async (payload = input, demo = false) => {
    setError(''); setResult(null); setLoading(true); setIsDemo(demo)
    try { const parsed = JSON.parse(payload) as DisagreementRequest; setResult(await analyzeDisagreement(parsed)) }
    catch (err) { setError(err instanceof SyntaxError ? 'The request must be valid JSON.' : err instanceof Error ? err.message : 'Judge comparison could not be completed.') }
    finally { setLoading(false) }
  }
  const runDemo = () => { setInput(serializedDemo); void run(serializedDemo, true) }
  return <main className="page-shell"><div className="page-heading"><div><span className="eyebrow">PHASE 2 · CONSISTENCY & DISAGREEMENT</span><h1>Compare judges</h1><p>See where scores differ, inspect the evidence, and decide what needs human review.</p></div><button className="button button-primary" onClick={runDemo}>Load Judge Disagreement Demo <span aria-hidden="true">→</span></button></div><Disclaimer/>{isDemo && <div className="demo-label"><span className="demo-icon">D</span><div><strong>Fictional demonstration dataset</strong><p>These judges and scores are created for a demo. They are not Byte the Vibe judge scores.</p></div><span className="snapshot-pill fictional-pill">FICTIONAL</span></div>}<section className="comparison-input"><div className="form-heading"><div><span className="eyebrow">ANALYSIS INPUT</span><h2>Shared rubric & judge scores</h2><p>Use the fictional dataset or paste a request matching the backend schema.</p></div></div><label htmlFor="comparison-json">Disagreement request JSON</label><textarea id="comparison-json" className="json-input" rows={14} spellCheck={false} value={input} onChange={e=>{setInput(e.target.value);setIsDemo(false)}}/><div className="form-actions"><button className="button button-secondary" onClick={runDemo}>Reset fictional demo</button><button className="button button-primary" onClick={()=>void run(input,false)} disabled={loading}>Analyze disagreement <span aria-hidden="true">→</span></button></div></section>{loading && <LoadingState label="Comparing judge evaluations..."/>}{error && <div className="error-card" role="alert"><strong>Comparison could not be completed</strong><p>{error}</p><button className="button button-secondary" onClick={()=>void run(input,isDemo)}>Retry analysis</button></div>}{result && <section className="result-section" aria-live="polite"><div className="result-top"><div><span className="eyebrow">{isDemo ? 'FICTIONAL DEMONSTRATION' : 'JUDGE COMPARISON'}</span><h2>{result.project_name}</h2><p>{result.judge_totals.length} judges · maximum possible {result.maximum_possible_total_score} points · total range {result.total_score_range}</p></div><span className={`validation-pill ${result.validation_status==='VALIDATED'?'validated':'fallback'}`}>{result.validation_status==='VALIDATED'?'Explanation validated':'Safe fallback used'}</span></div>{result.human_review_required && <ReviewBanner detail="Review the evidence and rubric interpretation before making a final decision."/>}<h3 className="subsection-title">Score comparison</h3><JudgeTable data={result}/><h3 className="subsection-title disagreement-subhead">Criterion disagreement <span>Expand a criterion to inspect each judge’s evidence and reasoning.</span></h3><div className="disagreement-list">{result.criteria.map(item=><DisagreementCard item={item} key={item.criterion}/>)}</div><div className="result-note"><span aria-hidden="true">i</span>Disagreement is a signal for review, not proof that a judge is incorrect.</div></section>}</main>
}
