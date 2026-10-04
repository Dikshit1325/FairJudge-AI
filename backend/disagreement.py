"""Deterministic judge disagreement statistics and evidence-checked explanations."""

from statistics import median
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .models import (
    AttributedQuote, DisagreementCriterionResult, DisagreementRequest,
    DisagreementResponse, JudgeCriterionScore, JudgeTotal,
)
from .ollama_client import generate_structured
from .prompts import build_disagreement_prompt

LOW_DISAGREEMENT_PERCENT = 0.10
MODERATE_DISAGREEMENT_PERCENT = 0.25
SAFE_EXPLANATION = "Insufficient evidence to determine the reason for disagreement."


class ExplanationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    criterion: str
    explanation: str = Field(min_length=1)
    supporting_quotes: list[AttributedQuote]


class ExplanationOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    criteria: list[ExplanationItem]


def disagreement_level(score_range: int, max_score: int) -> tuple[float, Literal["LOW", "MODERATE", "HIGH"]]:
    percentage = score_range / max_score
    if percentage <= LOW_DISAGREEMENT_PERCENT:
        level = "LOW"
    elif percentage <= MODERATE_DISAGREEMENT_PERCENT:
        level = "MODERATE"
    else:
        level = "HIGH"
    return percentage, level


def _fallback_explanations(request: DisagreementRequest) -> dict[str, tuple[str, list[AttributedQuote]]]:
    return {item.criterion.casefold(): (SAFE_EXPLANATION, []) for item in request.rubric}


def _validated_explanations(request: DisagreementRequest) -> dict[str, tuple[str, list[AttributedQuote]]] | None:
    try:
        parsed = ExplanationOutput.model_validate_json(
            generate_structured(build_disagreement_prompt(request), ExplanationOutput)
        )
    except Exception:
        # Statistical analysis remains available even if local Ollama is offline
        # or returns content that fails schema validation.
        return None
    expected = {item.criterion.casefold() for item in request.rubric}
    actual = [item.criterion.casefold() for item in parsed.criteria]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        return None
    results = {}
    judge_by_id = {judge.judge_id.casefold(): judge for judge in request.judge_evaluations}
    for item in parsed.criteria:
        allowed: dict[str, set[str]] = {}
        for judge in request.judge_evaluations:
            evidence_key = next(k for k in judge.evidence if k.casefold() == item.criterion.casefold())
            reasoning_key = next(k for k in judge.reasoning if k.casefold() == item.criterion.casefold())
            allowed[judge.judge_id.casefold()] = set(judge.evidence[evidence_key]) | {judge.reasoning[reasoning_key]}
        if not item.supporting_quotes:
            return None
        for quote in item.supporting_quotes:
            judge = judge_by_id.get(quote.judge_id.casefold())
            if not judge or not quote.quote.strip() or not any(
                quote.quote in source for source in allowed[quote.judge_id.casefold()]
            ):
                return None
        results[item.criterion.casefold()] = (item.explanation, item.supporting_quotes)
    return results


def analyze_disagreement(request: DisagreementRequest) -> DisagreementResponse:
    explanations = _validated_explanations(request)
    safe = explanations is None
    if safe:
        explanations = _fallback_explanations(request)

    criterion_results = []
    for rubric_item in request.rubric:
        judge_scores = []
        values = []
        for judge in request.judge_evaluations:
            key = next(k for k in judge.scores if k.casefold() == rubric_item.criterion.casefold())
            evidence_key = next(k for k in judge.evidence if k.casefold() == rubric_item.criterion.casefold())
            reasoning_key = next(k for k in judge.reasoning if k.casefold() == rubric_item.criterion.casefold())
            confidence_key = next((k for k in judge.confidence if k.casefold() == rubric_item.criterion.casefold()), None)
            value = judge.scores[key]
            values.append(value)
            judge_scores.append(JudgeCriterionScore(
                judge_id=judge.judge_id, judge_name=judge.judge_name, score=value,
                evidence=judge.evidence[evidence_key], reasoning=judge.reasoning[reasoning_key],
                confidence=judge.confidence.get(confidence_key) if confidence_key else None,
            ))
        low, high = min(values), max(values)
        percentage, level = disagreement_level(high - low, rubric_item.max_score)
        explanation, quotes = explanations[rubric_item.criterion.casefold()]
        review = level != "LOW" or safe or any(not score.evidence for score in judge_scores)
        criterion_results.append(DisagreementCriterionResult(
            criterion=rubric_item.criterion, max_score=rubric_item.max_score,
            number_of_judges=len(values), scores=judge_scores,
            average_score=round(sum(values) / len(values), 4), minimum_score=low,
            maximum_score=high, score_range=high-low, median_score=float(median(values)),
            disagreement_percentage=round(percentage, 4), disagreement_level=level,
            human_review_required=review, explanation=explanation, supporting_quotes=quotes,
        ))

    rubric_max = sum(item.max_score for item in request.rubric)
    totals = [JudgeTotal(
        judge_id=judge.judge_id, judge_name=judge.judge_name,
        total_score=sum(judge.scores[next(k for k in judge.scores if k.casefold() == item.criterion.casefold())] for item in request.rubric),
        max_score=rubric_max,
    ) for judge in request.judge_evaluations]
    total_values = [item.total_score for item in totals]
    return DisagreementResponse(
        project_name=request.project_name, criteria=criterion_results, judge_totals=totals,
        maximum_possible_total_score=rubric_max, minimum_total_score=min(total_values),
        maximum_total_score=max(total_values), total_score_range=max(total_values)-min(total_values),
        human_review_required=any(item.human_review_required for item in criterion_results),
        validation_status="SAFE_FALLBACK_USED" if safe else "VALIDATED",
    )
