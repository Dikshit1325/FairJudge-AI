import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend import disagreement
from backend.main import app


def test_health_and_fictional_disagreement_api(monkeypatch):
    fixture = json.loads((Path(__file__).parent / "fixtures" / "phase2_demo.json").read_text(encoding="utf-8"))
    rows = []
    for criterion in fixture["rubric"]:
        judge = fixture["judge_evaluations"][0]
        rows.append({"criterion": criterion["criterion"], "explanation": "The supplied reasoning emphasizes different aspects.",
                     "supporting_quotes": [{"judge_id": judge["judge_id"], "quote": judge["evidence"][criterion["criterion"]][0]}]})
    monkeypatch.setattr(disagreement, "generate_structured", lambda *_: json.dumps({"criteria": rows}))
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    response = client.post("/analyze-disagreement", json=fixture)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["validation_status"] == "VALIDATED"
    assert body["criteria"][0]["disagreement_level"] == "HIGH"
    assert body["judge_totals"][0]["total_score"] == 61


def test_api_rejects_missing_criterion():
    fixture = json.loads((Path(__file__).parent / "fixtures" / "phase2_demo.json").read_text(encoding="utf-8"))
    del fixture["judge_evaluations"][0]["scores"]["Impact"]
    response = TestClient(app).post("/analyze-disagreement", json=fixture)
    assert response.status_code == 422
