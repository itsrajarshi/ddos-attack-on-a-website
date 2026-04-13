from __future__ import annotations

from app.security import SecurityEngine


def test_rate_limit_then_block():
    s = SecurityEngine(
        rate_limit_per_window=3,
        window_seconds=10,
        block_seconds=60,
        strike_limit=2,
        ids_burst_threshold=10,
    )
    ip = "10.1.1.1"

    for _ in range(3):
        ok, _ = s.inspect(ip, "/products")
        assert ok

    ok, msg = s.inspect(ip, "/products")
    assert not ok
    assert "Rate limit" in msg

    ok, msg = s.inspect(ip, "/products")
    assert not ok
    assert "blocked" in msg.lower()

    blocked = s.blocked_ips()
    assert len(blocked) == 1
    assert blocked[0]["ip"] == ip


def test_alert_generation():
    s = SecurityEngine(
        rate_limit_per_window=100,
        window_seconds=10,
        block_seconds=60,
        strike_limit=3,
        ids_burst_threshold=5,
    )
    ip = "10.2.2.2"
    for _ in range(6):
        ok, _ = s.inspect(ip, "/checkout")
        assert ok
    alerts = s.alerts()
    assert any(a["reason"] == "ids-burst-detected" for a in alerts)
