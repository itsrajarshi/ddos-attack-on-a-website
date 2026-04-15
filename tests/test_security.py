# ================= FUTURE IMPORT =================
# Enables postponed evaluation of type annotations (Python 3.7+ compatibility)
from __future__ import annotations


# ================= IMPORTS =================
from app.security import SecurityEngine  # Import the security engine to test


# ================= TEST: RATE LIMIT AND BLOCK =================
def test_rate_limit_then_block():
    # Initialize SecurityEngine with custom test parameters
    s = SecurityEngine(
        rate_limit_per_window=3,   # Allow only 3 requests per window
        window_seconds=10,         # Time window of 10 seconds
        block_seconds=60,          # Block duration of 60 seconds
        strike_limit=2,            # Block after 2 violations
        ids_burst_threshold=10,    # Burst threshold (not relevant here)
    )

    ip = "10.1.1.1"  # Test IP address

    # First 3 requests should be allowed
    for _ in range(3):
        ok, _ = s.inspect(ip, "/products")
        assert ok  # Expect request to pass

    # 4th request should exceed rate limit
    ok, msg = s.inspect(ip, "/products")
    assert not ok                     # Request should be blocked
    assert "Rate limit" in msg        # Message should indicate rate limit

    # Next request should trigger full block
    ok, msg = s.inspect(ip, "/products")
    assert not ok                     # Request should still be blocked
    assert "blocked" in msg.lower()   # Message should indicate blocking

    # Verify IP is listed in blocked IPs
    blocked = s.blocked_ips()
    assert len(blocked) == 1          # Only one blocked IP expected
    assert blocked[0]["ip"] == ip     # IP should match test IP


# ================= TEST: ALERT GENERATION =================
def test_alert_generation():
    # Initialize SecurityEngine with high rate limit to avoid blocking
    s = SecurityEngine(
        rate_limit_per_window=100,  # High limit so no rate limiting occurs
        window_seconds=10,
        block_seconds=60,
        strike_limit=3,
        ids_burst_threshold=5,      # Low threshold to trigger burst alert
    )

    ip = "10.2.2.2"  # Test IP address

    # Send multiple requests to trigger burst detection
    for _ in range(6):
        ok, _ = s.inspect(ip, "/checkout")
        assert ok  # Requests should still be allowed

    # Retrieve generated alerts
    alerts = s.alerts()

    # Check if at least one burst alert was generated
    assert any(
        a["reason"] == "ids-burst-detected" for a in alerts
    )