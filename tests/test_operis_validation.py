"""Regression coverage for the user-supplied Operis AI Phase 1.5 data."""

import json

import pytest

from backend import evaluator
from backend.evaluator import MalformedEvaluationError
from backend.models import EvaluationCriterion, ProjectSubmission, RubricCriterion
from backend.prompts import build_evaluation_prompt
from backend.scoring import validate_evidence_quotes


RUBRIC = [
    RubricCriterion(
        criterion="Innovation", max_score=20,
        evaluation_guidance=(
            "Consider the supplied combination of Chrome Extension, FastAPI, ML and React, "
            "real-time activity tracking, burnout prediction, productivity monitoring, dashboard, "
            "and stated problem. Do not assume novelty from AI/ML use. If uniqueness versus existing "
            "solutions cannot be established, state Insufficient evidence."
        ),
    ),
    RubricCriterion(
        criterion="Technical", max_score=30,
        evaluation_guidance=(
            "Assess only the described stack, architecture, endpoints, model, synthetic training data, "
            "features, deployment description and listed challenges solved. Do not claim model accuracy "
            "or production readiness. No ML performance metrics were supplied."
        ),
    ),
    RubricCriterion(
        criterion="Impact", max_score=20,
        evaluation_guidance=(
            "Assess the stated intended impact: organizational productivity monitoring, early burnout-risk "
            "detection, visualization and alerts. State Insufficient evidence for real-world impact; "
            "identify absent actual users, measured productivity improvement, measured burnout performance, "
            "organizational deployment, user feedback and quantitative outcomes."
        ),
    ),
]

SUBMISSION = ProjectSubmission(
    project_name="Operis AI",
    problem_statement="Burnout Prediction & Productivity Monitoring System.",
    solution_description=(
        "Operis-AI is a full-stack system that combines Machine Learning for burnout prediction, "
        "Chrome Extension for user activity tracking, FastAPI Backend for processing and APIs, "
        "and React Dashboard for real-time visualization. The system helps organizations monitor "
        "productivity and detect burnout risks early."
    ),
    technical_details=(
        "Frontend: React, Vite, Tailwind CSS, Recharts. Backend: FastAPI, Python, Joblib. "
        "Extension: Chrome Extension API, Manifest V3. Deployment: Frontend Netlify, Backend Render. "
        "Model: Logistic Regression. Training: Synthetic dataset. Features: hours_worked, "
        "meetings_count, sentiment, tasks_completed. POST /predict predicts burnout. GET /live "
        "gets real-time dashboard data. Architecture: Chrome Extension, FastAPI Backend, ML Model, "
        "React Dashboard. Features include real-time tracking of user activity, time spent, tasks, "
        "meetings and current working context/websites; burnout risk as Low / High; productivity score; "
        "real-time productivity trends, burnout distribution charts and alerts for high-risk users; "
        "dashboard updates every few seconds."
    ),
    github_url="https://github.com/Dikshit1325/OPERIS",
    other_information=(
        "Challenges solved: CORS issues between frontend, backend and extension; preflight OPTIONS "
        "request handling; real-time data syncing; deployment mismatches. The project structure "
        "describes backend/main.py, extension/background.js, extension/content.js, "
        "extension/manifest.json, ml/burnout_model.pkl, ml/train_model.py, src/pages, "
        "src/components, src/lib, and README.md."
    ),
    future_improvements=["Firebase integration for user storage", "Multi-user tracking"],
    identity_information=["GitHub username: Dikshit1325"],
)


def test_only_the_three_actual_criteria_and_maxima_are_used(monkeypatch):
    expected = {
        "criteria": [
            {"criterion": "Innovation", "score": 13, "max_score": 20,
             "evidence": ["Chrome Extension for user activity tracking"],
             "missing_evidence": ["Insufficient evidence to establish uniqueness compared with existing solutions."],
             "reasoning": "The submission combines a browser extension, API, ML model, and dashboard; uniqueness is not established.",
             "confidence": 0.72},
            {"criterion": "Technical", "score": 23, "max_score": 30,
             "evidence": ["Model: Logistic Regression."],
             "missing_evidence": ["Insufficient evidence: no ML performance metrics or test results were supplied."],
             "reasoning": "The submission describes the model and stack, but provides no performance validation.",
             "confidence": 0.78},
            {"criterion": "Impact", "score": 12, "max_score": 20,
             "evidence": ["The system helps organizations monitor productivity and detect burnout risks early."],
             "missing_evidence": ["Insufficient evidence: no real users or measured outcomes were supplied."],
             "reasoning": "The intended impact is stated, but real-world outcomes are not reported.",
             "confidence": 0.65},
        ]
    }
    captured = {}

    def fake_generate(prompt, _model):
        captured["prompt"] = prompt
        return json.dumps(expected)

    monkeypatch.setattr(evaluator, "generate_structured", fake_generate)
    result = evaluator.evaluate_project(RUBRIC, SUBMISSION)

    assert [item.criterion for item in result.criteria] == ["Innovation", "Technical", "Impact"]
    assert [item.max_score for item in result.criteria] == [20, 30, 20]
    assert result.max_score == 70
    assert result.total_score == 48
    assert result.total_score == sum(item.score for item in result.criteria)
    assert result.total_score <= result.max_score
    assert result.human_review_required is True
    assert "Innovation" in captured["prompt"] and "Technical" in captured["prompt"]
    assert "Impact" in captured["prompt"] and "Presentation" not in captured["prompt"]
    assert "GitHub evidence unavailable" in captured["prompt"]
    assert "No ML performance metrics were supplied" in captured["prompt"]
    assert "measured productivity improvement" in captured["prompt"]
    assert "Dikshit1325" not in captured["prompt"]


def test_future_improvement_cannot_be_used_as_evidence():
    future_claim = "Firebase integration for user storage"
    result = EvaluationCriterion(
        criterion="Technical", score=20, max_score=30, evidence=[future_claim],
        missing_evidence=[], reasoning="A future item was counted.", confidence=0.8,
    )
    with pytest.raises(ValueError, match="exact quote"):
        validate_evidence_quotes([result], SUBMISSION)


def test_real_submission_prompt_labels_future_items_as_unimplemented():
    prompt = build_evaluation_prompt(RUBRIC, SUBMISSION)
    assert "future_improvements are explicitly not implemented" in prompt
    assert "Firebase integration for user storage" in prompt
    assert "Multi-user tracking" in prompt
    assert "Do not assume an ML model is accurate" in prompt
    assert "Intended impact is not measured impact" in prompt


def test_unsupported_github_repository_claim_is_rejected(monkeypatch):
    unsupported = {
        "criteria": [
            {"criterion": name, "score": 1, "max_score": maximum,
             "evidence": ["The GitHub repository contains extensive unit tests."],
             "missing_evidence": [], "reasoning": "Claim based on an uninspected repository.",
             "confidence": 0.8}
            for name, maximum in (("Innovation", 20), ("Technical", 30), ("Impact", 20))
        ]
    }
    monkeypatch.setattr(evaluator, "generate_structured", lambda *_: json.dumps(unsupported))
    with pytest.raises(MalformedEvaluationError, match="exact quote"):
        evaluator.evaluate_project(RUBRIC, SUBMISSION)


@pytest.mark.parametrize(
    "criterion,maximum,unsupported_claim",
    [
        ("Technical", 30, "Model accuracy is 94%."),
        ("Impact", 20, "Productivity improved by 25%."),
    ],
)
def test_unprovided_ml_and_impact_metrics_are_rejected(criterion, maximum, unsupported_claim):
    result = EvaluationCriterion(
        criterion=criterion, score=1, max_score=maximum, evidence=[unsupported_claim],
        missing_evidence=[], reasoning="Unsupported metric.", confidence=0.5,
    )
    with pytest.raises(ValueError, match="exact quote"):
        validate_evidence_quotes([result], SUBMISSION)
