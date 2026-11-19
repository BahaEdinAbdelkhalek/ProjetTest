# ISO/IEC 25010 traceability and live demo checklist

**Evidence status:** actual results recorded in `EXECUTION_RESULTS.md`. Do not present any target or procedure there as a passing result unless that record says it passed.

| Characteristic | Concrete claim/acceptance | Verification and evidence |
|---|---|---|
| Functional suitability | CRUD customer/product, order creation, role checks, stock validation, legal order transitions, dashboard and audit work | 4 API tests passed; see `EXECUTION_RESULTS.md`. Postman collection is provided; execution through Newman/Postman remains pending. |
| Performance efficiency | API p95 under 500 ms at 20 concurrent users | Short 10-second Locust run: aggregate p95 1,100 ms (fails target); dashboard 300 ms, search 200 ms, login 1,300 ms. See `EXECUTION_RESULTS.md`. |
| Compatibility | UI/API run in Chrome and Firefox; REST contract is framework-neutral | Chromium viewer check passed; sales E2E and Firefox incomplete/failing. See `EXECUTION_RESULTS.md`. |
| Usability | Keyboard-accessible labels, responsive layout, visible feedback, basic validation | Not manually verified. See `EXECUTION_RESULTS.md`. |
| Reliability | Failed order creation does not consume stock; invalid transitions rejected; SQLite data persists via Docker volume | API tests verified stock rejection, valid deduction and status rejection. Container restart persistence not separately verified. |
| Security | JWT authentication, role checks, SQLAlchemy parameterization, bounded search, no audit access for non-admin | Bandit passed with no findings. pip-audit and OWASP ZAP not run. See `EXECUTION_RESULTS.md`. |
| Maintainability | Layered models/routes, static checks and measured test coverage | Ruff passed; total measured coverage 90%. See `EXECUTION_RESULTS.md`. |
| Portability | Repeatable Docker Compose build with persistent data volume | Images built, both services started, API health and frontend returned HTTP 200. Clean-machine installation not tested. |

## Functional rules

1. Customer email is unique (database constraint).
2. Product SKU is unique (database constraint).
3. Price and order-item quantity must be positive; stock cannot be negative.
4. An order needs an existing customer and existing products.
5. Requested quantity cannot exceed available stock. Stock is decremented only when an order is validated.
6. Status transitions are only `draft -> validated -> closed`.
7. A customer with orders and a product referenced by an order cannot be deleted.
8. Audit events record actor, action, entity, id and timestamp; audit listing is admin-only.

## Fast presentation path

Sign in as viewer, show read-only access and blocked create action; sign in as sales, add a product and customer; use `/docs` to create an order, show rejected over-stock request and validate a valid order; sign in as admin to show audit. Then run at least the unit/API tests live. Show actual command output, not this checklist, as evidence.

## Test-layer mapping

Unit/API integration: pytest + FastAPI TestClient, 4 tests passed. API contract: OpenAPI at `/docs`; Newman executed the Postman collection, 16 requests and 17 assertions passed. E2E: Playwright suite exists; viewer test passed on Chromium, but sales workflow assertions failed and Firefox was not validated. Performance: actual 20-user short-run Locust result is recorded, with aggregate target miss. SAST: Bandit passed. SCA: pip-audit unavailable. DAST: ZAP not run. Browser compatibility and usability are not yet fully verified. Portability: Docker Compose build/run smoke passed; clean-machine install not tested.
