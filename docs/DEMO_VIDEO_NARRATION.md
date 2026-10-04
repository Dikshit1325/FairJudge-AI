# FairJudge AI demo video narration

## Voiceover script

Welcome to FairJudge AI, an evidence-based assistant for hackathon evaluation.

The idea began with a friend who regularly joins hackathons. Judging can feel inconsistent when reviewers interpret a rubric differently or when project evidence is incomplete. FairJudge makes those differences easier to see and discuss. It supports judges; it does not choose a winner or claim that a score is objectively correct.

The workflow starts with one shared rubric. A judge supplies the project description and technical details. FairJudge evaluates each criterion and shows the score alongside its supporting evidence and reasoning. It also identifies missing information, helping a human reviewer see what the submission demonstrates and what still needs checking.

Qwen three, eight billion parameters, runs locally through Ollama. The model works from supplied project material. The backend validates evidence quotes, and Python calculates score totals. Project links are not treated as evidence unless their contents are inspected. Missing evidence or an unsupported quote leads to human review.

The Operis AI screen shows the documented Phase One point five validation from Byte the Vibe: fifteen out of twenty for Innovation, twenty-five out of thirty for Technical, and ten out of twenty for Impact, totaling fifty out of seventy. This is one AI-assisted evaluation, not a judge consensus or event prediction. Model performance, independently verified implementation, and real-world outcomes were not established.

Phase Two compares judges using that same rubric. Python calculates criterion averages, score ranges, disagreement percentages relative to each maximum, and judge totals. Low, moderate, and high labels help reviewers focus. The model may explain a difference using the judges’ supplied evidence and reasoning; unsupported quotes trigger a safe fallback. Judges’ scores, evidence, and reasoning remain available side by side.

The comparison shown here is fictional demonstration data, not Byte the Vibe judge results. Innovation and Impact show high disagreement; Technical shows low disagreement. These are review signals, not verdicts about judge quality.

FairJudge combines a React dashboard, FastAPI, local Ollama, and deterministic Python validation and scoring. No paid cloud AI service is required for the core workflow. Humans check the evidence, discuss the rubric, and make the final decision. Disagreement is a signal for review, not proof that a judge is incorrect. FairJudge aims to make evaluation more transparent, evidence-based, and easier to review.
