"""Orchestrates prompt construction, Ollama generation, and validation."""

from pydantic import BaseModel, ConfigDict, ValidationError

from .models import EvaluationCriterion, ProjectSubmission, RubricCriterion
from .ollama_client import generate_structured
from .prompts import build_evaluation_prompt
from .scoring import (
    EvaluationValidationError,
    build_evaluation_response,
    validate_evidence_quotes,
    validate_scores,
)


class MalformedEvaluationError(RuntimeError):
    """Generated evaluation cannot be safely parsed or validated."""


class ModelOutput(BaseModel):
    """Criterion-only model output; final totals are never model supplied."""

    model_config = ConfigDict(extra="forbid")
    criteria: list[EvaluationCriterion]


def evaluate_project(rubric: list[RubricCriterion], submission: ProjectSubmission):
    evidence_fields = (
        submission.problem_statement,
        submission.solution_description,
        submission.technical_details,
        submission.presentation_text,
        submission.other_information,
    )
    if not any(value and str(value).strip() for value in evidence_fields):
        # With no evaluable submission material, avoid prompting a model that
        # could hallucinate to fill the empty record. This is still a validated
        # evaluation: Python reports no supported points and requests review.
        missing = ["Insufficient evidence: no project details were supplied."]
        if submission.github_url:
            missing.append("GitHub evidence unavailable: the repository was not inspected.")
        if submission.demo_url:
            missing.append("Demo evidence unavailable: the demo was not inspected.")
        empty_results = [EvaluationCriterion(
                criterion=item.criterion,
                score=0,
                max_score=item.max_score,
                evidence=[],
                missing_evidence=missing.copy(),
                reasoning="No project details were supplied for this criterion; a human judge must review it.",
                confidence=0.0,
            ) for item in rubric]
        return build_evaluation_response(submission.project_name, empty_results, rubric)

    # The Ollama schema contains only criterion-level fields; totals and review
    # flags are always constructed by Python.
    prompt = build_evaluation_prompt(rubric, submission)
    raw = generate_structured(prompt, ModelOutput)
    try:
        parsed = ModelOutput.model_validate_json(raw)
    except (ValidationError, ValueError) as exc:
        raise MalformedEvaluationError("Ollama returned malformed or invalid evaluation JSON.") from exc
    try:
        validate_scores(parsed.criteria, rubric)
        validate_evidence_quotes(parsed.criteria, submission)
    except EvaluationValidationError as exc:
        raise MalformedEvaluationError(str(exc)) from exc

    rubric_order = {item.criterion.casefold(): index for index, item in enumerate(rubric)}
    criteria = sorted(parsed.criteria, key=lambda item: rubric_order[item.criterion.casefold()])
    return build_evaluation_response(submission.project_name, criteria, rubric)
