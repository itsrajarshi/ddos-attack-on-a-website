# ================= IMPORTS =================
import requests    # For sending HTTP requests
import threading   # For running multiple attack threads
import random      # For random IP selection
import time        # For delay between requests


# ================= TARGET URL =================
# Endpoint to simulate attack on
URL = "http://127.0.0.1:5000/products"


# ================= ATTACKER IP POOL =================
# Limited set of IPs to simulate realistic attackers
ATTACKER_IPS = [
    "101.1.1.1",
    "102.2.2.2",
    "103.3.3.3",
    "104.4.4.4",
    "105.5.5.5"
]


# ================= ATTACK FUNCTION =================
def attack():
    while True:
        try:
            # Randomly pick an attacker IP
            ip = random.choice(ATTACKER_IPS)

            # Set fake IP in headers (for simulation)
            headers = {
                "X-Forwarded-For": ip
            }

            # Send GET request to target URL
            requests.get(URL, headers=headers)

            # Small delay to make traffic visible in graphs
            time.sleep(0.02)

        except:
            # Ignore all exceptions to keep attack running continuously
            pass


# ================= THREAD CREATION =================
# Create multiple threads to simulate concurrent attackers
for _ in range(20):
    threading.Thread(target=attack).start()