import pytest
from pydantic import ValidationError

from backend.models import EvaluationCriterion, EvaluationRequest, ProjectSubmission, RubricCriterion


def test_valid_rubric_and_submission():
    request = EvaluationRequest(
        rubric=[RubricCriterion(criterion="Innovation", max_score=20)],
        submission=ProjectSubmission(
            project_name="Example", problem_statement="Problem", solution_description="Solution",
            technical_details="Python backend", github_url=None, demo_url=None,
            presentation_text="Pitch",
        ),
    )
    assert request.rubric[0].max_score == 20


def test_incomplete_submission_can_leave_evidence_fields_empty():
    submission = ProjectSubmission(
        project_name="Incomplete", problem_statement="", solution_description="",
        technical_details="",
    )
    assert submission.technical_details == ""


def test_rubric_maximum_is_required():
    with pytest.raises(ValidationError):
        RubricCriterion.model_validate({"criterion": "Actual Criterion"})


def test_rubric_guidance_does_not_create_additional_criteria():
    criterion = RubricCriterion(
        criterion="Impact", max_score=20,
        evaluation_guidance="Assess only the stated impact evidence.",
    )
    assert criterion.criterion == "Impact"
    assert criterion.max_score == 20


def test_score_cannot_exceed_maximum():
    with pytest.raises(ValidationError):
        EvaluationCriterion(
            criterion="Innovation", score=21, max_score=20, evidence=[],
            missing_evidence=[], reasoning="Reason", confidence=0.8,
        )


def test_negative_score_is_rejected():
    with pytest.raises(ValidationError):
        EvaluationCriterion(
            criterion="Innovation", score=-1, max_score=20, evidence=[],
            missing_evidence=[], reasoning="Reason", confidence=0.8,
        )


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_invalid_confidence_is_rejected(confidence):
    with pytest.raises(ValidationError):
        EvaluationCriterion(
            criterion="Innovation", score=1, max_score=20, evidence=[],
            missing_evidence=[], reasoning="Reason", confidence=confidence,
        )
