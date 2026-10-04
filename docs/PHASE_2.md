# Phase 2: Judge consistency and disagreement

## Purpose

Different scores can point reviewers to unclear rubric language, different interpretations of the project evidence, or different judgments. FairJudge identifies and quantifies those differences so a human can inspect them. **Disagreement is a signal for review, not proof that a judge is incorrect.** The system never determines which judge is right.

## Calculation

For each rubric criterion, Python calculates judge count, arithmetic mean, minimum, maximum, range, median, and `range / criterion maximum`. Thresholds are centralized in `backend/disagreement.py`: LOW is at or below 10%; MODERATE is above 10% and at or below 25%; HIGH is above 25%. Since rubric maximums differ, each range is normalized against its own supplied maximum. Python also calculates each judge's total and the observed total-score range.

Python owns these calculations so they are deterministic, reproducible, and independently testable. The model receives no authority to set or change scores, totals, or statistics.

## Qwen3:8b role and evidence controls

Qwen3:8b, served locally through Ollama, can offer a short explanation of possible differences based on the rubric, evidence, and reasoning provided by each judge. It cannot invent project facts, add criteria, make external comparisons, or decide which judge is correct. Each returned quote must exactly match evidence or reasoning from the attributed judge and criterion. Invalid, missing, or unsupported quotes cause a safe fallback: “Insufficient evidence to determine the reason for disagreement.” A human review is then required. Exact quote validation cannot fully prove that every unquoted implication in a model explanation is semantically supported; reviewers should inspect the source evidence.

The core workflow requires no paid proprietary LLM API. Judge and project details can remain within the local Ollama workflow; the model layer uses a replaceable client boundary.

## Review policy

MODERATE and HIGH disagreement automatically recommend human review. LOW disagreement does not, unless evidence is missing or an explanation failed validation. The recommendation is not an error designation or a finding about judge quality.

## Fictional example

The following data is a deterministic software demo only. The judges and their scores are fictional and are not Byte the Vibe judge results. The Phase 1.5 Operis AI evaluation remains a separate, single AI-assisted evaluation of **50/70** (Innovation 15/20, Technical 25/30, Impact 10/20), documented in `REAL_WORLD_VALIDATION.md`.

For the demo rubric (Innovation 20, Technical 30, Impact 20), fictional Judges A/B/C score:

| Criterion | Scores | Mean | Range | Range / max | Level |
|---|---:|---:|---:|---:|---|
| Innovation | 18, 12, 15 | 15.0000 | 6 | 30% | HIGH |
| Technical | 27, 25, 28 | 26.6667 | 3 | 10% | LOW |
| Impact | 16, 10, 14 | 13.3333 | 6 | 30% | HIGH |

Their totals are 61/70, 47/70, and 57/70, for an observed total range of 14. Human review is recommended for the HIGH disagreement criteria. The test fixture is `tests/fixtures/phase2_demo.json`.

## API

`POST /analyze-disagreement` accepts a project name, rubric, and two or more judge evaluations. Each judge provides a unique ID and a score, evidence list, and reasoning per rubric criterion; confidence is optional. Criteria must match the rubric exactly and scores must be integer values within the maximum. Invalid input returns FastAPI/Pydantic validation errors rather than being silently repaired. The response includes per-criterion judge details, statistics, explanation, review flag, judge totals, maximum possible total, observed maximum and minimum judge totals, and `validation_status` (`VALIDATED` or `SAFE_FALLBACK_USED`). `GET /health` and Phase 1 `POST /evaluate` remain available.

## Limitations

Thresholds are configurable starting points, not empirically calibrated universal standards. A small score range does not establish agreement about evidence quality or objective fairness. Evidence and reasoning are supplied by judges and are not independently verified. Explanation quote checks provide source attribution but cannot establish truth or guarantee semantic entailment. This system does not establish objective fairness or determine the objectively correct winner; humans retain responsibility for final decisions.
