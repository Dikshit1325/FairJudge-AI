import json

import pytest

from backend import evaluator
from backend.evaluator import MalformedEvaluationError
from backend.models import ProjectSubmission, RubricCriterion
from backend.ollama_client import OllamaUnavailableError, generate_structured
from backend.scoring import EvaluationValidationError


RUBRIC = [RubricCriterion(criterion="Technical", max_score=10)]
SUBMISSION = ProjectSubmission(
    project_name="Example", problem_statement="Users need planning.",
    solution_description="A planning tool.", technical_details="FastAPI backend.",
)
GOOD = {"criteria": [{"criterion": "Technical", "score": 7, "max_score": 10,
                       "evidence": ["FastAPI backend."], "missing_evidence": [],
                       "reasoning": "A backend is identified, but detail is limited.", "confidence": 0.7}]}


def test_valid_evaluation_and_python_totals(monkeypatch):
    monkeypatch.setattr(evaluator, "generate_structured", lambda *_: json.dumps(GOOD))
    response = evaluator.evaluate_project(RUBRIC, SUBMISSION)
    assert response.total_score == 7
    assert response.max_score == 10


def test_arbitrary_rubric_is_used_not_greengrid_defaults(monkeypatch):
    custom_rubric = [RubricCriterion(criterion="Community Fit", max_score=7)]
    custom_result = {"criteria": [{**GOOD["criteria"][0], "criterion": "Community Fit",
                                    "score": 5, "max_score": 7}]}
    seen = {}

    def fake_generate(prompt, _model):
        seen["prompt"] = prompt
        return json.dumps(custom_result)

    monkeypatch.setattr(evaluator, "generate_structured", fake_generate)
    response = evaluator.evaluate_project(custom_rubric, SUBMISSION)
    assert response.criteria[0].criterion == "Community Fit"
    assert response.max_score == 7
    assert "Innovation" not in seen["prompt"]


def test_identity_metadata_is_not_sent_to_model(monkeypatch):
    submission = SUBMISSION.model_copy(update={
        "identity_information": ["Team identity: Northbridge University"],
    })
    seen = {}

    def fake_generate(prompt, _model):
        seen["prompt"] = prompt
        return json.dumps(GOOD)

    monkeypatch.setattr(evaluator, "generate_structured", fake_generate)
    evaluator.evaluate_project(RUBRIC, submission)
    assert "Northbridge University" not in seen["prompt"]
    assert "Ignore team names, colleges or universities" in seen["prompt"]


def test_unknown_criterion_is_rejected(monkeypatch):
    data = {"criteria": [{**GOOD["criteria"][0], "criterion": "Unlisted"}]}
    monkeypatch.setattr(evaluator, "generate_structured", lambda *_: json.dumps(data))
    with pytest.raises(MalformedEvaluationError):
        evaluator.evaluate_project(RUBRIC, SUBMISSION)


def test_unquoted_or_invented_evidence_is_rejected(monkeypatch):
    data = {"criteria": [{**GOOD["criteria"][0], "evidence": ["Automated testing passed."]}]}
    monkeypatch.setattr(evaluator, "generate_structured", lambda *_: json.dumps(data))
    with pytest.raises(MalformedEvaluationError, match="exact quote"):
        evaluator.evaluate_project(RUBRIC, SUBMISSION)


def test_missing_evidence_is_preserved(monkeypatch):
    data = {"criteria": [{**GOOD["criteria"][0], "evidence": [],
                           "missing_evidence": ["Insufficient evidence: test results were not supplied"],
                           "confidence": 0.3}]}
    monkeypatch.setattr(evaluator, "generate_structured", lambda *_: json.dumps(data))
    response = evaluator.evaluate_project(RUBRIC, SUBMISSION)
    assert response.human_review_required is True
    assert response.overall_missing_evidence


def test_empty_submission_returns_insufficient_evidence_without_model(monkeypatch):
    empty = ProjectSubmission(
        project_name="Empty", problem_statement="", solution_description="",
        technical_details="",
    )
    monkeypatch.setattr(
        evaluator, "generate_structured",
        lambda *_: pytest.fail("model should not be asked to invent evidence"),
    )
    result = evaluator.evaluate_project(RUBRIC, empty)
    assert result.total_score == 0
    assert result.max_score == 10
    assert result.human_review_required is True
    assert result.criteria[0].evidence == []
    assert "Insufficient evidence" in result.criteria[0].missing_evidence[0]


def test_uninspected_links_are_reported_as_unavailable(monkeypatch):
    linked_only = ProjectSubmission(
        project_name="Links Only", problem_statement="", solution_description="",
        technical_details="", github_url="https://github.com/example/project",
        demo_url="https://example.com/demo",
    )
    monkeypatch.setattr(
        evaluator, "generate_structured",
        lambda *_: pytest.fail("uninspected URLs must not be sent as project evidence"),
    )
    result = evaluator.evaluate_project(RUBRIC, linked_only)
    missing = " ".join(result.criteria[0].missing_evidence)
    assert "GitHub evidence unavailable" in missing
    assert "Demo evidence unavailable" in missing
    assert result.human_review_required is True


def test_malformed_json_fails_safely(monkeypatch):
    monkeypatch.setattr(evaluator, "generate_structured", lambda *_: "not JSON")
    with pytest.raises(MalformedEvaluationError):
        evaluator.evaluate_project(RUBRIC, SUBMISSION)


def test_ollama_unavailable_has_clear_error(monkeypatch):
    def fail(*_args, **_kwargs):
        raise OllamaUnavailableError("Ollama is unavailable. Start the local Ollama service.")
    monkeypatch.setattr(evaluator, "generate_structured", fail)
    with pytest.raises(OllamaUnavailableError, match="Start the local Ollama"):
        evaluator.evaluate_project(RUBRIC, SUBMISSION)


def test_ollama_client_extracts_response_from_envelope(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *_): pass
        def read(self): return b'{"response":"{\\"criteria\\":[]}"}'
    monkeypatch.setattr("backend.ollama_client.urlopen", lambda *_args, **_kwargs: Response())
    assert generate_structured("prompt", evaluator.ModelOutput) == '{"criteria":[]}'
