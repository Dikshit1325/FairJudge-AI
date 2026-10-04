"""FastAPI application for FairJudge AI Phase 1."""

from fastapi import FastAPI, HTTPException
from starlette.concurrency import run_in_threadpool

from .evaluator import MalformedEvaluationError, evaluate_project
from .disagreement import analyze_disagreement
from .models import DisagreementRequest, DisagreementResponse, EvaluationRequest, EvaluationResponse
from .ollama_client import OllamaResponseError, OllamaUnavailableError

app = FastAPI(
    title="FairJudge AI",
    description="Evidence-first evaluation support for human hackathon judges.",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest) -> EvaluationResponse:
    try:
        return await run_in_threadpool(evaluate_project, request.rubric, request.submission)
    except OllamaUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (MalformedEvaluationError, OllamaResponseError) as exc:
        raise HTTPException(status_code=502, detail=f"Evaluation could not be safely validated: {exc}") from exc


@app.post("/analyze-disagreement", response_model=DisagreementResponse)
async def analyze_judge_disagreement(request: DisagreementRequest) -> DisagreementResponse:
    return await run_in_threadpool(analyze_disagreement, request)
