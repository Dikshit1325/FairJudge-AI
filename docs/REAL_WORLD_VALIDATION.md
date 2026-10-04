# Real-World Validation — Operis AI

Hackathon: **Byte the Vibe**  
Project: **Operis AI**

## Rubric

- Innovation — 20
- Technical — 30
- Impact — 20

No other criteria were used. Python calculated the total from the three individual scores.

## Evaluation

**Total: 50 / 70**

This is the first successfully validated local Qwen3:8b evaluation, checked against the supplied rubric and project text. Python calculated the total as 15 + 25 + 10 = 50. It is not an objectively correct score or a prediction of the hackathon result. A later prompt-reinforced repeat did not produce a valid evaluation: one request timed out and another was rejected because an evidence quote did not match the submission text. Repository and demo contents were not inspected. This variation is a reason for human review.

### Innovation

**Score: 15 / 20**

**Evidence:**

- “A real-time intelligent system that tracks user activity, predicts burnout risk using Machine Learning, and visualizes insights through a live dashboard.”
- “Chrome Extension for user activity tracking”
- “FastAPI Backend for processing and APIs”
- “React Dashboard for real-time visualization”
- “Tracks user activity”; “Tracks time spent”; “Tracks tasks”; “Tracks meetings”; “Detects current working context/websites”

**Missing evidence:**

- **Insufficient evidence** to establish how Operis AI is unique compared with existing solutions. The submission describes its combination of tracking, burnout prediction, and dashboard features, but supplies no comparison with other approaches.

**Reasoning:** The submission describes a specific combination of browser activity tracking, burnout prediction, productivity monitoring, and live visualization. That supports an innovation assessment of the described concept, while its novelty relative to existing solutions remains unestablished. The score reflects the model’s judgment of the supplied description only.

### Technical

**Score: 25 / 30**

**Evidence:**

- “React”; “Vite”; “Tailwind CSS”; “Recharts”
- “FastAPI”; “Python”; “Joblib”
- “Chrome Extension API”; “Manifest V3”
- “Model: Logistic Regression” and “Training: Synthetic dataset”
- “Features: hours_worked, meetings_count, sentiment, tasks_completed”
- “POST /predict - Predict burnout” and “GET /live - Get real-time dashboard data”
- “Deployment: Frontend: Netlify, Backend: Render”
- The submission says these challenges were solved: “CORS issues between frontend, backend and extension”; “Preflight OPTIONS request handling”; “Real-time data syncing”; “Deployment mismatches”

**Missing evidence:**

- **Insufficient evidence** about ML performance. No accuracy, precision, recall, F1 score, test results, or validation dataset results were supplied.
- **Insufficient evidence** to independently verify the described code, endpoints, extension behavior, or deployments. The GitHub repository was not inspected; **GitHub evidence unavailable**.
- The listed technical challenges are described as solved, but implementation details or verification results for those fixes were not supplied.
- No production-readiness claim is made.

**Reasoning:** The submission provides a broad stack, architecture, model type, training-data description, input features, endpoints, and deployment description. It also lists cross-origin, preflight, data-sync, and deployment issues as solved. The missing code inspection and performance/test results limit what can be verified from those descriptions. The score reflects the model’s judgment of the submitted technical detail, not independently verified operation.

### Impact

**Score: 10 / 20**

**Evidence:**

- “The system helps organizations monitor productivity and detect burnout risks early.”
- “Real-time productivity trends”
- “Alerts for high-risk users”
- The submission says the dashboard shows “burnout distribution charts”.

**Missing evidence:**

- **Insufficient evidence** of actual users or organizational use.
- **Insufficient evidence** of measured productivity improvement or reduced burnout.
- **Insufficient evidence** of burnout-detection performance in real or held-out data.
- No user feedback or quantitative outcomes were supplied.
- The frontend and backend hosting providers are named, but no evidence of adoption or organizational deployment was supplied.

**Reasoning:** The submission states intended organizational benefits and describes charts and high-risk alerts. It does not report real-world usage or measured outcomes, so the stated intended impact cannot be treated as demonstrated impact. The score reflects the stated potential in the description only.

## Future Improvements

The submission labels Firebase integration for user storage and multi-user tracking as future improvements. They were not treated as implemented features or used to support any score.

## GitHub / Demo

The supplied GitHub URL was not inspected because this backend has no repository retrieval mechanism. **GitHub evidence unavailable.** No demo URL was supplied, so no demo evidence was available.

## Human Review

**Required: Yes.** Human judges should review the innovation score because comparative novelty is not established; the technical score because code and ML performance were not verified; and the impact score because no real-user validation or outcome measurements were supplied. The final judging decision remains with the human judges.

## Potentially Disputed Criteria

- **Innovation:** The project’s combination of features is described, but comparative uniqueness is not established.
- **Technical:** The score relies on the submitted implementation description; no code inspection or ML performance results were available.
- **Impact:** The evidence describes intended benefits rather than demonstrated outcomes.

## Participant Feedback

