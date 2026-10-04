# FairJudge AI

FairJudge AI is an evidence-based hackathon evaluation and transparency system. It connects scores to supplied evidence, surfaces missing information, and identifies differences between judges. **AI-assisted evaluation — human judges retain final authority.** It does not eliminate human bias, guarantee fairness, or determine an objectively correct winner.

The idea comes from a problem experienced by the author's friend, who frequently participates in hackathons: scoring can vary when judges interpret criteria differently or submissions do not provide comparable evidence.

## Evidence-first principle

The evaluator must use only the project submission and supplied rubric. Identity metadata is excluded from the model prompt and evidence source. GitHub and demo URLs are not fetched; their presence alone is not treated as evidence. The model is instructed to quote evidence verbatim; the backend checks every evidence quote against supplied project text and rejects the evaluation if a quote is not present. Unknown rubric criteria, mismatched maximum scores, malformed model output, and out-of-range scores are rejected. Missing information is stated as insufficient evidence and prompts human review. Python computes both total scores and maximum scores.

## Problem and solution

Judges may interpret a rubric differently or have uneven evidence available across submissions. FairJudge provides an evidence-first evaluation workflow and a deterministic multi-judge disagreement analysis so reviewers can focus on what needs discussion.

## Architecture

```text
User
 ↓
React Dashboard
 ↓
FastAPI
 ↓
Evaluation / Disagreement Engine
 ↓
Ollama
 ↓
Qwen3:8b

Deterministic Python scoring and evidence validation run alongside the model.
```

Ollama is accessed through its local HTTP API. The model cannot supply totals or disagreement statistics. The browser uses a Vite development proxy to call the FastAPI API; no cloud AI service is used.

## Technology

- Python 3.10+
- FastAPI and Pydantic v2
- Ollama with `qwen3:8b`
- pytest for automated tests
- React, TypeScript, Vite, Tailwind CSS, and React Router

## Project phases

- **Phase 1:** Evidence-based AI project evaluation, evidence quote validation, deterministic Python scoring, missing-evidence handling, and a human review flag.
- **Phase 1.5:** Real-world validation of Operis AI from Byte the Vibe. The documented local evaluation is **50/70**: Innovation 15/20, Technical 25/30, Impact 10/20. Details and limitations are in [docs/REAL_WORLD_VALIDATION.md](docs/REAL_WORLD_VALIDATION.md).
- **Phase 2:** Multi-judge score comparison and disagreement detection. Python computes statistics and totals; local Qwen may explain differences with evidence-attributed quotes. See [docs/PHASE_2.md](docs/PHASE_2.md). The three-judge sample there is fictional and is not actual Byte the Vibe judge data.
- **Phase 3:** Responsive React dashboard with an evaluation page, judge comparison, and clearly labeled validation/demo workflows.

## Screenshots

_Placeholder: add dashboard, evaluation, and judge comparison screenshots after capture._

## Local setup

1. Install [Ollama](https://ollama.com/download) and start its local service.
2. Pull the model:

   ```bash
   ollama pull qwen3:8b
   ollama list
   ```

3. From this project directory, create and activate a virtual environment, then install dependencies:

   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # macOS/Linux: source .venv/bin/activate
   python -m pip install -r backend/requirements.txt
   ```

4. `.env.example` documents the available settings: `OLLAMA_BASE_URL=http://localhost:11434`, `OLLAMA_MODEL=qwen3:8b`, and a 180 second generation timeout. Set these in your shell before starting the server. The application does not load `.env` files automatically.
5. Start the backend on `http://127.0.0.1:8000`:

   ```bash
   uvicorn backend.main:app --reload
   ```

6. In a second terminal, install and start the dashboard on `http://localhost:5173`:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   The Vite proxy forwards `/api/*` requests to `http://127.0.0.1:8000`. To use another backend URL during development, set `FAIRJUDGE_API_URL` before launching Vite.

## API

### Health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

This is an API liveness check; it does not check Ollama connectivity.

### Evaluate

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "rubric": [
      {"criterion": "Innovation", "max_score": 20},
      {"criterion": "Technical Implementation", "max_score": 25}
    ],
    "submission": {
      "project_name": "Example Project",
      "problem_statement": "Teams lack a clear way to plan tasks.",
      "solution_description": "A planning tool for teams.",
      "technical_details": "FastAPI backend.",
      "github_url": null,
      "demo_url": null,
      "presentation_text": "The project was presented to judges."
    }
  }'
```

The output has this shape; actual scores and evidence depend on the submission and model response:

```json
{
  "project_name": "Example Project",
  "total_score": 27,
  "max_score": 45,
  "criteria": [
    {
      "criterion": "Innovation",
      "score": 12,
      "max_score": 20,
      "evidence": ["A planning tool for teams."],
      "missing_evidence": ["Insufficient evidence: no comparison with existing approaches was supplied."],
      "reasoning": "The submission describes a planning tool, but provides limited detail for assessing novelty.",
      "confidence": 0.55
    },
    {
      "criterion": "Technical Implementation",
      "score": 15,
      "max_score": 25,
      "evidence": ["FastAPI backend."],
      "missing_evidence": ["Insufficient evidence: implementation details and test results were not supplied."],
      "reasoning": "A FastAPI backend is identified, while implementation depth is not described.",
      "confidence": 0.62
    }
  ],
  "overall_missing_evidence": [
    "Innovation: Insufficient evidence: no comparison with existing approaches was supplied.",
    "Technical Implementation: Insufficient evidence: implementation details and test results were not supplied."
  ],
  "human_review_required": true
}
```

The example response is illustrative, not a deterministic expected result. A request with an unavailable Ollama service returns HTTP 503 with a clear startup/model message. Invalid or unsupported generated content returns HTTP 502 rather than a successful evaluation.

### Analyze judge disagreement (Phase 2)

`POST /analyze-disagreement` compares two or more judge evaluations against a shared rubric. Python computes each criterion's mean, range, normalized disagreement level, and each judge's total. Local Qwen3:8b may explain differences using supplied judge evidence and reasoning; unsupported quotes trigger a safe fallback. The endpoint recommends human review for moderate or high disagreement and never determines which judge is correct. See [docs/PHASE_2.md](docs/PHASE_2.md) for thresholds, the fictional demo, and limitations.

## Dashboard demo workflow

1. Open `http://localhost:5173` while FastAPI is running.
2. On **Evaluation**, choose **Load Operis AI Demo** to view the historical Phase 1.5 validation snapshot (50/70), or enter a submission to call `POST /evaluate`.
3. On **Judge Comparison**, use **Load Judge Disagreement Demo** to send the shared fictional fixture to `POST /analyze-disagreement`. Its scores are fictional—not actual hackathon judge scores. Expand a criterion to inspect each judge’s evidence and reasoning.
4. Human judges review flagged items and make the final decision.

## Tests

Run the unit suite with:

```bash
python -m pytest
```

Tests mock the Ollama boundary for fast, repeatable validation; the application uses the real local Ollama service.

Build the frontend from `frontend/` with:

```bash
npm run build
```

## Current limitations

- LLM judgments can vary and are not calibrated against human-scored submissions. Judges must inspect the evidence and rationale.
- Exact-quote checks prevent invented evidence excerpts, but do not prove the model's reasoning or score is fair or correct.
- The health endpoint checks only that FastAPI is serving requests.
- There is no persistence, ranking, authentication, or deployment.
- Evaluation latency depends on local hardware and model availability.
- Demo snapshots are static validation examples; only submitted evaluation and judge comparison requests call the backend.
- A disagreement signal is not proof that a judge is wrong. Human review and final decisions remain necessary.
