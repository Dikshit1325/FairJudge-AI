"""Pydantic contracts for the FairJudge evaluation API."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StrictInt, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RubricCriterion(StrictModel):
    criterion: str = Field(min_length=1)
    max_score: int = Field(ge=1)
    evaluation_guidance: str | None = None


class ProjectSubmission(StrictModel):
    project_name: str = Field(min_length=1)
    # Empty descriptions are allowed so judges can evaluate an incomplete
    # submission and receive explicit insufficient-evidence findings.
    problem_statement: str
    solution_description: str
    technical_details: str
    github_url: HttpUrl | None = None
    demo_url: HttpUrl | None = None
    presentation_text: str | None = None
    other_information: str | None = None
    future_improvements: list[str] = Field(default_factory=list)
    # Kept out of the evaluator prompt and allowed evidence source.
    identity_information: list[str] = Field(default_factory=list)


class EvaluationRequest(StrictModel):
    rubric: list[RubricCriterion] = Field(min_length=1)
    submission: ProjectSubmission

    @model_validator(mode="after")
    def unique_criteria(self):
        names = [item.criterion.casefold() for item in self.rubric]
        if len(names) != len(set(names)):
            raise ValueError("Rubric criterion names must be unique")
        return self


class EvaluationCriterion(StrictModel):
    criterion: str = Field(min_length=1)
    score: int = Field(ge=0)
    max_score: int = Field(ge=1)
    evidence: list[str]
    missing_evidence: list[str]
    reasoning: str = Field(min_length=1)
    confidence: Annotated[float, Field(ge=0, le=1)]

    @model_validator(mode="after")
    def score_within_maximum(self):
        if self.score > self.max_score:
            raise ValueError("score cannot exceed max_score")
        return self


class EvaluationResponse(StrictModel):
    project_name: str
    total_score: int = Field(ge=0)
    max_score: int = Field(ge=0)
    criteria: list[EvaluationCriterion]
    overall_missing_evidence: list[str]
    human_review_required: bool

    @model_validator(mode="after")
    def total_is_consistent(self):
        if self.total_score != sum(item.score for item in self.criteria):
            raise ValueError("total_score must equal the sum of criterion scores")
        if self.max_score != sum(item.max_score for item in self.criteria):
            raise ValueError("max_score must equal the sum of criterion maximums")
        if self.total_score > self.max_score:
            raise ValueError("total_score cannot exceed max_score")
        return self


class JudgeEvaluation(StrictModel):
    judge_id: str = Field(min_length=1)
    judge_name: str | None = None
    scores: dict[str, StrictInt]
    evidence: dict[str, list[str]]
    reasoning: dict[str, str]
    confidence: dict[str, Annotated[float, Field(ge=0, le=1)]] = Field(default_factory=dict)


class DisagreementRequest(StrictModel):
    project_name: str = Field(min_length=1)
    rubric: list[RubricCriterion] = Field(min_length=1)
    judge_evaluations: list[JudgeEvaluation] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_judges_and_criteria(self):
        criteria = [item.criterion.casefold() for item in self.rubric]
        if len(criteria) != len(set(criteria)):
            raise ValueError("Rubric criterion names must be unique")
        ids = [item.judge_id.casefold() for item in self.judge_evaluations]
        if any(not value.strip() for value in ids):
            raise ValueError("judge_id must not be empty")
        if len(ids) != len(set(ids)):
            raise ValueError("judge_id values must be unique")
        expected = set(criteria)
        for judge in self.judge_evaluations:
            for field_name, mapping in (("scores", judge.scores), ("evidence", judge.evidence), ("reasoning", judge.reasoning)):
                actual = {key.casefold() for key in mapping}
                if actual != expected:
                    raise ValueError(f"Judge '{judge.judge_id}' {field_name} must include exactly the rubric criteria")
                if len(actual) != len(mapping):
                    raise ValueError(f"Judge '{judge.judge_id}' {field_name} contains duplicate criterion names")
            if not set(key.casefold() for key in judge.confidence).issubset(expected):
                raise ValueError(f"Judge '{judge.judge_id}' confidence contains an unknown criterion")
            for rubric_item in self.rubric:
                score = judge.scores[next(k for k in judge.scores if k.casefold() == rubric_item.criterion.casefold())]
                if not 0 <= score <= rubric_item.max_score:
                    raise ValueError(f"Judge '{judge.judge_id}' score for '{rubric_item.criterion}' must be between 0 and {rubric_item.max_score}")
        return self


class JudgeCriterionScore(StrictModel):
    judge_id: str
    judge_name: str | None = None
    score: int
    evidence: list[str]
    reasoning: str
    confidence: float | None = None


class JudgeTotal(StrictModel):
    judge_id: str
    judge_name: str | None = None
    total_score: int
    max_score: int


class AttributedQuote(StrictModel):
    judge_id: str
    quote: str


class DisagreementCriterionResult(StrictModel):
    criterion: str
    max_score: int
    number_of_judges: int
    scores: list[JudgeCriterionScore]
    average_score: float
    minimum_score: int
    maximum_score: int
    score_range: int
    median_score: float
    disagreement_percentage: float
    disagreement_level: Literal["LOW", "MODERATE", "HIGH"]
    human_review_required: bool
    explanation: str
    supporting_quotes: list[AttributedQuote]


class DisagreementResponse(StrictModel):
    project_name: str
    criteria: list[DisagreementCriterionResult]
    judge_totals: list[JudgeTotal]
    maximum_possible_total_score: int
    minimum_total_score: int
    maximum_total_score: int
    total_score_range: int
    human_review_required: bool
    validation_status: Literal["VALIDATED", "SAFE_FALLBACK_USED"]
