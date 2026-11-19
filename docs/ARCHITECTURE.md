# Design note

## Architecture and stack

The demo uses Angular 19 for a responsive single-page UI, FastAPI for typed JSON endpoints and OpenAPI documentation, SQLAlchemy 2 for persistence, and SQLite for a zero-setup local database. Docker Compose packages the API and web frontend so the same launch procedure can be used on another machine. This stack provides a short path to a working, testable prototype while keeping browser, HTTP and data layers separate.

## Domain model

- `Customer` has many `Order` records (one-to-many).
- `Order` has many `OrderItem` records (one-to-many).
- Each `OrderItem` references one `Product`; products can appear in many order items (many-to-many between orders and products through `OrderItem`).
- `User` holds a seeded role. `Audit` records actor/action/entity/id/time for sensitive changes.

## Role matrix

| Capability | Admin | Sales | Viewer |
|---|---:|---:|---:|
| Read dashboard, customers, products, orders | Yes | Yes | Yes |
| Create/update customers and products | Yes | Yes | No |
| Delete customers/products | Yes | No | No |
| Create orders and change draft status | Yes | Yes | No |
| Delete draft order | Yes | Yes | No |
| Read audit history | Yes | No | No |

Authorization is enforced by API dependencies, not only by hiding buttons in Angular.

## Business rules

See `TRACEABILITY.md` for the explicit rules and evidence map. Core invariants include unique customer email/SKU, positive unit price and quantity, valid foreign keys, draft-only order item changes and deletion, stock deduction at validation (not draft creation), and ordered `draft -> validated -> closed` transitions.
