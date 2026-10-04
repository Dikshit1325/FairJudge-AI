import asyncio

import httpx

from backend import main
from backend.ollama_client import OllamaUnavailableError


async def request(method, path, **kwargs):
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, path, **kwargs)


def test_health_endpoint():
    response = asyncio.run(request("GET", "/health"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ollama_unavailable_maps_to_clear_503(monkeypatch):
    def unavailable(*_args, **_kwargs):
        raise OllamaUnavailableError("Ollama is unavailable. Start the local Ollama service.")

    monkeypatch.setattr(main, "evaluate_project", unavailable)
    response = asyncio.run(request("POST", "/evaluate", json={
        "rubric": [{"criterion": "Innovation", "max_score": 20}],
        "submission": {
            "project_name": "Example",
            "problem_statement": "A problem",
            "solution_description": "A solution",
            "technical_details": "Python",
        },
    }))
    assert response.status_code == 503
    assert "Start the local Ollama service" in response.json()["detail"]
