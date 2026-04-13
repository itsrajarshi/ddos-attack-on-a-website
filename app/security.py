from collections import defaultdict, deque
from dataclasses import dataclass
from time import time

@dataclass
class Alert:
    ts: float
    ip: str
    reason: str
    route: str
    detail: str

class SecurityEngine:
    def __init__(self):
        # 🔥 TUNED VALUES
        self.rate_limit = 10
        self.window_seconds = 5
        self.block_seconds = 30
        self.strike_limit = 2
        self.ids_burst_threshold = 15

        self._requests = defaultdict(lambda: defaultdict(deque))
        self._ip_total_requests = defaultdict(int)
        self._strikes = defaultdict(int)
        self._blocked_until = {}
        self._alerts = deque(maxlen=200)

    def _now(self):
        return time()

    def _cleanup(self, ip, route, now):
        q = self._requests[ip][route]
        cutoff = now - self.window_seconds

        while q and q[0] < cutoff:
            q.popleft()

        if ip in self._blocked_until and self._blocked_until[ip] <= now:
            del self._blocked_until[ip]
            self._strikes[ip] = 0

    def inspect(self, ip, route):
        now = self._now()
        self._cleanup(ip, route, now)

        # Localhost safe
        if ip == "127.0.0.1":
            return True, "localhost bypass"

        # Honeypot
        if route == "/admin-secret":
            self._blocked_until[ip] = now + self.block_seconds
            self._alerts.append(Alert(now, ip, "honeypot", route, "Trap triggered"))
            return False, "Honeypot triggered"

        if ip in self._blocked_until:
            return False, "Blocked"

        q = self._requests[ip][route]
        q.append(now)
        self._ip_total_requests[ip] += 1

        count = len(q)

        if count > self.ids_burst_threshold:
            self._alerts.append(Alert(now, ip, "burst", route, "High traffic"))

        if count > self.rate_limit:
            self._strikes[ip] += 1
            self._alerts.append(Alert(now, ip, "rate-limit", route, "Exceeded"))

            if self._strikes[ip] >= self.strike_limit:
                self._blocked_until[ip] = now + self.block_seconds
                self._alerts.append(Alert(now, ip, "blocked", route, "Blocked IP"))
                return False, "Blocked"

            return False, "Rate limit"

        return True, "ok"

    def blocked_ips(self):
        now = self._now()
        result = []

        for ip, until in list(self._blocked_until.items()):
            if until <= now:
                del self._blocked_until[ip]
                continue

            result.append({
                "ip": ip,
                "blocked_for_seconds": int(until - now)
            })

        return result

    def alerts(self):
        return [a.__dict__ for a in self._alerts]

    def top_attackers(self):
        return sorted(
            [{"ip": ip, "count": c} for ip, c in self._ip_total_requests.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:5]