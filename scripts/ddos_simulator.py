import requests
import threading
import random
import time

URL = "http://127.0.0.1:5000/products"

# LIMITED attacker pool (realistic)
ATTACKER_IPS = [
    "101.1.1.1",
    "102.2.2.2",
    "103.3.3.3",
    "104.4.4.4",
    "105.5.5.5"
]

def attack():
    while True:
        try:
            ip = random.choice(ATTACKER_IPS)

            headers = {
                "X-Forwarded-For": ip
            }

            requests.get(URL, headers=headers)

            # Small delay → visible graph
            time.sleep(0.02)

        except:
            pass

# Controlled threads
for _ in range(20):
    threading.Thread(target=attack).start()