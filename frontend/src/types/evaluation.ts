export interface RubricCriterion { criterion: string; max_score: number; evaluation_guidance?: string | null }
export interface ProjectSubmission {
  project_name: string; problem_statement: string; solution_description: string; technical_details: string;
  github_url?: string | null; demo_url?: string | null; presentation_text?: string | null;
  other_information?: string | null; future_improvements?: string[]; identity_information?: string[];
}
export interface EvaluationRequest { rubric: RubricCriterion[]; submission: ProjectSubmission }
export interface EvaluationCriterion {
  criterion: string; score: number; max_score: number; evidence: string[]; missing_evidence: string[];
  reasoning: string; confidence?: number;
}
export interface EvaluationResponse {
  project_name: string; total_score: number; max_score: number; criteria: EvaluationCriterion[];
  overall_missing_evidence: string[]; human_review_required: boolean;
}
export interface JudgeEvaluation {
  judge_id: string; judge_name?: string | null; scores: Record<string, number>;
  evidence: Record<string, string[]>; reasoning: Record<string, string>; confidence?: Record<string, number>;
}
export interface DisagreementRequest { project_name: string; rubric: RubricCriterion[]; judge_evaluations: JudgeEvaluation[] }
export interface JudgeCriterionScore {
  judge_id: string; judge_name?: string | null; score: number; evidence: string[];
  reasoning: string; confidence?: number | null;
}
export interface JudgeTotal { judge_id: string; judge_name?: string | null; total_score: number; max_score: number }
export interface AttributedQuote { judge_id: string; quote: string }
export interface DisagreementCriterionResult {
  criterion: string; max_score: number; number_of_judges: number; scores: JudgeCriterionScore[];
  average_score: number; minimum_score: number; maximum_score: number; score_range: number;
  median_score: number; disagreement_percentage: number; disagreement_level: 'LOW' | 'MODERATE' | 'HIGH';
  human_review_required: boolean; explanation: string; supporting_quotes: AttributedQuote[];
}
export interface DisagreementResponse {
  project_name: string; criteria: DisagreementCriterionResult[]; judge_totals: JudgeTotal[];
  maximum_possible_total_score: number; minimum_total_score: number; maximum_total_score: number;
  total_score_range: number; human_review_required: boolean; validation_status: 'VALIDATED' | 'SAFE_FALLBACK_USED';
}
