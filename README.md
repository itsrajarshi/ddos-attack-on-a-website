# DDoS Attack Case Study (Flask Web Application)

This repository demonstrates how a Flask-based web application behaves under normal traffic and during a simulated DDoS attack, then shows how layered defenses reduce abuse impact.

## Demo

<p align="center">
  <video src="assets/demo.mp4" controls width="900"></video>
</p>

If the embedded player is not supported in your browser, open the video directly: [Watch demo](assets/demo.mp4).

## Key Highlights

- Multi-route Flask e-commerce style application.
- DDoS traffic simulator targeting configurable endpoints.
- Layered defense strategy:
  - Rate limiting
  - Temporary IP blocking
  - IDS-style alert generation
- Monitoring endpoints for blocked clients and security alerts.

## Project Structure

| Path | Description |
| --- | --- |
| `app/app.py` | Flask app and route handlers |
| `app/security.py` | Security logic for rate limiting, strikes, temporary blocks, and alerts |
| `scripts/normal_traffic.py` | Simulates baseline user behavior |
| `scripts/ddos_simulator.py` | Simulates high-concurrency abusive traffic |
| `tests/test_security.py` | Unit tests for defense behavior |

## Getting Started

### 1. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app/app.py
```

Application URL: `http://127.0.0.1:5000`

## Application Routes

**Core routes**
- `/`
- `/login`
- `/products`
- `/cart/add` (POST JSON: `{"product_id": 1}`)
- `/checkout`

**Security/monitoring routes**
- `/admin/blocked` - list of currently blocked IPs
- `/admin/alerts` - IDS-style alert stream

## Traffic Simulation

### Baseline (Normal) Traffic

Run in a separate terminal:

```bash
python scripts/normal_traffic.py --base-url http://127.0.0.1:5000 --duration 20 --interval 0.6
```

Expected result: little to no blocked requests.

### DDoS Simulation

Run in a separate terminal:

```bash
python scripts/ddos_simulator.py --base-url http://127.0.0.1:5000 --path /products --workers 80 --duration 20 --delay 0.01
```

Expected results:
- Increased `429 Too Many Requests` responses once thresholds are crossed
- Offending IPs appear in `/admin/blocked`
- Alerts in `/admin/alerts` such as:
  - `ids-burst-detected`
  - `rate-limit-exceeded`
  - `ip-blocked`

## Test Suite

```bash
pytest -q
```

The tests cover the rate-limit-to-block flow and IDS-style burst detection behavior.
