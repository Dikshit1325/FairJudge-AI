# FairJudge AI dashboard

React + TypeScript + Vite frontend for the FairJudge FastAPI backend.

From this directory:

```bash
npm install
npm run dev
npm run build
```

The dev server runs at `http://localhost:5173` and proxies `/api` requests to `http://127.0.0.1:8000`. Set `FAIRJUDGE_API_URL` before running Vite to point at another local backend. Start FastAPI from the repository root with `uvicorn backend.main:app --reload`.

The Operis AI page is a static rendering of the documented Phase 1.5 validation snapshot (50/70). Judge Comparison sends the existing fictional Phase 2 fixture to the live disagreement endpoint; those scores are not actual hackathon judge scores. See the repository [README](../README.md) and [Phase 2 notes](../docs/PHASE_2.md).
