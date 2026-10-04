import pytest
from pydantic import ValidationError

from backend.models import EvaluationCriterion, EvaluationResponse, RubricCriterion
from backend.scoring import (
    EvaluationValidationError, build_evaluation_response, calculate_max_score,
    calculate_total_score, collect_missing_evidence, requires_human_review,
    validate_scores,
)


def criterion(name="Innovation", score=17, max_score=20, **kwargs):
    values = {
        "criterion": name,
        "score": score,
        "max_score": max_score,
        "evidence": ["provided fact"],
        "missing_evidence": [],
        "reasoning": "The supplied fact supports this score.",
        "confidence": 0.9,
    }
    values.update(kwargs)
    return EvaluationCriterion(**values)


def test_python_calculates_total_and_maximum():
    results = [criterion(), criterion("Impact", 22, 25)]
    rubric = [RubricCriterion(criterion="Innovation", max_score=20),
              RubricCriterion(criterion="Impact", max_score=25)]
    assert calculate_total_score(results) == 39
    assert calculate_max_score(rubric) == 45
    response = build_evaluation_response("Project", results, rubric)
    assert response.total_score == 39
    assert response.max_score == 45


def test_unknown_criterion_is_rejected():
    with pytest.raises(EvaluationValidationError):
        validate_scores([criterion("Surprise", 1, 2)], [RubricCriterion(criterion="Innovation", max_score=20)])


def test_max_score_must_match_rubric():
    with pytest.raises(EvaluationValidationError):
        validate_scores([criterion("Innovation", 1, 19)], [RubricCriterion(criterion="Innovation", max_score=20)])


def test_score_cannot_exceed_actual_rubric_maximum():
    # The model's own maximum is internally valid, but does not match the
    # actual supplied criterion maximum; backend validation rejects it.
    with pytest.raises(EvaluationValidationError, match="must match the supplied rubric"):
        validate_scores(
            [criterion("Innovation", 15, 25)],
            [RubricCriterion(criterion="Innovation", max_score=10)],
        )


def test_incomplete_evidence_sets_review_and_is_reported():
    result = criterion(missing_evidence=["Insufficient evidence: measured outcomes were not supplied"], confidence=0.4)
    assert requires_human_review([result]) is True
    assert collect_missing_evidence([result]) == ["Innovation: Insufficient evidence: measured outcomes were not supplied"]


def test_inconsistent_or_over_max_total_is_rejected():
    with pytest.raises(ValidationError):
        EvaluationResponse(project_name="P", total_score=40, max_score=20,
                           criteria=[criterion()], overall_missing_evidence=[], human_review_required=False)
