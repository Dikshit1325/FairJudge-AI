import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend import disagreement
from backend.disagreement import analyze_disagreement, disagreement_level
from backend.models import DisagreementRequest

FIXTURE = Path(__file__).parent / "fixtures" / "phase2_demo.json"


def demo():
    return DisagreementRequest.model_validate_json(FIXTURE.read_text(encoding="utf-8"))


def valid_explanation(request):
    rows = []
    for criterion in request.rubric:
        judge = request.judge_evaluations[0]
        key = next(key for key in judge.evidence if key.casefold() == criterion.criterion.casefold())
        rows.append({"criterion": criterion.criterion, "explanation": "The judges emphasize different supplied aspects.",
                     "supporting_quotes": [{"judge_id": judge.judge_id, "quote": judge.evidence[key][0]}]})
    return json.dumps({"criteria": rows})


@pytest.mark.parametrize("span,maximum,expected", [
    (0, 20, "LOW"), (2, 20, "LOW"), (3, 20, "MODERATE"),
    (5, 20, "MODERATE"), (6, 20, "HIGH"),
])
def test_thresholds(span, maximum, expected):
    assert disagreement_level(span, maximum)[1] == expected


def test_percent_and_stats_for_fictional_innovation(monkeypatch):
    request = demo()
    monkeypatch.setattr(disagreement, "generate_structured", lambda *_: valid_explanation(request))
    result = analyze_disagreement(request)
    innovation = result.criteria[0]
    assert (innovation.average_score, innovation.minimum_score, innovation.maximum_score, innovation.score_range) == (15, 12, 18, 6)
    assert innovation.disagreement_percentage == 0.3
    assert innovation.disagreement_level == "HIGH" and innovation.human_review_required
    assert result.validation_status == "VALIDATED"
    assert [j.total_score for j in result.judge_totals] == [61, 47, 57]
    assert (result.maximum_possible_total_score, result.minimum_total_score, result.maximum_total_score, result.total_score_range) == (70, 47, 61, 14)
    assert result.criteria[1].disagreement_level == "LOW"
    assert result.criteria[2].disagreement_level == "HIGH"


def test_identical_scores_low(monkeypatch):
    request = demo()
    for judge in request.judge_evaluations:
        judge.scores["Innovation"] = 10
    monkeypatch.setattr(disagreement, "generate_structured", lambda *_: valid_explanation(request))
    assert analyze_disagreement(request).criteria[0].disagreement_level == "LOW"


@pytest.mark.parametrize("mutate", [
    lambda d: d["judge_evaluations"][0]["scores"].update(Innovation=21),
    lambda d: d["judge_evaluations"][0]["scores"].update(Innovation=-1),
    lambda d: d["judge_evaluations"][0]["scores"].update(Innovation="18"),
    lambda d: d["judge_evaluations"][0]["scores"].pop("Impact"),
    lambda d: d["judge_evaluations"][1].update(judge_id="judge-a"),
    lambda d: d["judge_evaluations"][0].update(judge_id=""),
    lambda d: d["judge_evaluations"][0]["scores"].update(Unknown=1),
    lambda d: d["judge_evaluations"][0].pop("judge_id"),
    lambda d: d["judge_evaluations"][0]["evidence"].update(Unknown=[]),
])
def test_invalid_judge_data_rejected(mutate):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    mutate(data)
    with pytest.raises(ValidationError):
        DisagreementRequest.model_validate(data)


def test_unsupported_quote_falls_back(monkeypatch):
    request = demo()
    def unsupported(*_):
        return json.dumps({"criteria": [{"criterion": c.criterion, "explanation": "The project has millions of users.",
            "supporting_quotes": [{"judge_id": "judge-a", "quote": "Millions of users"}]} for c in request.rubric]})
    monkeypatch.setattr(disagreement, "generate_structured", unsupported)
    result = analyze_disagreement(request)
    assert result.validation_status == "SAFE_FALLBACK_USED"
    assert result.criteria[0].explanation == disagreement.SAFE_EXPLANATION
    assert result.human_review_required


def test_no_evidence_quote_falls_back(monkeypatch):
    request = demo()
    monkeypatch.setattr(disagreement, "generate_structured", lambda *_: json.dumps({"criteria": [
        {"criterion": c.criterion, "explanation": disagreement.SAFE_EXPLANATION, "supporting_quotes": []} for c in request.rubric]}))
    assert analyze_disagreement(request).validation_status == "SAFE_FALLBACK_USED"
