# Execution record

Observed locally on 2026-11-19 using Docker Desktop. These are the outputs actually obtained, not a claim that every ISO check passed.

| Check | Result | Evidence |
|---|---|---|
| Docker image build | Pass: API and Angular web images built successfully. | `docker compose build` output showed both images Built. |
| Deployment smoke | Pass: both containers reported Up; `GET /api/health` returned HTTP 200 `{"status":"ok"}` and `HEAD /` on port 4200 returned HTTP 200. | Live curl/container output. |
| API/unit/integration | Pass: `4 passed` (roles, unique fields, stock, status rules, CRUD, linked order items and dashboard filter). | `docker run ... test-api python -m pytest -q`: 4 passed. Tests use a temporary database per process. |
| Postman API acceptance | Pass: 16 requests, 17 assertions, 0 failures. | Newman 6.2.1 ran `StockFlow.postman_collection.json` against the live API in 8.1 seconds. See command in README. |
| Coverage | Pass: 90% total statement coverage (API module 89%, tests 100%). | `coverage report -m`: app/main.py 332 statements, 38 missed, 89%; total 388 statements, 38 missed, 90%. |
| Static checks | Pass: Ruff returned `All checks passed!`. | `ruff check app tests`. |
| SAST | Pass: Bandit reported `No issues identified`, 532 lines scanned, 0 high/medium/low issues. | `bandit -r app`. |
| 20-user load | Mixed: 156 requests, 0 failures. Aggregate p95 1,100 ms. Dashboard p95 300 ms; product search p95 200 ms; token endpoint p95 1,300 ms. The aggregate does **not** meet the <500 ms target because bcrypt login dominates. | Locust headless, 20 users, spawn rate 5/s, duration 10 seconds. This is a short smoke load, not a sustained benchmark. |
| Browser E2E | Incomplete/failing: viewer authorization scenario passed on Chromium. Sales workflow progressed through customer/product/order creation, but the order list/status assertion did not pass. Firefox sales workflow also failed. Do not claim browser acceptance. | `frontend/e2e/stockflow.spec.ts`, Playwright 1.51. Browser fix/build still needs verification. |
| SCA (pip-audit) | Not run: `pip-audit` was missing in the running image; adding it triggered a Docker pip-install build that timed out. | No vulnerability scan result available. |
| DAST / manual usability / cross-browser review | Not run. | OWASP ZAP, keyboard/mobile review, and a successful Firefox workflow still need real execution. |

The only performance claim currently supported is the measured short-run result above. The API/search/dashboard met the local p95 target individually; the aggregate and login did not.
