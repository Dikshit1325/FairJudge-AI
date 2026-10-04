import type { DisagreementRequest, DisagreementResponse, EvaluationRequest, EvaluationResponse } from '../types/evaluation'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try { response = await fetch(`/api${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } }) }
  catch { throw new Error('Unable to connect to FairJudge backend. Make sure the FastAPI server is running.') }
  if (!response.ok) {
    let message = `Request failed (${response.status}). Please review the submitted information and try again.`
    try {
      const body = await response.json()
      if (typeof body.detail === 'string') message = body.detail
      else if (Array.isArray(body.detail)) message = body.detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join('; ') || message
    } catch { /* Keep the safe status message for non-JSON errors. */ }
    throw new Error(message)
  }
  try { return await response.json() as T }
  catch { throw new Error('The backend returned an unreadable response. Please try again.') }
}

export const checkHealth = () => request<{ status: string }>('/health')
export const evaluateProject = (body: EvaluationRequest) => request<EvaluationResponse>('/evaluate', { method: 'POST', body: JSON.stringify(body) })
export const analyzeDisagreement = (body: DisagreementRequest) => request<DisagreementResponse>('/analyze-disagreement', { method: 'POST', body: JSON.stringify(body) })
