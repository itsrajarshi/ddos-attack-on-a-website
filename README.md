# DDoS Attack Case Study (Flask Website)

This project demonstrates:
- A realistic multi-route Flask e-commerce style site.
- A DDoS simulation script that floods one endpoint.
- A defense layer with rate limiting, temporary IP blocking, and IDS-like alerts.
- Firewall-like behavior by denying abusive clients (`429` + blocklist period).

## Project Structure

- `app/app.py`: Flask application and route handlers.
- `app/security.py`: Security engine (rate limit + strike/block + alerts).
- `scripts/ddos_simulator.py`: High-concurrency attack simulation.
- `scripts/normal_traffic.py`: Baseline normal-user traffic simulation.
- `tests/test_security.py`: Unit tests for defense behavior.

## Setup

```bash
python -m pip install -r requirements.txt
```

## Run Website

```bash
python app/app.py
```

Server starts at `http://127.0.0.1:5000`.

Main routes:
- `/`
- `/login`
- `/products`
- `/cart/add` (POST JSON: `{"product_id": 1}`)
- `/checkout`

Monitoring routes:
- `/admin/blocked` (shows currently blocked IPs)
- `/admin/alerts` (IDS-style alert stream)

## Baseline Demo (Normal Traffic)

In another terminal:

```bash
python scripts/normal_traffic.py --base-url http://127.0.0.1:5000 --duration 20 --interval 0.6
```

Expected: very low or zero blocked requests.

## DDoS Simulation Demo

In another terminal:

```bash
python scripts/ddos_simulator.py --base-url http://127.0.0.1:5000 --path /products --workers 80 --duration 20 --delay 0.01
```

Expected:
- Many `429` responses after threshold crossing.
- IP eventually appears in `/admin/blocked`.
- Alerts in `/admin/alerts` with reasons:
  - `ids-burst-detected`
  - `rate-limit-exceeded`
  - `ip-blocked`

## Case Study Narrative (Use in Report)

1. Show normal behavior under regular traffic (service mostly available).
2. Trigger attack and observe request spikes.
3. Observe rate limiting activating first (balanced defense).
4. Observe repeated abuse causing temporary firewall block (60s).
5. Show IDS-like alerts proving suspicious pattern detection.
6. Conclude how layered controls preserve service and visibility.

## Run Tests

```bash
pytest -q
```

These tests validate:
- Rate limit then block flow.
- IDS-style burst detection alerts.
