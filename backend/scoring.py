"""Deterministic score and human-review calculations."""

from .models import EvaluationCriterion, EvaluationResponse, ProjectSubmission, RubricCriterion


class EvaluationValidationError(ValueError):
    """Generated evaluation does not match the request or evidence source."""


LOW_CONFIDENCE_THRESHOLD = 0.60


def validate_scores(criteria: list[EvaluationCriterion], rubric: list[RubricCriterion]) -> None:
    expected = {item.criterion.casefold(): item for item in rubric}
    actual = [item.criterion.casefold() for item in criteria]
    if len(actual) != len(set(actual)):
        raise EvaluationValidationError("LLM returned a criterion more than once")
    if set(actual) != set(expected):
        unknown = sorted(set(actual) - set(expected))
        missing = sorted(set(expected) - set(actual))
        raise EvaluationValidationError(
            f"LLM criteria do not match rubric (unknown={unknown}, missing={missing})"
        )
    for result in criteria:
        supplied = expected[result.criterion.casefold()]
        if result.max_score != supplied.max_score:
            raise EvaluationValidationError(
                f"max_score for '{result.criterion}' must match the supplied rubric"
            )
        if not 0 <= result.score <= supplied.max_score:
            raise EvaluationValidationError(f"score for '{result.criterion}' is outside its allowed range")


def validate_evidence_quotes(criteria: list[EvaluationCriterion], submission: ProjectSubmission) -> None:
    submitted_facts = (
        submission.problem_statement,
        submission.solution_description,
        submission.technical_details,
        submission.presentation_text,
        submission.other_information,
        # Future items are visible to the model so it can avoid treating them
        # as implemented, but they can never serve as score evidence.
    )
    source = "\n".join(
        value for value in submitted_facts if isinstance(value, str) and value.strip()
    )
    for result in criteria:
        for quote in result.evidence:
            if not quote.strip() or quote not in source:
                raise EvaluationValidationError(
                    f"Evidence for '{result.criterion}' must be an exact quote from the submission"
                )


def calculate_total_score(criteria: list[EvaluationCriterion]) -> int:
    return sum(item.score for item in criteria)


def calculate_max_score(rubric: list[RubricCriterion]) -> int:
    return sum(item.max_score for item in rubric)


def collect_missing_evidence(criteria: list[EvaluationCriterion]) -> list[str]:
    collected: list[str] = []
    for item in criteria:
        for missing in item.missing_evidence:
            detail = f"{item.criterion}: {missing}"
            if detail not in collected:
                collected.append(detail)
    return collected


def requires_human_review(criteria: list[EvaluationCriterion]) -> bool:
    return any(
        item.missing_evidence
        or item.confidence < LOW_CONFIDENCE_THRESHOLD
        or not item.evidence
        for item in criteria
    )


def build_evaluation_response(project_name, criteria, rubric) -> EvaluationResponse:
    return EvaluationResponse(
        project_name=project_name,
        total_score=calculate_total_score(criteria),
        max_score=calculate_max_score(rubric),
        criteria=criteria,
        overall_missing_evidence=collect_missing_evidence(criteria),
        human_review_required=requires_human_review(criteria),
    )
