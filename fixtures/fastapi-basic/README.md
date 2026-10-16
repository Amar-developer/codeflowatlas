# fastapi-basic fixture

A small shop API used as a known input for the Python analyzer. The analyzer reads these files as data and never imports or runs them.

## Endpoints

- `POST /api/checkout`: reserve stock, charge the card, create the order, send a notification.
- `GET /api/orders/{order_id}`: read one order through an injected `OrderService`.

## Cases this fixture covers

| Case | Location | Expected result |
| --- | --- | --- |
| Router prefix + `include_router` prefix | `app/main.py`, `app/routers/checkout.py` | Path `/api/checkout` |
| Imported function call | `charge_card(...)` | CALLS, exact |
| Module attribute call | `inventory.reserve(...)` | CALLS, exact |
| Method on constructed instance | `OrderService(session).create(...)` | CALLS, high |
| `Depends`-injected service method | `service.get(...)` in `get_order` | CALLS, medium |
| ORM read | `select(Product)` in `inventory.reserve` | READS_FROM `products` |
| ORM write | `session.add(order)` in `OrderService.create` | WRITES_TO `orders` |
| Attribute mutation flushed on commit | `product.stock -= quantity` | Not detected; documented limitation |
| External HTTP | `httpx.post` in `payment.charge_card` | ExternalService, `PAYMENT_URL` |
| Dynamic dispatch | `globals()[...]` in `notifications.send` | Unresolved; must not be guessed |

## Known issues to surface (for the AI guide)

- `OutOfStockError` is not handled in `checkout`, so it returns HTTP 500.
- If payment succeeds but `OrderService.create` fails, the card is charged with no order.
- `notify_channel` is user input used to choose a function; an unknown value raises `KeyError` (HTTP 500).

`expected-graph.json` holds the machine-readable assertions: required endpoints, entities, and edges with confidence; edges that must stay unresolved; edges that must not be guessed; and known gaps. `tests/unit/test_fixture_expectations.py` checks that every `site` still matches the fixture source, so update both together.