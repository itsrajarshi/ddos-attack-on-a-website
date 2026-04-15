# ================= IMPORTS =================
from collections import defaultdict, deque  # Efficient data structures
from dataclasses import dataclass          # For structured alert objects
from time import time                      # For timestamps


# ================= ALERT DATA STRUCTURE =================
@dataclass
class Alert:
    ts: float     # Timestamp of the alert
    ip: str       # IP address of the requester
    reason: str   # Reason for alert (rate-limit, burst, etc.)
    route: str    # Requested route
    detail: str   # Additional description


# ================= SECURITY ENGINE =================
class SecurityEngine:
    def __init__(self):
        # 🔥 TUNED VALUES (thresholds and limits)

        self.rate_limit = 10          # Max requests allowed in window
        self.window_seconds = 5       # Time window (seconds)
        self.block_seconds = 30       # Block duration (seconds)
        self.strike_limit = 2         # Strikes before blocking
        self.ids_burst_threshold = 15 # Burst detection threshold

        # ================= INTERNAL STORAGE =================

        # Store request timestamps per IP and route
        self._requests = defaultdict(lambda: defaultdict(deque))

        # Total requests per IP (for attacker tracking)
        self._ip_total_requests = defaultdict(int)

        # Strike count per IP
        self._strikes = defaultdict(int)

        # Blocked IPs with expiry time
        self._blocked_until = {}

        # Recent alerts (max 200 stored)
        self._alerts = deque(maxlen=200)


    # ================= GET CURRENT TIME =================
    def _now(self):
        return time()


    # ================= CLEANUP OLD DATA =================
    def _cleanup(self, ip, route, now):
        # Get request queue for this IP and route
        q = self._requests[ip][route]

        # Remove requests older than the time window
        cutoff = now - self.window_seconds
        while q and q[0] < cutoff:
            q.popleft()

        # Remove expired blocks
        if ip in self._blocked_until and self._blocked_until[ip] <= now:
            del self._blocked_until[ip]
            self._strikes[ip] = 0  # Reset strikes after unblock


    # ================= MAIN INSPECTION LOGIC =================
    def inspect(self, ip, route):
        now = self._now()

        # Clean old data before processing
        self._cleanup(ip, route, now)

        # Allow localhost without restrictions
        if ip == "127.0.0.1":
            return True, "localhost bypass"

        # ================= HONEYPOT CHECK =================
        if route == "/admin-secret":
            # Immediately block IP if honeypot is triggered
            self._blocked_until[ip] = now + self.block_seconds

            # Log alert
            self._alerts.append(
                Alert(now, ip, "honeypot", route, "Trap triggered")
            )

            return False, "Honeypot triggered"

        # ================= BLOCK CHECK =================
        if ip in self._blocked_until:
            return False, "Blocked"

        # ================= REQUEST TRACKING =================
        q = self._requests[ip][route]

        # Add current request timestamp
        q.append(now)

        # Increment total request count for IP
        self._ip_total_requests[ip] += 1

        # Number of requests in current window
        count = len(q)

        # ================= BURST DETECTION =================
        if count > self.ids_burst_threshold:
            self._alerts.append(
                Alert(now, ip, "burst", route, "High traffic")
            )

        # ================= RATE LIMIT CHECK =================
        if count > self.rate_limit:
            # Increase strike count
            self._strikes[ip] += 1

            # Log rate limit alert
            self._alerts.append(
                Alert(now, ip, "rate-limit", route, "Exceeded")
            )

            # If strikes exceed limit → block IP
            if self._strikes[ip] >= self.strike_limit:
                self._blocked_until[ip] = now + self.block_seconds

                self._alerts.append(
                    Alert(now, ip, "blocked", route, "Blocked IP")
                )

                return False, "Blocked"

            return False, "Rate limit"

        # Request is allowed
        return True, "ok"


    # ================= GET BLOCKED IPS =================
    def blocked_ips(self):
        now = self._now()
        result = []

        # Iterate over blocked IPs
        for ip, until in list(self._blocked_until.items()):
            # Remove expired blocks
            if until <= now:
                del self._blocked_until[ip]
                continue

            # Add active blocked IP info
            result.append({
                "ip": ip,
                "blocked_for_seconds": int(until - now)
            })

        return result


    # ================= GET ALERTS =================
    def alerts(self):
        # Return alerts as dictionaries
        return [a.__dict__ for a in self._alerts]


    # ================= TOP ATTACKERS =================
    def top_attackers(self):
        # Sort IPs by total request count (descending)
        return sorted(
            [{"ip": ip, "count": c} for ip, c in self._ip_total_requests.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:5]  # Return top 5 attackers